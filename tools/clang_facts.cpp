// Deterministic source facts collector for the public DSC C reference model.
//
// This executable deliberately uses Clang LibTooling and AST Matchers.  It
// does not tokenize or parse C source text itself; source text is only used
// for human-readable evidence ranges obtained from Clang's SourceManager.

#include "clang/AST/ASTContext.h"
#include "clang/AST/Decl.h"
#include "clang/AST/Expr.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/AST/Stmt.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/Basic/SourceManager.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Index/USRGeneration.h"
#include "clang/Lex/Lexer.h"
#include "clang/Tooling/JSONCompilationDatabase.h"
#include "clang/Tooling/Tooling.h"
#include "llvm/ADT/APSInt.h"
#include "llvm/ADT/SmallString.h"
#include "llvm/Support/CommandLine.h"

#include <algorithm>
#include <cctype>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <functional>
#include <limits>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <string>
#include <system_error>
#include <tuple>
#include <utility>
#include <vector>

using namespace clang;
using namespace clang::ast_matchers;
using namespace clang::tooling;

namespace {

llvm::cl::OptionCategory Category("dsc12a clang facts options");
llvm::cl::opt<std::string> Compdb(
    "compdb", llvm::cl::desc("compile_commands.json"), llvm::cl::Required,
    llvm::cl::cat(Category));
llvm::cl::opt<std::string> Output(
    "output", llvm::cl::desc("raw JSON output"), llvm::cl::Required,
    llvm::cl::cat(Category));
llvm::cl::opt<std::string> SourceRoot(
    "source-root", llvm::cl::desc("root of the public C source"),
    llvm::cl::Required, llvm::cl::cat(Category));

struct Location {
  std::string file;
  unsigned line = 0;
  unsigned column = 0;
};

struct Access {
  std::string name;
  std::string type;
  std::string record;
  std::string role;
  std::string context;
  Location location;
};

struct Dependency {
  std::string kind;
  std::string name;
  Location location;
};

struct CallEffect {
  std::string name;
  std::string usr;
  std::string category;
  Location location;
  bool direct = false;
};

struct OperatorFact {
  std::string spelling;
  std::string expression;
  Location location;
};

struct PointerParam {
  std::string name;
  std::string type;
  bool pointee_const = false;
  std::string mode = "READ_ONLY";
  std::vector<std::string> evidence;
};

struct LoopFact {
  std::string kind;
  std::string condition;
  std::string increment;
  std::string proof;
  std::string dependency_status = "UNKNOWN";
  std::vector<std::string> dependency_locations;
  std::vector<std::pair<std::string, int64_t>> trip_count_cases;
  bool has_fixed_trip_count = false;
  int64_t fixed_trip_count = 0;
  Location location;
};

struct GlobalDeclFact {
  std::string usr;
  std::string name;
  std::string type;
  Location location;
  bool is_const = false;
  bool is_static = false;
  bool is_array = false;
  uint64_t array_size = 0;
  std::vector<int64_t> constant_values;
};

struct FunctionFact {
  std::string usr;
  std::string name;
  std::string qualified_name;
  std::string return_type;
  Location location;
  bool is_static = false;
  std::vector<std::tuple<std::string, std::string, bool, bool>> parameters;
  std::map<std::string, std::string> callers;
  std::map<std::string, std::string> callees;
  std::vector<Access> globals_read;
  std::vector<Access> globals_write;
  std::vector<Access> fields_read;
  std::vector<Access> fields_write;
  std::vector<PointerParam> pointer_parameters;
  std::vector<std::string> static_mutable_state;
  std::vector<CallEffect> calls;
  std::vector<OperatorFact> operators;
  std::vector<LoopFact> loops;
  std::vector<Dependency> return_dependencies;
  std::set<std::string> unknown_facts;
  bool file_io = false;
  bool logging = false;
  bool assertion = false;
  bool allocation = false;
  bool indirect_call = false;
};

struct Edge {
  std::string caller_usr;
  std::string caller_name;
  std::string callee_usr;
  std::string callee_name;
  Location location;
};

struct SourceOrder {
  bool operator()(const Location &a, const Location &b) const {
    return std::tie(a.file, a.line, a.column) <
           std::tie(b.file, b.line, b.column);
  }
};

std::string jsonEscape(const std::string &input) {
  std::ostringstream out;
  for (unsigned char c : input) {
    switch (c) {
    case '"':
      out << "\\\"";
      break;
    case '\\':
      out << "\\\\";
      break;
    case '\b':
      out << "\\b";
      break;
    case '\f':
      out << "\\f";
      break;
    case '\n':
      out << "\\n";
      break;
    case '\r':
      out << "\\r";
      break;
    case '\t':
      out << "\\t";
      break;
    default:
      if (c < 0x20)
        out << "\\u00" << std::hex << static_cast<int>(c) << std::dec;
      else
        out << c;
    }
  }
  return out.str();
}

void quoted(std::ostream &out, const std::string &value) {
  out << '"' << jsonEscape(value) << '"';
}

std::string trimType(std::string value) {
  while (!value.empty() && value.back() == ' ')
    value.pop_back();
  return value;
}

std::string canonicalRecordName(const RecordDecl *record) {
  if (!record)
    return "UNKNOWN";
  std::string name = record->getNameAsString();
  if (name == "dsc_cfg_s")
    return "dsc_cfg_t";
  if (name == "dsc_state_s")
    return "dsc_state_t";
  if (name == "dsc_range_cfg_s")
    return "dsc_range_cfg_t";
  if (name == "dsc_history_s")
    return "dsc_history_t";
  return name.empty() ? "ANONYMOUS" : name;
}

std::string usrForDecl(const Decl *decl) {
  if (!decl)
    return "UNKNOWN";
  llvm::SmallString<256> storage;
  if (index::generateUSRForDecl(decl, storage))
    return "UNKNOWN";
  return storage.str().str();
}

bool isBeforeOrEqual(const SourceManager &sm, SourceLocation a,
                     SourceLocation b) {
  if (a.isInvalid() || b.isInvalid())
    return false;
  return !sm.isBeforeInTranslationUnit(b, a);
}

bool rangeContains(const SourceManager &sm, SourceRange outer,
                   SourceRange inner) {
  if (outer.isInvalid() || inner.isInvalid())
    return false;
  return isBeforeOrEqual(sm, outer.getBegin(), inner.getBegin()) &&
         isBeforeOrEqual(sm, inner.getEnd(), outer.getEnd());
}

std::string sourceText(const Expr *expr, ASTContext &context) {
  if (!expr)
    return "";
  auto range = CharSourceRange::getTokenRange(expr->getSourceRange());
  return Lexer::getSourceText(range, context.getSourceManager(),
                              context.getLangOpts())
      .str();
}

std::string sourceText(const Stmt *stmt, ASTContext &context) {
  if (!stmt)
    return "";
  auto range = CharSourceRange::getTokenRange(stmt->getSourceRange());
  return Lexer::getSourceText(range, context.getSourceManager(),
                              context.getLangOpts())
      .str();
}

Location locationFor(SourceLocation source_location, ASTContext &context) {
  const auto &sm = context.getSourceManager();
  PresumedLoc presumed = sm.getPresumedLoc(sm.getExpansionLoc(source_location));
  if (presumed.isInvalid())
    return {};
  std::filesystem::path file(presumed.getFilename());
  std::filesystem::path root(SourceRoot.getValue());
  std::error_code ec;
  auto canonical_file = std::filesystem::weakly_canonical(file, ec);
  ec.clear();
  auto canonical_root = std::filesystem::weakly_canonical(root, ec);
  std::string relative;
  ec.clear();
  auto candidate = std::filesystem::relative(canonical_file, canonical_root, ec);
  if (!ec && !candidate.empty() && candidate.native().rfind("..", 0) != 0)
    relative = candidate.generic_string();
  else
    relative = std::string("<external>/") + canonical_file.filename().generic_string();
  return {relative, presumed.getLine(), presumed.getColumn()};
}

bool evaluateInt(const Expr *expr, ASTContext &context, int64_t &value) {
  if (!expr)
    return false;
  Expr::EvalResult result;
  if (!expr->EvaluateAsInt(result, context))
    return false;
  const llvm::APSInt &number = result.Val.getInt();
  if (number.getBitWidth() > 63 && !number.isSigned())
    return false;
  value = number.getSExtValue();
  return true;
}

const DeclRefExpr *findDeclRef(const Expr *expr) {
  if (!expr)
    return nullptr;
  expr = expr->IgnoreParenImpCasts();
  if (auto *ref = dyn_cast<DeclRefExpr>(expr))
    return ref;
  if (auto *unary = dyn_cast<UnaryOperator>(expr))
    return findDeclRef(unary->getSubExpr());
  return nullptr;
}

class ContainsDeclVisitor
    : public RecursiveASTVisitor<ContainsDeclVisitor> {
public:
  explicit ContainsDeclVisitor(const ValueDecl *needle) : needle(needle) {}
  bool VisitDeclRefExpr(DeclRefExpr *ref) {
    if (ref->getDecl()->getCanonicalDecl() == needle->getCanonicalDecl())
      found = true;
    return true;
  }
  bool found = false;

private:
  const ValueDecl *needle;
};

bool containsDecl(const Stmt *stmt, const ValueDecl *decl) {
  if (!stmt || !decl)
    return false;
  ContainsDeclVisitor visitor(decl);
  visitor.TraverseStmt(const_cast<Stmt *>(stmt));
  return visitor.found;
}

bool isWriteExpr(const Expr *expr, ASTContext &context) {
  const SourceManager &sm = context.getSourceManager();
  const Stmt *current = expr;
  for (unsigned depth = 0; depth < 10 && current; ++depth) {
    auto parents = context.getParents(*current);
    if (parents.empty())
      return false;
    const DynTypedNode &parent = parents[0];
    if (const auto *binary = parent.get<BinaryOperator>()) {
      if (binary->isAssignmentOp() &&
          rangeContains(sm, binary->getLHS()->getSourceRange(),
                        expr->getSourceRange()))
        return true;
      return false;
    }
    if (const auto *unary = parent.get<UnaryOperator>()) {
      if (unary->isIncrementDecrementOp())
        return true;
      return false;
    }
    if (const auto *compound = parent.get<CompoundAssignOperator>()) {
      if (rangeContains(sm, compound->getLHS()->getSourceRange(),
                        expr->getSourceRange()))
        return true;
      return false;
    }
    if (const auto *statement = parent.get<Stmt>()) {
      current = statement;
      continue;
    }
    return false;
  }
  return false;
}

std::string accessContext(const Expr *expr, ASTContext &context) {
  const SourceManager &sm = context.getSourceManager();
  const Stmt *current = expr;
  for (unsigned depth = 0; depth < 8 && current; ++depth) {
    auto parents = context.getParents(*current);
    if (parents.empty())
      break;
    const DynTypedNode &parent = parents[0];
    if (const auto *call = parent.get<CallExpr>()) {
      for (const Expr *argument : call->arguments())
        if (rangeContains(sm, argument->getSourceRange(), expr->getSourceRange()))
          return "call_argument";
    }
    if (const auto *array = parent.get<ArraySubscriptExpr>()) {
      if (rangeContains(sm, array->getIdx()->getSourceRange(),
                        expr->getSourceRange()))
        return "array_index";
    }
    if (const auto *if_stmt = parent.get<IfStmt>()) {
      if (if_stmt->getCond() &&
          rangeContains(sm, if_stmt->getCond()->getSourceRange(),
                        expr->getSourceRange()))
        return "condition";
    }
    if (const auto *for_stmt = parent.get<ForStmt>()) {
      if (for_stmt->getCond() &&
          rangeContains(sm, for_stmt->getCond()->getSourceRange(),
                        expr->getSourceRange()))
        return "condition";
    }
    if (const auto *statement = parent.get<Stmt>()) {
      current = statement;
      continue;
    }
    break;
  }
  return "expression";
}

std::string accessRole(const Expr *expr, ASTContext &context) {
  return isWriteExpr(expr, context) ? "WRITE" : "READ";
}

struct AccessKey {
  std::string name;
  std::string record;
  std::string role;
  Location location;
  bool operator<(const AccessKey &other) const {
    return std::tie(name, record, role, location.file, location.line,
                    location.column) <
           std::tie(other.name, other.record, other.role, other.location.file,
                    other.location.line, other.location.column);
  }
};

void addAccess(std::vector<Access> &accesses, Access access) {
  AccessKey key{access.name, access.record, access.role, access.location};
  for (const Access &existing : accesses) {
    AccessKey existing_key{existing.name, existing.record, existing.role,
                           existing.location};
    if (!(key < existing_key) && !(existing_key < key))
      return;
  }
  accesses.push_back(std::move(access));
}

void addDependency(std::vector<Dependency> &dependencies, Dependency dep) {
  for (const auto &existing : dependencies) {
    if (existing.kind == dep.kind && existing.name == dep.name &&
        existing.location.file == dep.location.file &&
        existing.location.line == dep.location.line)
      return;
  }
  dependencies.push_back(std::move(dep));
}

class ReturnDependencyVisitor
    : public RecursiveASTVisitor<ReturnDependencyVisitor> {
public:
  ReturnDependencyVisitor(FunctionFact &fact, ASTContext &context)
      : fact(fact), context(context) {}

  bool VisitDeclRefExpr(DeclRefExpr *ref) {
    const auto *value = ref->getDecl();
    Location loc = locationFor(ref->getExprLoc(), context);
    if (const auto *param = dyn_cast<ParmVarDecl>(value)) {
      addDependency(fact.return_dependencies,
                    {"parameter", param->getNameAsString(), loc});
    } else if (const auto *var = dyn_cast<VarDecl>(value)) {
      if (var->hasGlobalStorage())
        addDependency(fact.return_dependencies,
                      {"global", var->getQualifiedNameAsString(), loc});
    }
    return true;
  }

  bool VisitMemberExpr(MemberExpr *member) {
    if (const auto *field = dyn_cast<FieldDecl>(member->getMemberDecl()))
      addDependency(fact.return_dependencies,
                    {"field", canonicalRecordName(field->getParent()) +
                                   "." + field->getNameAsString(),
                     locationFor(member->getExprLoc(), context)});
    return true;
  }

  bool VisitCallExpr(CallExpr *call) {
    if (const FunctionDecl *callee = call->getDirectCallee())
      addDependency(fact.return_dependencies,
                    {"callee", callee->getQualifiedNameAsString(),
                     locationFor(call->getExprLoc(), context)});
    return true;
  }

private:
  FunctionFact &fact;
  ASTContext &context;
};

class BreakVisitor : public RecursiveASTVisitor<BreakVisitor> {
public:
  bool VisitBreakStmt(BreakStmt *) {
    found = true;
    return true;
  }
  bool found = false;
};

class LoopEffectVisitor : public RecursiveASTVisitor<LoopEffectVisitor> {
public:
  explicit LoopEffectVisitor(ASTContext &context) : context(context) {}

  bool VisitDeclRefExpr(DeclRefExpr *ref) {
    const auto *value = ref->getDecl();
    std::string key;
    if (const auto *field = dyn_cast<FieldDecl>(value))
      key = "field:" + canonicalRecordName(field->getParent()) + "." +
            field->getNameAsString();
    else if (const auto *var = dyn_cast<VarDecl>(value))
      key = "var:" + var->getQualifiedNameAsString();
    if (key.empty())
      return true;
    if (isWriteExpr(ref, context))
      writes.insert(key);
    else
      reads.insert(key);
    return true;
  }

  std::set<std::string> reads;
  std::set<std::string> writes;

private:
  ASTContext &context;
};

struct LoopBounds {
  bool valid = false;
  bool has_fixed = false;
  int64_t fixed = 0;
  std::vector<std::pair<std::string, int64_t>> cases;
  std::string proof;
};

LoopBounds loopBounds(const ForStmt *loop, ASTContext &context) {
  LoopBounds result;
  const VarDecl *loop_var = nullptr;
  int64_t start = 0;
  if (const auto *decl_stmt = dyn_cast_or_null<DeclStmt>(loop->getInit());
      decl_stmt && decl_stmt->isSingleDecl()) {
    loop_var = dyn_cast<VarDecl>(decl_stmt->getSingleDecl());
    if (!loop_var || !evaluateInt(loop_var->getInit(), context, start)) {
      result.proof = "UNKNOWN: initializer value is not constant";
      return result;
    }
  } else if (const auto *assignment =
                 dyn_cast_or_null<BinaryOperator>(loop->getInit());
             assignment && assignment->getOpcode() == BO_Assign) {
    const auto *lhs = findDeclRef(assignment->getLHS());
    loop_var = lhs ? dyn_cast<VarDecl>(lhs->getDecl()) : nullptr;
    if (!loop_var || !evaluateInt(assignment->getRHS(), context, start)) {
      result.proof = "UNKNOWN: assignment initializer value is not constant";
      return result;
    }
  } else {
    result.proof = "UNKNOWN: initializer is not a local declaration or assignment";
    return result;
  }
  const auto *condition = dyn_cast_or_null<BinaryOperator>(loop->getCond());
  if (!condition ||
      !findDeclRef(condition->getLHS()) ||
      findDeclRef(condition->getLHS())->getDecl()->getCanonicalDecl() !=
          loop_var->getCanonicalDecl()) {
    result.proof = "UNKNOWN: condition is not a canonical comparison";
    return result;
  }
  int64_t step = 0;
  const Stmt *increment = loop->getInc();
  if (const auto *unary = dyn_cast_or_null<UnaryOperator>(increment)) {
    if (unary->isIncrementOp())
      step = 1;
    else if (unary->isDecrementOp())
      step = -1;
  } else if (const auto *compound = dyn_cast_or_null<CompoundAssignOperator>(increment)) {
    if (findDeclRef(compound->getLHS()) &&
        findDeclRef(compound->getLHS())->getDecl()->getCanonicalDecl() ==
            loop_var->getCanonicalDecl()) {
      if (compound->getOpcode() == BO_AddAssign)
        evaluateInt(compound->getRHS(), context, step);
      else if (compound->getOpcode() == BO_SubAssign) {
        if (evaluateInt(compound->getRHS(), context, step))
          step = -step;
      }
    }
  }
  if (step == 0) {
    result.proof = "UNKNOWN: increment is not a constant unit step";
    return result;
  }

  auto tripCountForLimit = [&](int64_t limit, int64_t &count) {
    if (step > 0 && condition->getOpcode() == BO_LT) {
      count = limit <= start ? 0 : (limit - start + step - 1) / step;
      return true;
    }
    if (step > 0 && condition->getOpcode() == BO_LE) {
      count = limit < start ? 0 : (limit - start) / step + 1;
      return true;
    }
    if (step < 0 && condition->getOpcode() == BO_GT) {
      count = limit >= start ? 0 : (start - limit + (-step) - 1) / (-step);
      return true;
    }
    if (step < 0 && condition->getOpcode() == BO_GE) {
      count = limit > start ? 0 : (start - limit) / (-step) + 1;
      return true;
    }
    return false;
  };

  int64_t limit = 0;
  const auto *conditional = dyn_cast<ConditionalOperator>(
      condition->getRHS()->IgnoreParenImpCasts());
  if (conditional) {
    int64_t true_value = 0;
    int64_t false_value = 0;
    int64_t true_count = 0;
    int64_t false_count = 0;
    if (evaluateInt(conditional->getTrueExpr(), context, true_value) &&
        evaluateInt(conditional->getFalseExpr(), context, false_value) &&
        tripCountForLimit(true_value, true_count) &&
        tripCountForLimit(false_value, false_count)) {
      result.valid = true;
      result.cases.push_back({"condition true", true_count});
      result.cases.push_back({"condition false", false_count});
      result.proof = "CONDITIONAL_FIXED_BOUND: both conditional bounds are constants";
    } else {
      result.proof = "UNKNOWN: conditional bound is not constant";
    }
  } else if (evaluateInt(condition->getRHS(), context, limit)) {
    int64_t count = 0;
    if (!tripCountForLimit(limit, count)) {
      result.proof = "CONSTANT_BOUND_ZERO_OR_UNKNOWN: comparison may be empty";
      return result;
    }
    result.valid = true;
    result.has_fixed = true;
    result.fixed = count;
    result.proof = "FIXED_TRIP_COUNT: constant initializer, bound, and step";
  } else {
    result.proof = "UNKNOWN: loop bound is not constant";
  }
  return result;
}

std::string callCategory(const std::string &name) {
  std::string lower = name;
  std::transform(lower.begin(), lower.end(), lower.begin(),
                 [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
  if (lower.find("malloc") != std::string::npos ||
      lower.find("calloc") != std::string::npos ||
      lower.find("realloc") != std::string::npos || lower == "free")
    return "malloc";
  if (lower.find("fopen") != std::string::npos ||
      lower.find("fclose") != std::string::npos ||
      lower.find("fread") != std::string::npos ||
      lower.find("fwrite") != std::string::npos ||
      lower.find("fprintf") != std::string::npos || lower == "open" ||
      lower == "close" || lower == "read" || lower == "write")
    return "file_io";
  if (lower.find("assert") != std::string::npos)
    return "assert";
  if (lower.find("printf") != std::string::npos ||
      lower.find("puts") != std::string::npos ||
      lower.find("perror") != std::string::npos || lower == "uerr" ||
      lower.find("log") != std::string::npos)
    return "logging";
  return "other";
}

class PointerUseVisitor : public RecursiveASTVisitor<PointerUseVisitor> {
public:
  PointerUseVisitor(FunctionFact &fact, ASTContext &context)
      : fact(fact), context(context) {}

  bool VisitDeclRefExpr(DeclRefExpr *ref) {
    for (auto &param : fact.pointer_parameters) {
      if (ref->getDecl()->getNameAsString() == param.name &&
          isWriteExpr(ref, context)) {
        param.mode = "WRITES_THROUGH";
        addEvidence(param, "pointer expression is in a write context");
      }
    }
    return true;
  }

  bool VisitBinaryOperator(BinaryOperator *binary) {
    if (!binary->isAssignmentOp())
      return true;
    for (auto &param : fact.pointer_parameters) {
      for (const auto *decl : pointerDecls()) {
        if (decl->getNameAsString() == param.name &&
            containsDecl(binary->getLHS(), decl)) {
          param.mode = "WRITES_THROUGH";
          addEvidence(param, "assignment LHS contains pointer parameter");
        }
      }
    }
    return true;
  }

  bool VisitCallExpr(CallExpr *call) {
    const FunctionDecl *callee = call->getDirectCallee();
    for (unsigned i = 0; i < call->getNumArgs(); ++i) {
      const Expr *argument = call->getArg(i);
      for (const auto *decl : pointerDecls()) {
        if (!containsDecl(argument, decl))
          continue;
        bool known_read_only = false;
        if (callee && i < callee->getNumParams()) {
          QualType parameter_type = callee->getParamDecl(i)->getType();
          known_read_only = parameter_type->isPointerType() &&
                            parameter_type->getPointeeType().isConstQualified();
        }
        if (!known_read_only) {
          for (auto &param : fact.pointer_parameters) {
            if (param.name == decl->getNameAsString()) {
              param.mode = "UNKNOWN";
              addEvidence(param, "pointer escapes to a non-const or indirect call");
            }
          }
        }
      }
    }
    return true;
  }

private:
  std::vector<const ParmVarDecl *> pointerDecls() const {
    std::vector<const ParmVarDecl *> result;
    for (const auto &param : fact.parameters) {
      if (!std::get<2>(param))
        continue;
      // The visitor is only used for the current function.  Names are enough
      // for the C model's non-overloaded parameter list; the final facts keep
      // the type from Clang as the authoritative identity.
      for (const ParmVarDecl *decl : current_params)
        if (decl->getNameAsString() == std::get<0>(param))
          result.push_back(decl);
    }
    return result;
  }

public:
  std::vector<const ParmVarDecl *> current_params;

private:
  static void addEvidence(PointerParam &param, const char *evidence) {
    if (std::find(param.evidence.begin(), param.evidence.end(), evidence) ==
        param.evidence.end())
      param.evidence.emplace_back(evidence);
  }

  FunctionFact &fact;
  ASTContext &context;
};

class FactCollector : public MatchFinder::MatchCallback {
public:
  explicit FactCollector(std::string source_root)
      : source_root(std::move(source_root)) {}

  void registerMatchers() {
    finder.addMatcher(functionDecl(isDefinition()).bind("function"), this);
    finder.addMatcher(
        functionDecl(isDefinition(), forEachDescendant(
                                         callExpr().bind("call")))
            .bind("call_function"),
        this);
    finder.addMatcher(
        functionDecl(isDefinition(), forEachDescendant(
                                         memberExpr().bind("field_access")))
            .bind("field_function"),
        this);
    finder.addMatcher(
        functionDecl(isDefinition(), forEachDescendant(
                                         declRefExpr().bind("var_ref")))
            .bind("var_function"),
        this);
    finder.addMatcher(
        functionDecl(isDefinition(), forEachDescendant(
                                         binaryOperator(hasOperatorName("%"))
                                             .bind("modulo_operator")))
            .bind("operator_function"),
        this);
    finder.addMatcher(
        functionDecl(isDefinition(),
                     forEachDescendant(stmt(anyOf(
                         forStmt().bind("for_loop"),
                         whileStmt().bind("while_loop"),
                         doStmt().bind("do_loop")))))
            .bind("loop_function"),
        this);
    finder.addMatcher(
        functionDecl(isDefinition(),
                     forEachDescendant(
                         returnStmt(hasReturnValue(expr().bind("return_expr")))))
            .bind("return_function"),
        this);
    finder.addMatcher(varDecl(isDefinition()).bind("global_decl"), this);
  }

  std::unique_ptr<ASTConsumer> newConsumer() { return finder.newASTConsumer(); }

  void setContext(ASTContext *context) { current_context = context; }

  void run(const MatchFinder::MatchResult &result) override {
    ASTContext *context = result.Context;
    if (!context)
      return;
    setContext(context);

    if (const auto *global = result.Nodes.getNodeAs<VarDecl>("global_decl"))
      collectGlobal(global, *context);

    FunctionDecl *function = nullptr;
    for (const char *binding : {"function", "call_function", "field_function",
                                "var_function", "loop_function",
                                "return_function", "operator_function"}) {
      if ((function = const_cast<FunctionDecl *>(
               result.Nodes.getNodeAs<FunctionDecl>(binding))))
        break;
    }
    if (!function)
      return;
    FunctionFact &fact = ensureFunction(function, *context);

    if (result.Nodes.getNodeAs<CallExpr>("call"))
      collectCall(fact, result.Nodes.getNodeAs<CallExpr>("call"), *context);
    if (result.Nodes.getNodeAs<MemberExpr>("field_access"))
      collectField(fact, result.Nodes.getNodeAs<MemberExpr>("field_access"),
                   *context);
    if (result.Nodes.getNodeAs<DeclRefExpr>("var_ref"))
      collectVariable(fact, result.Nodes.getNodeAs<DeclRefExpr>("var_ref"),
                      *context);
    if (const auto *loop = result.Nodes.getNodeAs<ForStmt>("for_loop"))
      collectLoop(fact, loop, "for", *context);
    if (const auto *loop = result.Nodes.getNodeAs<WhileStmt>("while_loop"))
      collectLoop(fact, loop, "while", *context);
    if (const auto *loop = result.Nodes.getNodeAs<DoStmt>("do_loop"))
      collectLoop(fact, loop, "do", *context);
    if (const auto *return_expr = result.Nodes.getNodeAs<Expr>("return_expr")) {
      ReturnDependencyVisitor visitor(fact, *context);
      visitor.TraverseStmt(const_cast<Expr *>(return_expr));
    }
    if (const auto *modulo =
            result.Nodes.getNodeAs<BinaryOperator>("modulo_operator")) {
      fact.operators.push_back(
          {"%", sourceText(modulo, *context),
           locationFor(modulo->getOperatorLoc(), *context)});
    }

    // Pointer and parameter facts are derived only after the declaration is
    // seen. Re-running this small visitor is deterministic and avoids a text
    // parser or a second analysis representation.
    if (function->hasBody() && !fact.pointer_parameters.empty()) {
      PointerUseVisitor visitor(fact, *context);
      for (const ParmVarDecl *param : function->parameters())
        visitor.current_params.push_back(param);
      visitor.TraverseStmt(function->getBody());
    }
  }

  const std::map<std::string, FunctionFact> &getFunctions() const {
    return functions;
  }
  const std::vector<Edge> &getEdges() const { return edges; }
  const std::map<std::string, GlobalDeclFact> &getGlobals() const {
    return globals;
  }

  void writeJson(const std::string &path) const {
    std::ofstream out(path);
    out << "{\n  \"functions\": [\n";
    bool first = true;
    for (const auto &pair : functions) {
      if (!first)
        out << ",\n";
      first = false;
      writeFunction(out, pair.second, 4);
    }
    out << "\n  ],\n  \"edges\": [\n";
    first = true;
    std::vector<Edge> sorted_edges = edges;
    std::sort(sorted_edges.begin(), sorted_edges.end(), [](const Edge &a, const Edge &b) {
      return std::tie(a.caller_usr, a.callee_usr, a.location.file,
                      a.location.line, a.location.column) <
             std::tie(b.caller_usr, b.callee_usr, b.location.file,
                      b.location.line, b.location.column);
    });
    for (const auto &edge : sorted_edges) {
      if (!first)
        out << ",\n";
      first = false;
      out << "    {\"caller_usr\":";
      quoted(out, edge.caller_usr);
      out << ",\"caller_name\":";
      quoted(out, edge.caller_name);
      out << ",\"callee_usr\":";
      quoted(out, edge.callee_usr);
      out << ",\"callee_name\":";
      quoted(out, edge.callee_name);
      out << ",\"location\":";
      writeLocation(out, edge.location, 0);
      out << "}";
    }
    out << "\n  ],\n  \"global_declarations\": [\n";
    first = true;
    for (const auto &pair : globals) {
      if (!first)
        out << ",\n";
      first = false;
      writeGlobal(out, pair.second, 4);
    }
    out << "\n  ]\n}\n";
  }

private:
  FunctionFact &ensureFunction(FunctionDecl *function, ASTContext &context) {
    FunctionDecl *canonical = function->getCanonicalDecl();
    std::string usr = usrForDecl(canonical);
    if (usr == "UNKNOWN") {
      Location loc = locationFor(function->getLocation(), context);
      usr = "UNKNOWN:" + function->getNameAsString() + ":" + loc.file + ":" +
            std::to_string(loc.line);
    }
    FunctionFact &fact = functions[usr];
    fact.usr = usr;
    fact.name = function->getNameAsString();
    fact.qualified_name = function->getQualifiedNameAsString();
    fact.return_type = trimType(function->getReturnType().getAsString());
    fact.location = locationFor(function->getLocation(), context);
    fact.is_static = function->getStorageClass() == SC_Static;
    if (fact.parameters.empty()) {
      for (const ParmVarDecl *param : function->parameters()) {
        QualType type = param->getType();
        bool pointer = type->isPointerType();
        bool pointee_const = pointer && type->getPointeeType().isConstQualified();
        fact.parameters.emplace_back(param->getNameAsString(),
                                     trimType(type.getAsString()), pointer,
                                     pointee_const);
        if (pointer) {
          PointerParam pointer_fact;
          pointer_fact.name = param->getNameAsString();
          pointer_fact.type = trimType(type.getAsString());
          pointer_fact.pointee_const = pointee_const;
          pointer_fact.evidence.push_back("Clang parameter type is a pointer");
          fact.pointer_parameters.push_back(std::move(pointer_fact));
        }
      }
    }
    return fact;
  }

  void collectGlobal(const VarDecl *global, ASTContext &context) {
    if (!global->hasGlobalStorage() || !global->isFileVarDecl() ||
        !global->isThisDeclarationADefinition())
      return;
    std::string usr = usrForDecl(global->getCanonicalDecl());
    GlobalDeclFact &fact = globals[usr];
    fact.usr = usr;
    fact.name = global->getQualifiedNameAsString();
    fact.type = trimType(global->getType().getAsString());
    fact.location = locationFor(global->getLocation(), context);
    fact.is_const = global->getType().isConstQualified();
    fact.is_static = global->getStorageClass() == SC_Static;
    if (const auto *array = context.getAsConstantArrayType(global->getType())) {
      fact.is_array = true;
      fact.array_size = array->getSize().getZExtValue();
    }
    if (const auto *list = dyn_cast_or_null<InitListExpr>(global->getAnyInitializer())) {
      for (const Expr *init : list->inits()) {
        int64_t value = 0;
        if (evaluateInt(init, context, value))
          fact.constant_values.push_back(value);
      }
    }
  }

  void collectCall(FunctionFact &caller, const CallExpr *call,
                   ASTContext &context) {
    const FunctionDecl *callee = call->getDirectCallee();
    CallEffect effect;
    effect.location = locationFor(call->getExprLoc(), context);
    if (callee) {
      effect.name = callee->getQualifiedNameAsString();
      effect.usr = usrForDecl(callee->getCanonicalDecl());
      effect.direct = true;
      std::string name = callee->getNameAsString();
      edges.push_back({caller.usr, caller.name, effect.usr, effect.name,
                       effect.location});
      caller.callees[effect.usr] = effect.name;
      functions[effect.usr].callers[caller.usr] = caller.name;
    } else {
      effect.name = "<indirect-call>";
      effect.usr = "UNKNOWN";
      effect.direct = false;
      caller.indirect_call = true;
      caller.unknown_facts.insert("indirect call target");
    }
    effect.category = callCategory(effect.name);
    caller.file_io |= effect.category == "file_io";
    caller.logging |= effect.category == "logging";
    caller.assertion |= effect.category == "assert";
    caller.allocation |= effect.category == "malloc";
    caller.calls.push_back(std::move(effect));
  }

  void collectField(FunctionFact &function, const MemberExpr *member,
                    ASTContext &context) {
    const auto *field = dyn_cast<FieldDecl>(member->getMemberDecl());
    if (!field)
      return;
    Access access;
    access.name = field->getNameAsString();
    access.type = trimType(field->getType().getAsString());
    access.record = canonicalRecordName(field->getParent());
    access.role = accessRole(member, context);
    access.context = accessContext(member, context);
    access.location = locationFor(member->getExprLoc(), context);
    if (access.role == "WRITE")
      addAccess(function.fields_write, access);
    else
      addAccess(function.fields_read, access);
  }

  void collectVariable(FunctionFact &function, const DeclRefExpr *ref,
                       ASTContext &context) {
    const auto *var = dyn_cast<VarDecl>(ref->getDecl());
    if (!var || !var->hasGlobalStorage() || isa<ParmVarDecl>(var))
      return;
    Access access;
    access.name = var->getQualifiedNameAsString();
    access.type = trimType(var->getType().getAsString());
    access.record = "";
    access.role = accessRole(ref, context);
    access.context = accessContext(ref, context);
    access.location = locationFor(ref->getExprLoc(), context);
    if (access.role == "WRITE")
      addAccess(function.globals_write, access);
    else
      addAccess(function.globals_read, access);
    if ((var->isStaticLocal() || var->getStorageClass() == SC_Static) &&
        !var->getType().isConstQualified()) {
      function.static_mutable_state.push_back(var->getQualifiedNameAsString());
      std::sort(function.static_mutable_state.begin(),
                function.static_mutable_state.end());
      function.static_mutable_state.erase(
          std::unique(function.static_mutable_state.begin(),
                      function.static_mutable_state.end()),
          function.static_mutable_state.end());
    }
  }

  void collectLoop(FunctionFact &function, const Stmt *loop,
                   const std::string &kind, ASTContext &context) {
    LoopFact fact;
    fact.kind = kind;
    fact.location = locationFor(loop->getBeginLoc(), context);
    if (const auto *for_loop = dyn_cast<ForStmt>(loop)) {
      fact.condition = sourceText(for_loop->getCond(), context);
      fact.increment = sourceText(for_loop->getInc(), context);
      LoopBounds bounds = loopBounds(for_loop, context);
      fact.proof = bounds.proof;
      fact.has_fixed_trip_count = bounds.has_fixed;
      fact.fixed_trip_count = bounds.fixed;
      fact.trip_count_cases = bounds.cases;
    } else if (const auto *while_loop = dyn_cast<WhileStmt>(loop)) {
      fact.condition = sourceText(while_loop->getCond(), context);
      fact.proof = "UNKNOWN: while-loop bound is not statically canonicalized";
    } else if (const auto *do_loop = dyn_cast<DoStmt>(loop)) {
      fact.condition = sourceText(do_loop->getCond(), context);
      fact.proof = "UNKNOWN: do-loop bound is not statically canonicalized";
    }
    const Stmt *body = nullptr;
    if (const auto *for_loop = dyn_cast<ForStmt>(loop))
      body = for_loop->getBody();
    else if (const auto *while_loop = dyn_cast<WhileStmt>(loop))
      body = while_loop->getBody();
    else if (const auto *do_loop = dyn_cast<DoStmt>(loop))
      body = do_loop->getBody();
    if (body) {
      BreakVisitor breaks;
      breaks.TraverseStmt(const_cast<Stmt *>(body));
      if (breaks.found) {
        fact.has_fixed_trip_count = false;
        fact.proof += "; UNKNOWN: break statement is present";
      }
      LoopEffectVisitor effects(context);
      effects.TraverseStmt(const_cast<Stmt *>(body));
      for (const std::string &key : effects.reads)
        if (effects.writes.count(key))
          fact.dependency_locations.push_back(key);
      std::sort(fact.dependency_locations.begin(),
                fact.dependency_locations.end());
      fact.dependency_locations.erase(
          std::unique(fact.dependency_locations.begin(),
                      fact.dependency_locations.end()),
          fact.dependency_locations.end());
      fact.dependency_status = fact.dependency_locations.empty()
                                   ? "NO_SAME_LOCATION_READ_WRITE_OBSERVED"
                                   : "POTENTIAL_CROSS_ITERATION_DEPENDENCY";
    }
    function.loops.push_back(std::move(fact));
  }

  static void writeIndent(std::ostream &out, unsigned indent) {
    for (unsigned i = 0; i < indent; ++i)
      out << ' ';
  }

  static void writeLocation(std::ostream &out, const Location &location,
                            unsigned indent) {
    (void)indent;
    out << "{\"file\":";
    quoted(out, location.file);
    out << ",\"line\":" << location.line << ",\"column\":"
        << location.column << "}";
  }

  static void writeAccessArray(std::ostream &out,
                               const std::vector<Access> &accesses,
                               unsigned indent) {
    std::vector<Access> sorted = accesses;
    std::sort(sorted.begin(), sorted.end(), [](const Access &a, const Access &b) {
      return std::tie(a.name, a.record, a.role, a.location.file, a.location.line,
                      a.location.column) <
             std::tie(b.name, b.record, b.role, b.location.file, b.location.line,
                      b.location.column);
    });
    out << "[";
    bool first = true;
    for (const auto &access : sorted) {
      if (!first)
        out << ",";
      first = false;
      out << "{\"name\":";
      quoted(out, access.name);
      out << ",\"type\":";
      quoted(out, access.type);
      out << ",\"record\":";
      quoted(out, access.record);
      out << ",\"role\":";
      quoted(out, access.role);
      out << ",\"context\":";
      quoted(out, access.context);
      out << ",\"location\":";
      writeLocation(out, access.location, 0);
      out << "}";
    }
    out << "]";
  }

  static void writeFunction(std::ostream &out, const FunctionFact &fact,
                            unsigned indent) {
    writeIndent(out, indent);
    out << "{\"clang_usr\":";
    quoted(out, fact.usr);
    out << ",\"name\":";
    quoted(out, fact.name);
    out << ",\"qualified_name\":";
    quoted(out, fact.qualified_name);
    out << ",\"source_file\":";
    quoted(out, fact.location.file);
    out << ",\"line\":" << fact.location.line << ",\"column\":"
        << fact.location.column << ",\"return_type\":";
    quoted(out, fact.return_type);
    out << ",\"is_static\":" << (fact.is_static ? "true" : "false");
    out << ",\"parameters\":[";
    for (size_t i = 0; i < fact.parameters.size(); ++i) {
      if (i)
        out << ",";
      const auto &param = fact.parameters[i];
      out << "{\"name\":";
      quoted(out, std::get<0>(param));
      out << ",\"type\":";
      quoted(out, std::get<1>(param));
      out << ",\"pointer\":" << (std::get<2>(param) ? "true" : "false")
          << ",\"pointee_const\":"
          << (std::get<3>(param) ? "true" : "false") << "}";
    }
    out << "]";
    auto writeRefs = [&out](const char *key, const std::map<std::string, std::string> &refs) {
      out << ",\"" << key << "\":[";
      bool first = true;
      for (const auto &ref : refs) {
        if (!first)
          out << ",";
        first = false;
        out << "{\"clang_usr\":";
        quoted(out, ref.first);
        out << ",\"name\":";
        quoted(out, ref.second);
        out << "}";
      }
      out << "]";
    };
    writeRefs("callers", fact.callers);
    writeRefs("callees", fact.callees);
    out << ",\"globals_read\":";
    writeAccessArray(out, fact.globals_read, 0);
    out << ",\"globals_write\":";
    writeAccessArray(out, fact.globals_write, 0);
    out << ",\"fields_read\":";
    writeAccessArray(out, fact.fields_read, 0);
    out << ",\"fields_write\":";
    writeAccessArray(out, fact.fields_write, 0);
    out << ",\"pointer_parameters\":[";
    for (size_t i = 0; i < fact.pointer_parameters.size(); ++i) {
      if (i)
        out << ",";
      const auto &param = fact.pointer_parameters[i];
      out << "{\"name\":";
      quoted(out, param.name);
      out << ",\"type\":";
      quoted(out, param.type);
      out << ",\"pointee_const\":"
          << (param.pointee_const ? "true" : "false") << ",\"mode\":";
      quoted(out, param.mode);
      out << ",\"evidence\":[";
      for (size_t j = 0; j < param.evidence.size(); ++j) {
        if (j)
          out << ",";
        quoted(out, param.evidence[j]);
      }
      out << "]}";
    }
    out << "]";
    out << ",\"static_mutable_state\":[";
    for (size_t i = 0; i < fact.static_mutable_state.size(); ++i) {
      if (i)
        out << ",";
      quoted(out, fact.static_mutable_state[i]);
    }
    out << "]";
    out << ",\"effects\":{\"file_io\":" << (fact.file_io ? "true" : "false")
        << ",\"logging\":" << (fact.logging ? "true" : "false")
        << ",\"assert\":" << (fact.assertion ? "true" : "false")
        << ",\"malloc\":" << (fact.allocation ? "true" : "false")
        << ",\"indirect_call\":" << (fact.indirect_call ? "true" : "false")
        << "},\"calls\":[";
    std::vector<CallEffect> calls = fact.calls;
    std::sort(calls.begin(), calls.end(), [](const CallEffect &a, const CallEffect &b) {
      return std::tie(a.location.file, a.location.line, a.location.column, a.name) <
             std::tie(b.location.file, b.location.line, b.location.column, b.name);
    });
    for (size_t i = 0; i < calls.size(); ++i) {
      if (i)
        out << ",";
      const auto &call = calls[i];
      out << "{\"name\":";
      quoted(out, call.name);
      out << ",\"clang_usr\":";
      quoted(out, call.usr);
      out << ",\"category\":";
      quoted(out, call.category);
      out << ",\"direct\":" << (call.direct ? "true" : "false")
          << ",\"location\":";
      writeLocation(out, call.location, 0);
      out << "}";
    }
    out << "]";
    out << ",\"operators\":[";
    std::vector<OperatorFact> operators = fact.operators;
    std::sort(operators.begin(), operators.end(), [](const OperatorFact &a,
                                                     const OperatorFact &b) {
      return std::tie(a.spelling, a.location.file, a.location.line,
                      a.location.column, a.expression) <
             std::tie(b.spelling, b.location.file, b.location.line,
                      b.location.column, b.expression);
    });
    operators.erase(std::unique(operators.begin(), operators.end(),
                                [](const OperatorFact &a, const OperatorFact &b) {
                                  return a.spelling == b.spelling &&
                                         a.expression == b.expression &&
                                         a.location.file == b.location.file &&
                                         a.location.line == b.location.line &&
                                         a.location.column == b.location.column;
                                }),
                    operators.end());
    for (size_t i = 0; i < operators.size(); ++i) {
      if (i)
        out << ",";
      out << "{\"operator\":";
      quoted(out, operators[i].spelling);
      out << ",\"expression\":";
      quoted(out, operators[i].expression);
      out << ",\"location\":";
      writeLocation(out, operators[i].location, 0);
      out << "}";
    }
    out << "]";
    out << ",\"loop_count\":" << fact.loops.size() << ",\"loops\":[";
    std::vector<LoopFact> loops = fact.loops;
    std::sort(loops.begin(), loops.end(), [](const LoopFact &a, const LoopFact &b) {
      return std::tie(a.location.file, a.location.line, a.location.column, a.kind) <
             std::tie(b.location.file, b.location.line, b.location.column, b.kind);
    });
    for (size_t i = 0; i < loops.size(); ++i) {
      if (i)
        out << ",";
      const auto &loop = loops[i];
      out << "{\"kind\":";
      quoted(out, loop.kind);
      out << ",\"condition\":";
      quoted(out, loop.condition);
      out << ",\"increment\":";
      quoted(out, loop.increment);
      out << ",\"proof\":";
      quoted(out, loop.proof);
      out << ",\"has_fixed_trip_count\":"
          << (loop.has_fixed_trip_count ? "true" : "false");
      out << ",\"fixed_trip_count\":";
      if (loop.has_fixed_trip_count)
        out << loop.fixed_trip_count;
      else
        out << "null";
      out << ",\"trip_count_cases\":[";
      for (size_t j = 0; j < loop.trip_count_cases.size(); ++j) {
        if (j)
          out << ",";
        out << "{\"condition\":";
        quoted(out, loop.trip_count_cases[j].first);
        out << ",\"count\":" << loop.trip_count_cases[j].second << "}";
      }
      out << "],\"iteration_dependency\":";
      quoted(out, loop.dependency_status);
      out << ",\"dependency_locations\":[";
      for (size_t j = 0; j < loop.dependency_locations.size(); ++j) {
        if (j)
          out << ",";
        quoted(out, loop.dependency_locations[j]);
      }
      out << "],\"location\":";
      writeLocation(out, loop.location, 0);
      out << "}";
    }
    out << "],\"return_dependencies\":[";
    std::vector<Dependency> dependencies = fact.return_dependencies;
    std::sort(dependencies.begin(), dependencies.end(), [](const Dependency &a,
                                                           const Dependency &b) {
      return std::tie(a.kind, a.name, a.location.file, a.location.line,
                      a.location.column) <
             std::tie(b.kind, b.name, b.location.file, b.location.line,
                      b.location.column);
    });
    for (size_t i = 0; i < dependencies.size(); ++i) {
      if (i)
        out << ",";
      const auto &dep = dependencies[i];
      out << "{\"kind\":";
      quoted(out, dep.kind);
      out << ",\"name\":";
      quoted(out, dep.name);
      out << ",\"location\":";
      writeLocation(out, dep.location, 0);
      out << "}";
    }
    out << "],\"unknown_facts\":[";
    for (auto iter = fact.unknown_facts.begin(); iter != fact.unknown_facts.end();
         ++iter) {
      if (iter != fact.unknown_facts.begin())
        out << ",";
      quoted(out, *iter);
    }
    out << "]}";
  }

  static void writeGlobal(std::ostream &out, const GlobalDeclFact &fact,
                          unsigned indent) {
    writeIndent(out, indent);
    out << "{\"clang_usr\":";
    quoted(out, fact.usr);
    out << ",\"name\":";
    quoted(out, fact.name);
    out << ",\"type\":";
    quoted(out, fact.type);
    out << ",\"source_file\":";
    quoted(out, fact.location.file);
    out << ",\"line\":" << fact.location.line << ",\"column\":"
        << fact.location.column << ",\"const\":"
        << (fact.is_const ? "true" : "false") << ",\"static\":"
        << (fact.is_static ? "true" : "false") << ",\"is_array\":"
        << (fact.is_array ? "true" : "false") << ",\"array_size\":"
        << (fact.is_array ? std::to_string(fact.array_size) : "null")
        << ",\"constant_values\":[";
    for (size_t i = 0; i < fact.constant_values.size(); ++i) {
      if (i)
        out << ",";
      out << fact.constant_values[i];
    }
    out << "]}";
  }

  std::string source_root;
  ASTContext *current_context = nullptr;
  MatchFinder finder;
  std::map<std::string, FunctionFact> functions;
  std::vector<Edge> edges;
  std::map<std::string, GlobalDeclFact> globals;
};

class FactAction : public ASTFrontendAction {
public:
  explicit FactAction(FactCollector &collector) : collector(collector) {}

  std::unique_ptr<ASTConsumer>
  CreateASTConsumer(CompilerInstance &, StringRef) override {
    return collector.newConsumer();
  }

private:
  FactCollector &collector;
};

class FactActionFactory : public FrontendActionFactory {
public:
  explicit FactActionFactory(FactCollector &collector) : collector(collector) {}

  std::unique_ptr<FrontendAction> create() override {
    return std::make_unique<FactAction>(collector);
  }

private:
  FactCollector &collector;
};

} // namespace

int main(int argc, const char **argv) {
  llvm::cl::HideUnrelatedOptions(Category);
  llvm::cl::ParseCommandLineOptions(argc, argv);
  std::string error;
  auto database = JSONCompilationDatabase::loadFromFile(
      Compdb, error, JSONCommandLineSyntax::AutoDetect);
  if (!database) {
    llvm::errs() << "cannot load compilation database: " << error << "\n";
    return 2;
  }
  std::vector<std::string> files = database->getAllFiles();
  std::sort(files.begin(), files.end());
  files.erase(std::unique(files.begin(), files.end()), files.end());
  if (files.empty()) {
    llvm::errs() << "compilation database contains no files\n";
    return 3;
  }

  FactCollector collector(SourceRoot);
  collector.registerMatchers();
  ClangTool tool(*database, files);
  FactActionFactory factory(collector);
  int result = tool.run(&factory);
  if (result != 0)
    return result;
  collector.writeJson(Output);
  return 0;
}
