#!/usr/bin/env bash
# Reproducible focused DSC 1.2a C-model analysis.
set -u

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_DIR="$SCRIPT_DIR"
SOURCE_DIR="${DSC_SOURCE_DIR:-$REPO_DIR/DSC_model_20210623/source}"
OUTPUT_DIR="$SCRIPT_DIR"
TARGET_PROFILE="$SCRIPT_DIR/analysis-profile.json"
PYTHON="${PYTHON:-python3}"
TIMEOUT_SECONDS="${DSC_ANALYSIS_TIMEOUT_SECONDS:-300}"
CLANGXX="${CLANGXX:-$(command -v clang++ 2>/dev/null || true)}"
CLANG="${CLANG:-$(command -v clang 2>/dev/null || true)}"
FRAMA_C="${FRAMA_C:-$(command -v frama-c 2>/dev/null || true)}"
LLVM_CONFIG="${LLVM_CONFIG:-$(command -v llvm-config 2>/dev/null || true)}"
CMAKE="${CMAKE:-$(command -v cmake 2>/dev/null || true)}"
SYSROOT="${DSC_SYSROOT:-}"
if [ -z "$SYSROOT" ] && command -v xcrun >/dev/null 2>&1; then
  SYSROOT="$(xcrun --show-sdk-path 2>/dev/null || true)"
fi

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/dsc12a-analysis.XXXXXX")"
cleanup() {
  rm -rf -- "$WORK_DIR"
}
trap cleanup EXIT

CLANG_VERSION="UNKNOWN"
FRAMA_VERSION="UNKNOWN"
SOURCE_REVISION="UNKNOWN"
FAILURE_REASON=""

if [ -n "$CLANG" ]; then
  CLANG_VERSION="$($CLANG --version 2>/dev/null | head -1 || true)"
fi
if [ -n "$FRAMA_C" ]; then
  FRAMA_VERSION="$($FRAMA_C -version 2>/dev/null | head -1 || true)"
fi
if [ -d "$(dirname -- "$SOURCE_DIR")" ]; then
  SOURCE_REVISION="$(git -C "$(dirname -- "$SOURCE_DIR")" rev-parse HEAD 2>/dev/null || true)"
  [ -n "$SOURCE_REVISION" ] || SOURCE_REVISION="UNKNOWN"
fi

fail() {
  FAILURE_REASON="$1"
  return 1
}

clear_generated_outputs() {
  rm -f -- \
    "$OUTPUT_DIR/summary.json" \
    "$OUTPUT_DIR/facts/compile_commands.json" \
    "$OUTPUT_DIR/facts/compile-check.json" \
    "$OUTPUT_DIR/facts/discovered-functions.json" \
    "$OUTPUT_DIR/facts/functions.json" \
    "$OUTPUT_DIR/facts/callgraph.json" \
    "$OUTPUT_DIR/facts/field-access.json" \
    "$OUTPUT_DIR/facts/loops.json" \
    "$OUTPUT_DIR/facts/value-ranges.json" \
    "$OUTPUT_DIR/facts/dependencies.json" \
    "$OUTPUT_DIR/reports/function-summary.md" \
    "$OUTPUT_DIR/reports/field-summary.md" \
    "$OUTPUT_DIR/reports/candidate-functions.md" \
    "$OUTPUT_DIR/reports/unresolved.md"
}

run_once() {
  local attempt_dir="$1"
  local raw_json="$attempt_dir/clang-facts.json"
  local frama_dir="$attempt_dir/frama"
  local before_hash="$attempt_dir/source-before.json"
  local after_hash="$attempt_dir/source-after.json"
  if ! mkdir -p "$attempt_dir" "$frama_dir" "$OUTPUT_DIR/facts" "$OUTPUT_DIR/reports"; then
    fail "INFRASTRUCTURE_FAILURE: disk full or analysis output directory is not writable"
    return 1
  fi

  if [ ! -d "$SOURCE_DIR" ]; then
    fail "INFRASTRUCTURE_FAILURE: DSC source/submodule does not exist: $SOURCE_DIR"
    return 1
  fi
  if ! find "$SOURCE_DIR" -type f -name '*.c' -print -quit | grep -q .; then
    fail "INFRASTRUCTURE_FAILURE: DSC source contains no C files: $SOURCE_DIR"
    return 1
  fi
  if [ -z "$CLANG" ] || [ -z "$CLANGXX" ]; then
    fail "INFRASTRUCTURE_FAILURE: Clang is not installed"
    return 1
  fi
  if [ -z "$FRAMA_C" ]; then
    fail "INFRASTRUCTURE_FAILURE: Frama-C is not installed"
    return 1
  fi
  if [ -z "$PYTHON" ] || ! command -v "$PYTHON" >/dev/null 2>&1; then
    fail "INFRASTRUCTURE_FAILURE: Python runtime is not installed"
    return 1
  fi

  local compdb_args=(
    --source-dir "$SOURCE_DIR"
    --output "$OUTPUT_DIR/facts/compile_commands.json"
    --compiler "$CLANG"
  )
  if [ -n "$SYSROOT" ]; then
    compdb_args+=(--sysroot "$SYSROOT")
  fi
  if ! "$PYTHON" "$SCRIPT_DIR/tools/generate_compile_commands.py" "${compdb_args[@]}"; then
    fail "compile_commands.json generation failed"
    return 1
  fi
  if ! "$PYTHON" "$SCRIPT_DIR/tools/hash_source.py" "$SOURCE_DIR" >"$before_hash"; then
    fail "source hash manifest generation failed"
    return 1
  fi

  local compile_check_raw="$attempt_dir/compile-check.json"
  if ! "$PYTHON" "$SCRIPT_DIR/tools/check_compile_commands.py" \
      --compile-commands "$OUTPUT_DIR/facts/compile_commands.json" \
      --output "$compile_check_raw" \
      --timeout "$TIMEOUT_SECONDS"; then
    fail "INFRASTRUCTURE_FAILURE: C compiler front-end check failed; see $compile_check_raw"
    return 1
  fi

  if [ -z "$LLVM_CONFIG" ] || ! command -v "$LLVM_CONFIG" >/dev/null 2>&1; then
    fail "INFRASTRUCTURE_FAILURE: Clang LibTooling/AST Matchers development package is not installed (llvm-config missing)"
    return 1
  fi
  if [ -z "$CMAKE" ] || ! command -v "$CMAKE" >/dev/null 2>&1; then
    fail "INFRASTRUCTURE_FAILURE: CMake is required to build the LibTooling collector"
    return 1
  fi

  local llvm_dir=""
  local clang_dir=""
  llvm_dir="$($LLVM_CONFIG --cmakedir 2>/dev/null || true)"
  if [ -z "$llvm_dir" ] || [ ! -d "$llvm_dir" ]; then
    fail "INFRASTRUCTURE_FAILURE: LLVM CMake package is unavailable for LibTooling"
    return 1
  fi
  clang_dir="$(CDPATH= cd -- "$llvm_dir/../clang" 2>/dev/null && pwd || true)"
  [ -d "$clang_dir" ] || clang_dir="$llvm_dir"
  if ! "$CMAKE" -S "$SCRIPT_DIR/tools" -B "$attempt_dir/build" \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_CXX_COMPILER="$CLANGXX" \
      -DLLVM_DIR="$llvm_dir" \
      -DClang_DIR="$clang_dir" >"$attempt_dir/cmake-configure.log" 2>&1; then
    fail "INFRASTRUCTURE_FAILURE: Clang LibTooling/AST Matchers build failed; see $attempt_dir/cmake-configure.log"
    return 1
  fi
  if ! "$CMAKE" --build "$attempt_dir/build" --target dsc-clang-facts \
      >"$attempt_dir/cmake-build.log" 2>&1; then
    fail "INFRASTRUCTURE_FAILURE: Clang LibTooling/AST Matchers build failed; see $attempt_dir/cmake-build.log"
    return 1
  fi
  if ! "$PYTHON" "$SCRIPT_DIR/tools/run_command.py" \
      --timeout "$TIMEOUT_SECONDS" \
      --log "$attempt_dir/clang-facts.log" -- \
      "$attempt_dir/build/dsc-clang-facts" \
      --compdb "$OUTPUT_DIR/facts/compile_commands.json" \
      --output "$raw_json" \
      --source-root "$SOURCE_DIR"; then
    fail "INFRASTRUCTURE_FAILURE: Clang AST analysis failed or timed out; see $attempt_dir/clang-facts.log"
    return 1
  fi

  if ! "$PYTHON" "$SCRIPT_DIR/tools/run_frama.py" \
      --frama-c "$FRAMA_C" \
      --compile-commands "$OUTPUT_DIR/facts/compile_commands.json" \
      --source-dir "$SOURCE_DIR" \
      --output-dir "$frama_dir" \
      --timeout "$TIMEOUT_SECONDS" \
      --clang-facts "$raw_json" \
      --target-profile "$TARGET_PROFILE"; then
    fail "INFRASTRUCTURE_FAILURE: focused Frama-C Eva/From analysis failed or timed out; see $frama_dir"
    return 1
  fi

  if ! "$PYTHON" "$SCRIPT_DIR/tools/assemble_facts.py" \
      --raw "$raw_json" \
      --source-dir "$SOURCE_DIR" \
      --output-dir "$OUTPUT_DIR" \
      --source-revision "$SOURCE_REVISION" \
      --clang-version "$CLANG_VERSION" \
      --frama-c-version "$FRAMA_VERSION" \
      --compile-commands "$OUTPUT_DIR/facts/compile_commands.json" \
      --compile-check "$compile_check_raw" \
      --target-profile "$TARGET_PROFILE" \
      --frama-output-dir "$frama_dir" \
      --analysis-command "generate compile_commands.json from public Makefile flags" \
      --analysis-command "clang -fsyntax-only over every compile_commands.json entry" \
      --analysis-command "clang LibTooling AST Matchers over facts/compile_commands.json" \
      --analysis-command "frama-c -eva -main PROFILE_TARGET (profile-selected targets)" \
      --analysis-command "frama-c -deps -calldeps -main PROFILE_TARGET (profile-selected targets)"; then
    fail "fact assembly failed"
    return 1
  fi

  if ! "$PYTHON" "$SCRIPT_DIR/tools/hash_source.py" "$SOURCE_DIR" >"$after_hash"; then
    fail "source hash manifest generation failed after analysis"
    return 1
  fi
  if ! cmp -s "$before_hash" "$after_hash"; then
    fail "INFRASTRUCTURE_FAILURE: upstream DSC source changed during analysis"
    return 1
  fi
  return 0
}

clear_generated_outputs
mkdir -p "$OUTPUT_DIR/facts" "$OUTPUT_DIR/reports"

success=0
for attempt in 1 2; do
  FAILURE_REASON=""
  if run_once "$WORK_DIR/attempt-$attempt"; then
    success=1
    break
  fi
done

if [ "$success" -ne 1 ]; then
  clear_generated_outputs
  "$PYTHON" "$SCRIPT_DIR/tools/write_failure.py" \
    --output-dir "$OUTPUT_DIR" \
    --source-dir "$SOURCE_DIR" \
    --reason "$FAILURE_REASON" \
    --clang-version "$CLANG_VERSION" \
    --frama-c-version "$FRAMA_VERSION" \
    --analysis-command "deterministic retry count: 2" \
    --analysis-command "no LLM or fallback parser invoked"
  echo "$FAILURE_REASON" >&2
  exit 1
fi

echo "DSC 1.2a focused C analysis complete: $OUTPUT_DIR/summary.json"
