// Clang LibTooling/Rewriter overlay used by the executable migration agent.
//
// The Python orchestrator deliberately does not edit C source by line number.
// This tool resolves the selected function by USR, renames its definition,
// rewrites every direct call in every supplied translation unit, and fails
// closed for macro or indirect references.

#include "clang/AST/ASTContext.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/Basic/Diagnostic.h"
#include "clang/Basic/SourceManager.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Index/USRGeneration.h"
#include "clang/Lex/Lexer.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "clang/Tooling/CompilationDatabase.h"
#include "clang/Tooling/JSONCompilationDatabase.h"
#include "clang/Tooling/Core/Replacement.h"
#include "clang/Tooling/Tooling.h"
#include "llvm/ADT/SmallString.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/Errc.h"
#include "llvm/Support/Error.h"
#include "llvm/Support/InitLLVM.h"
#include "llvm/Support/JSON.h"
#include "llvm/Support/MemoryBuffer.h"
#include "llvm/Support/raw_ostream.h"

#include <algorithm>
#include <memory>
#include <set>
#include <string>
#include <utility>
#include <vector>

using namespace clang;
using namespace clang::ast_matchers;
using namespace clang::tooling;

namespace {

llvm::cl::OptionCategory Category("dsc-cicd-rewriter options");
llvm::cl::opt<std::string> Compdb("compdb", llvm::cl::desc("Compilation database"), llvm::cl::Required, llvm::cl::cat(Category));
llvm::cl::opt<std::string> TargetUSR("target-usr", llvm::cl::desc("USR of the selected function"), llvm::cl::Required, llvm::cl::cat(Category));
llvm::cl::opt<std::string> OriginalName("original-name", llvm::cl::desc("Renamed C implementation"), llvm::cl::Required, llvm::cl::cat(Category));
llvm::cl::opt<std::string> DispatcherName("dispatcher-name", llvm::cl::desc("Overlay dispatcher"), llvm::cl::Required, llvm::cl::cat(Category));
llvm::cl::opt<std::string> ReceiptPath("receipt", llvm::cl::desc("JSON receipt path"), llvm::cl::Required, llvm::cl::cat(Category));
llvm::cl::list<std::string> Sources(llvm::cl::Positional, llvm::cl::desc("Translation units"), llvm::cl::OneOrMore, llvm::cl::cat(Category));

struct RewriteState {
  bool failed = false;
  std::vector<std::string> failures;
  unsigned definitions = 0;
  unsigned directCalls = 0;
  unsigned rewrittenCalls = 0;
  std::set<std::string> rewrittenUSRs;
  std::set<std::string> changedFiles;
  std::set<std::string> indirectLocations;
  std::set<std::string> macroLocations;
  llvm::json::Array callSites;

  void fail(const std::string &Message) {
    failed = true;
    failures.push_back(Message);
  }
};

std::string usrFor(const Decl *D) {
  if (!D) return {};
  llvm::SmallString<256> Buffer;
  if (index::generateUSRForDecl(D, Buffer)) return {};
  return Buffer.str().str();
}

std::string locationString(const SourceManager &SM, SourceLocation Loc) {
  SourceLocation Spelling = SM.getSpellingLoc(Loc);
  PresumedLoc P = SM.getPresumedLoc(Spelling);
  if (P.isInvalid()) return "<invalid>";
  return (std::string(P.getFilename()) + ":" + std::to_string(P.getLine()) + ":" + std::to_string(P.getColumn()));
}

bool inMacro(const SourceManager &SM, SourceLocation Loc) {
  return Loc.isMacroID() || SM.isMacroBodyExpansion(Loc) || SM.isMacroArgExpansion(Loc);
}

std::string sourceText(const SourceManager &SM, const LangOptions &Lang, SourceRange Range) {
  if (Range.isInvalid()) return {};
  CharSourceRange Tokens = CharSourceRange::getTokenRange(Range);
  return Lexer::getSourceText(Tokens, SM, Lang).str();
}

class TargetReferenceVisitor : public RecursiveASTVisitor<TargetReferenceVisitor> {
 public:
  explicit TargetReferenceVisitor(std::string Target) : TargetUSRValue(std::move(Target)) {}
  bool VisitDeclRefExpr(DeclRefExpr *Reference) {
    if (usrFor(Reference->getDecl()) == TargetUSRValue) Found = true;
    return true;
  }
  bool found() const { return Found; }

 private:
  std::string TargetUSRValue;
  bool Found = false;
};

bool isDirectTargetReference(ASTContext &Context, const DeclRefExpr *Reference,
                             const std::string &Target) {
  DynTypedNode Current = DynTypedNode::create(*Reference);
  for (unsigned Depth = 0; Depth < 12; ++Depth) {
    auto Parents = Context.getParents(Current);
    if (Parents.empty()) return false;
    bool Advanced = false;
    for (const DynTypedNode &Parent : Parents) {
      if (const auto *Call = Parent.get<CallExpr>())
        return Call->getDirectCallee() && usrFor(Call->getDirectCallee()) == Target;
      if (Parent.get<Stmt>() || Parent.get<Decl>()) {
        Current = Parent;
        Advanced = true;
        break;
      }
    }
    if (!Advanced) return false;
  }
  return false;
}

std::string resultForCall(ASTContext &Context, const CallExpr *Call) {
  DynTypedNode Current = DynTypedNode::create(*Call);
  for (unsigned Depth = 0; Depth < 12; ++Depth) {
    auto Parents = Context.getParents(Current);
    if (Parents.empty()) return "discarded";
    bool Advanced = false;
    for (const DynTypedNode &Parent : Parents) {
      if (const auto *Assignment = Parent.get<BinaryOperator>()) {
        if (Assignment->isAssignmentOp()) {
          return sourceText(Context.getSourceManager(), Context.getLangOpts(), Assignment->getLHS()->getSourceRange());
        }
      }
      if (Parent.get<ReturnStmt>()) return "return_value";
      if (const auto *Variable = Parent.get<VarDecl>()) return Variable->getNameAsString();
      if (Parent.get<Stmt>() || Parent.get<Decl>()) {
        Current = Parent;
        Advanced = true;
        break;
      }
    }
    if (!Advanced) return "discarded";
  }
  return "discarded";
}

// Match callbacks need the target options, so this small adapter avoids
// global mutable selection state while still allowing one callback per tool.
class CallbackWithTarget : public MatchFinder::MatchCallback {
 public:
  CallbackWithTarget(std::shared_ptr<RewriteState> State, std::string Target)
      : StateValue(std::move(State)), TargetUSRValue(std::move(Target)) {}

  void onEndOfTranslationUnit() override {
    if (!Writer || !PendingReplacements || PendingReplacements->empty()) return;
    if (!applyAllReplacements(*PendingReplacements, *Writer) || Writer->overwriteChangedFiles())
      StateValue->fail("failed to write rewritten translation unit");
  }

  void run(const MatchFinder::MatchResult &Result) override {
    if (!Result.Context || !Result.SourceManager) return;
    ASTContext &Context = *Result.Context;
    SourceManager &SM = *Result.SourceManager;
    if (!Writer) {
      Writer = std::make_unique<Rewriter>(SM, Context.getLangOpts());
      PendingReplacements = std::make_unique<Replacements>();
    }
    auto mark = [&](SourceLocation Loc, const std::string &Message) {
      if (inMacro(SM, Loc)) {
        StateValue->macroLocations.insert(locationString(SM, Loc));
        StateValue->fail(Message);
        return true;
      }
      return false;
    };
    auto changed = [&](SourceLocation Loc) {
      StateValue->changedFiles.insert(SM.getFilename(SM.getSpellingLoc(Loc)).str());
    };

    if (const auto *Function = Result.Nodes.getNodeAs<FunctionDecl>("function")) {
      if (!Function->isThisDeclarationADefinition() || usrFor(Function) != TargetUSRValue) return;
      ++StateValue->definitions;
      SourceLocation Loc = Function->getNameInfo().getBeginLoc();
      if (mark(Loc, "target definition is inside a macro expansion")) return;
      if (auto Error = PendingReplacements->add(Replacement(
              SM, CharSourceRange::getTokenRange(Function->getNameInfo().getSourceRange()),
              OriginalName, Context.getLangOpts()))) {
        StateValue->fail("failed to record target definition replacement: " + llvm::toString(std::move(Error)));
      }
      changed(Loc);
      return;
    }

    if (const auto *Call = Result.Nodes.getNodeAs<CallExpr>("call")) {
      const FunctionDecl *Callee = Call->getDirectCallee();
      if (Callee && usrFor(Callee) == TargetUSRValue) {
        ++StateValue->directCalls;
        SourceLocation Loc = Call->getCallee()->getBeginLoc();
        if (mark(Loc, "direct target call is inside a macro expansion")) return;
        if (auto Error = PendingReplacements->add(Replacement(
                SM, CharSourceRange::getTokenRange(Call->getCallee()->getSourceRange()),
                DispatcherName, Context.getLangOpts()))) {
          StateValue->fail("failed to record target call replacement: " + llvm::toString(std::move(Error)));
        }
        changed(Loc);
        ++StateValue->rewrittenCalls;
        StateValue->rewrittenUSRs.insert(usrFor(Callee));
        llvm::json::Object Site;
        Site["callee_usr"] = usrFor(Callee);
        Site["location"] = locationString(SM, Call->getExprLoc());
        Site["call_text"] = sourceText(SM, Context.getLangOpts(), Call->getSourceRange());
        llvm::json::Array Arguments;
        for (const Expr *Argument : Call->arguments()) {
          Arguments.push_back(sourceText(SM, Context.getLangOpts(), Argument->getSourceRange()));
        }
        Site["arguments"] = std::move(Arguments);
        Site["result"] = resultForCall(Context, Call);
        StateValue->callSites.push_back(std::move(Site));
        return;
      }
      if (!Callee) {
        TargetReferenceVisitor Visitor(TargetUSRValue);
        Visitor.TraverseStmt(const_cast<Expr *>(Call->getCallee()));
        if (Visitor.found()) {
          std::string Location = locationString(SM, Call->getExprLoc());
          StateValue->indirectLocations.insert(Location);
          StateValue->fail("selected function is called indirectly at " + Location);
        }
      }
      return;
    }

    if (const auto *Reference = Result.Nodes.getNodeAs<DeclRefExpr>("reference")) {
      if (usrFor(Reference->getDecl()) != TargetUSRValue) return;
      bool IsDirectCallReference = isDirectTargetReference(Context, Reference, TargetUSRValue);
      if (!IsDirectCallReference) {
        std::string Location = locationString(SM, Reference->getExprLoc());
        StateValue->indirectLocations.insert(Location);
        StateValue->fail("selected function reference is not a direct call at " + Location);
      }
    }
  }

 private:
  std::shared_ptr<RewriteState> StateValue;
  std::string TargetUSRValue;
  std::unique_ptr<Rewriter> Writer;
  std::unique_ptr<Replacements> PendingReplacements;
};

class RewriteAction : public ASTFrontendAction {
 public:
  explicit RewriteAction(std::shared_ptr<RewriteState> State) : StateValue(std::move(State)) {}

  std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &, StringRef) override {
    Finder = std::make_unique<MatchFinder>();
    Callback = std::make_unique<CallbackWithTarget>(StateValue, TargetUSR);
    Finder->addMatcher(functionDecl(isDefinition()).bind("function"), Callback.get());
    Finder->addMatcher(callExpr().bind("call"), Callback.get());
    Finder->addMatcher(declRefExpr().bind("reference"), Callback.get());
    return Finder->newASTConsumer();
  }

 private:
  std::shared_ptr<RewriteState> StateValue;
  std::unique_ptr<MatchFinder> Finder;
  std::unique_ptr<CallbackWithTarget> Callback;
};

class ActionFactory : public FrontendActionFactory {
 public:
  explicit ActionFactory(std::shared_ptr<RewriteState> State) : StateValue(std::move(State)) {}
  std::unique_ptr<FrontendAction> create() override { return std::make_unique<RewriteAction>(StateValue); }

 private:
  std::shared_ptr<RewriteState> StateValue;
};

llvm::json::Array stringArray(const std::set<std::string> &Values) {
  llvm::json::Array Result;
  for (const auto &Value : Values) Result.push_back(Value);
  return Result;
}

void writeReceipt(RewriteState &State, int ToolResult) {
  llvm::json::Object Receipt;
  Receipt["schema_version"] = 1;
  Receipt["status"] = (!State.failed && ToolResult == 0 && State.definitions == 1 && State.rewrittenCalls == State.directCalls) ? "PASS" : "FAIL";
  Receipt["target_usr"] = TargetUSR;
  Receipt["original_name"] = OriginalName;
  Receipt["dispatcher_name"] = DispatcherName;
  Receipt["definitions_seen"] = State.definitions;
  Receipt["direct_calls_seen"] = State.directCalls;
  Receipt["rewritten_calls"] = State.rewrittenCalls;
  Receipt["rewritten_usrs"] = stringArray(State.rewrittenUSRs);
  Receipt["changed_files"] = stringArray(State.changedFiles);
  Receipt["macro_locations"] = stringArray(State.macroLocations);
  Receipt["indirect_locations"] = stringArray(State.indirectLocations);
  Receipt["call_sites"] = std::move(State.callSites);
  llvm::json::Array Failures;
  for (const auto &Failure : State.failures) Failures.push_back(Failure);
  Receipt["failures"] = std::move(Failures);
  std::error_code EC;
  llvm::raw_fd_ostream Out(ReceiptPath, EC);
  if (!EC) Out << llvm::json::Value(std::move(Receipt)) << "\n";
}

} // namespace

int main(int argc, const char **argv) {
  llvm::InitLLVM Init(argc, argv);
  llvm::cl::HideUnrelatedOptions(Category);
  llvm::cl::ParseCommandLineOptions(argc, argv);
  std::string Error;
  auto Database = JSONCompilationDatabase::loadFromFile(Compdb, Error, JSONCommandLineSyntax::AutoDetect);
  if (!Database) {
    llvm::errs() << "failed to load compilation database: " << Error << "\n";
    return 2;
  }
  auto State = std::make_shared<RewriteState>();
  ClangTool Tool(*Database, Sources);
  Tool.setDiagnosticConsumer(new IgnoringDiagConsumer());
  ActionFactory Factory(State);
  int Result = Tool.run(&Factory);
  writeReceipt(*State, Result);
  if (Result != 0 || State->failed || State->definitions != 1 || State->rewrittenCalls != State->directCalls) return 3;
  return 0;
}
