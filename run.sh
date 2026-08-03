#!/usr/bin/env bash
# Reproducible auto-discovery DSC 1.2a C-model analysis.
set -u

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_DIR="$SCRIPT_DIR"
OUTPUT_DIR="$SCRIPT_DIR"
PYTHON_REQUESTED="${PYTHON:-python3}"
CLANGXX_REQUESTED="${CLANGXX:-clang++}"
CLANG_REQUESTED="${CLANG:-clang}"
FRAMA_C_REQUESTED="${FRAMA_C:-frama-c}"
LLVM_CONFIG_REQUESTED="${LLVM_CONFIG:-llvm-config}"
CMAKE_REQUESTED="${CMAKE:-cmake}"
PYTHON="$PYTHON_REQUESTED"
TIMEOUT_SECONDS="${DSC_ANALYSIS_TIMEOUT_SECONDS:-600}"
BUILD_TIMEOUT_SECONDS="${DSC_BUILD_TIMEOUT_SECONDS:-$TIMEOUT_SECONDS}"
TOP_N="${DSC_ANALYSIS_TOP_N:-10}"
resolve_executable() {
  local name="$1"
  shift
  local candidate
  for candidate in "$@"; do
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  candidate="$(command -v "$name" 2>/dev/null || true)"
  if [ -n "$candidate" ]; then
    printf '%s\n' "$candidate"
    return 0
  fi
  if [ "$name" = "frama-c" ]; then
    if [ -n "${OPAM_SWITCH_PREFIX:-}" ]; then
      for candidate in \
        "$OPAM_SWITCH_PREFIX/bin/$name" \
        "$OPAM_SWITCH_PREFIX/_opam/bin/$name"; do
        if [ -x "$candidate" ]; then
          printf '%s\n' "$candidate"
          return 0
        fi
      done
    fi
    candidate="$(command -v opam 2>/dev/null || true)"
    if [ -z "$candidate" ]; then
      for candidate in /opt/homebrew/bin/opam /usr/local/bin/opam; do
        if [ -x "$candidate" ]; then
          break
        fi
      done
    fi
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
      local opam_tool
      opam_tool="$($candidate exec -- which "$name" 2>/dev/null | tail -n 1 || true)"
      if [ -x "$opam_tool" ]; then
        printf '%s\n' "$opam_tool"
        return 0
      fi
      local switch_name
      while IFS= read -r switch_name; do
        [ -n "$switch_name" ] || continue
        opam_tool="$($candidate exec --switch="$switch_name" -- which "$name" 2>/dev/null | tail -n 1 || true)"
        if [ -x "$opam_tool" ]; then
          printf '%s\n' "$opam_tool"
          return 0
        fi
      done <<EOF
$($candidate switch list --short 2>/dev/null || true)
EOF
    fi
  fi
  return 1
}

CLANGXX="${CLANGXX:-$(resolve_executable clang++ /opt/homebrew/opt/llvm/bin/clang++ /usr/local/opt/llvm/bin/clang++ || true)}"
CLANG="${CLANG:-$(resolve_executable clang || true)}"
FRAMA_C="${FRAMA_C:-$(resolve_executable frama-c || true)}"
LLVM_CONFIG="${LLVM_CONFIG:-$(resolve_executable llvm-config /opt/homebrew/opt/llvm/bin/llvm-config /usr/local/opt/llvm/bin/llvm-config || true)}"
CMAKE="${CMAKE:-$(resolve_executable cmake || true)}"
SYSROOT="${DSC_SYSROOT:-}"
if [ -z "$SYSROOT" ] && command -v xcrun >/dev/null 2>&1; then
  SYSROOT="$(xcrun --show-sdk-path 2>/dev/null || true)"
fi

MANIFEST="$OUTPUT_DIR/spec/manifest.json"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/dsc12a-analysis.XXXXXX")"
cleanup() {
  rm -rf -- "$WORK_DIR"
}
trap cleanup EXIT

CLANG_VERSION="UNKNOWN"
FRAMA_VERSION="UNKNOWN"
SOURCE_REVISION="UNKNOWN"
SOURCE_DIR="${DSC_SOURCE_DIR:-$REPO_DIR/DSC_model_20210623/source}"
MODEL_ROOT=""
FAILURE_REASON=""

if [ -n "$CLANG" ]; then
  CLANG_VERSION="$($CLANG --version 2>/dev/null | head -1 || true)"
fi
if [ -n "$FRAMA_C" ]; then
  FRAMA_VERSION="$($FRAMA_C -version 2>/dev/null | head -1 || true)"
fi

fail() {
  FAILURE_REASON="$1"
  return 1
}

refresh_dashboard() {
  if ! "$PYTHON" "$SCRIPT_DIR/tools/dashboard.py" build --run latest >/dev/null; then
    echo "INFRASTRUCTURE_FAILURE: dashboard/report refresh failed" >&2
    return 1
  fi
  if ! "$PYTHON" "$SCRIPT_DIR/tools/dashboard.py" check >/dev/null; then
    echo "INFRASTRUCTURE_FAILURE: dashboard/report check failed" >&2
    return 1
  fi
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
    "$OUTPUT_DIR/facts/comments.json" \
    "$OUTPUT_DIR/facts/candidates.json" \
    "$OUTPUT_DIR/facts/build-receipt.json" \
    "$OUTPUT_DIR/spec/anchors.json" \
    "$OUTPUT_DIR/traceability/links.proposed.yaml" \
    "$OUTPUT_DIR/traceability/traceability.json" \
    "$OUTPUT_DIR/reports/function-summary.md" \
    "$OUTPUT_DIR/reports/field-summary.md" \
    "$OUTPUT_DIR/reports/candidate-functions.md" \
    "$OUTPUT_DIR/reports/candidates.md" \
    "$OUTPUT_DIR/reports/spec-to-code.md" \
    "$OUTPUT_DIR/reports/code-to-spec.md" \
    "$OUTPUT_DIR/reports/orphan-triage.md" \
    "$OUTPUT_DIR/reports/orphans.md" \
    "$OUTPUT_DIR/reports/unresolved.md"
}

manifest_value() {
  "$PYTHON" - "$MANIFEST" "$1" <<'PY'
import json
import pathlib
import sys

manifest = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
key = sys.argv[2]
if key == "source_dir":
    value = manifest.get("source", {}).get("source_dir", "")
elif key == "model_root":
    value = manifest.get("source", {}).get("model_root", "")
elif key == "revision":
    value = manifest.get("source", {}).get("git", {}).get("commit", "UNKNOWN")
else:
    value = ""
print(value)
PY
}

run_once() {
  local attempt_dir="$1"
  local raw_json="$attempt_dir/clang-facts.json"
  local frama_dir="$attempt_dir/frama"
  local before_hash="$attempt_dir/source-before.json"
  local after_hash="$attempt_dir/source-after.json"
  if ! mkdir -p "$attempt_dir" "$frama_dir" "$OUTPUT_DIR/facts" "$OUTPUT_DIR/reports" "$OUTPUT_DIR/spec" "$OUTPUT_DIR/traceability"; then
    fail "INFRASTRUCTURE_FAILURE: disk full or analysis output directory is not writable"
    return 1
  fi

  if [ ! -d "$SOURCE_DIR" ]; then
    fail "INFRASTRUCTURE_FAILURE: discovered DSC source does not exist: $SOURCE_DIR"
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
    fail "INFRASTRUCTURE_FAILURE: compile_commands.json generation failed"
    return 1
  fi
  if ! "$PYTHON" "$SCRIPT_DIR/tools/hash_source.py" "$SOURCE_DIR" >"$before_hash"; then
    fail "INFRASTRUCTURE_FAILURE: source hash manifest generation failed"
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

  if ! "$PYTHON" "$SCRIPT_DIR/tools/rank_candidates.py" \
      --raw "$raw_json" \
      --build-receipt "$OUTPUT_DIR/build/build-receipt.json" \
      --output "$OUTPUT_DIR/facts/candidates.json" \
      --report "$OUTPUT_DIR/reports/candidates.md" \
      --top-n "$TOP_N"; then
    fail "INFRASTRUCTURE_FAILURE: auto-discovered candidate ranking failed"
    return 1
  fi

  if ! "$PYTHON" "$SCRIPT_DIR/tools/traceability.py" \
      --input-manifest "$MANIFEST" \
      --raw "$raw_json" \
      --candidates "$OUTPUT_DIR/facts/candidates.json" \
      --output-dir "$OUTPUT_DIR" \
      --reviewed "$OUTPUT_DIR/traceability/links.reviewed.yaml" \
      --library-manifest "$OUTPUT_DIR/library/manifest.json"; then
    fail "INFRASTRUCTURE_FAILURE: deterministic PDF/C traceability extraction failed"
    return 1
  fi

  if ! "$PYTHON" "$SCRIPT_DIR/tools/run_frama.py" \
      --frama-c "$FRAMA_C" \
      --compile-commands "$OUTPUT_DIR/facts/compile_commands.json" \
      --source-dir "$SOURCE_DIR" \
      --output-dir "$frama_dir" \
      --timeout "$TIMEOUT_SECONDS" \
      --candidates "$OUTPUT_DIR/facts/candidates.json" \
      --top-n "$TOP_N"; then
    fail "INFRASTRUCTURE_FAILURE: tool-ranked Frama-C Eva/From analysis failed or timed out; see $frama_dir"
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
      --input-manifest "$MANIFEST" \
      --build-receipt "$OUTPUT_DIR/build/build-receipt.json" \
      --candidates "$OUTPUT_DIR/facts/candidates.json" \
      --traceability "$OUTPUT_DIR/traceability/traceability.json" \
      --frama-output-dir "$frama_dir" \
      --analysis-command "discover local PDF and C model by metadata/source gates" \
      --analysis-command "make -j1 clean then make -j1 and run bittrue C smoke in an isolated copy" \
      --analysis-command "Clang LibTooling AST Matchers over every compile_commands.json entry" \
      --analysis-command "rank production/output-contributing bounded candidates without a function-name allowlist" \
      --analysis-command "Frama-C Eva and From on the top-ranked tool-selected candidates" \
      --analysis-command "deterministic PDF anchors and C model-note links; no LLM calls"; then
    fail "INFRASTRUCTURE_FAILURE: fact assembly failed"
    return 1
  fi

  if ! "$PYTHON" "$SCRIPT_DIR/tools/hash_source.py" "$SOURCE_DIR" >"$after_hash"; then
    fail "INFRASTRUCTURE_FAILURE: source hash manifest generation failed after analysis"
    return 1
  fi
  if ! cmp -s "$before_hash" "$after_hash"; then
    fail "INFRASTRUCTURE_FAILURE: upstream DSC source changed during analysis"
    return 1
  fi
  return 0
}

if [ -z "$PYTHON" ] || ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "INFRASTRUCTURE_FAILURE: Python runtime is not installed" >&2
  exit 1
fi
mkdir -p "$OUTPUT_DIR/spec" "$OUTPUT_DIR/facts" "$OUTPUT_DIR/reports" "$OUTPUT_DIR/traceability"

if ! "$PYTHON" "$SCRIPT_DIR/tools/discover_inputs.py" \
    --repo-root "$REPO_DIR" \
    --output "$MANIFEST" \
    --timeout "$TIMEOUT_SECONDS"; then
  echo "INFRASTRUCTURE_FAILURE: input discovery tool failed; see $MANIFEST" >&2
  exit 1
fi

DISCOVERY_STATUS="$("$PYTHON" - "$MANIFEST" <<'PY'
import json
import pathlib
import sys
print(json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")).get("status", "UNKNOWN"))
PY
)"
if [ "$DISCOVERY_STATUS" != "OK" ]; then
  echo "${DISCOVERY_STATUS:-INPUT_UNAVAILABLE}: local DSC PDF/C model gate did not pass; see $MANIFEST" >&2
  exit 1
fi
SOURCE_DIR="$("$PYTHON" - "$MANIFEST" <<'PY'
import json
import pathlib
import sys
print(json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")).get("source", {}).get("source_dir", ""))
PY
)"
MODEL_ROOT="$("$PYTHON" - "$MANIFEST" <<'PY'
import json
import pathlib
import sys
print(json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")).get("source", {}).get("model_root", ""))
PY
)"
SOURCE_REVISION="$("$PYTHON" - "$MANIFEST" <<'PY'
import json
import pathlib
import sys
print(json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")).get("source", {}).get("git", {}).get("commit", "UNKNOWN"))
PY
)"
if [ -z "$SOURCE_DIR" ] || [ -z "$MODEL_ROOT" ]; then
  echo "INFRASTRUCTURE_FAILURE: discovery manifest has no source/model path" >&2
  exit 1
fi

BUILD_LOG_DIR="$WORK_DIR/build-logs"
case "${DSC_REGRESSION_ROOT:-}" in
  /*)
    BUILD_LOG_DIR="$DSC_REGRESSION_ROOT/local/build-logs/$(date -u +%Y%m%dT%H%M%SZ)-$$"
    ;;
esac

if ! "$PYTHON" "$SCRIPT_DIR/tools/build_model.py" \
    --model-root "$MODEL_ROOT" \
    --output-dir "$OUTPUT_DIR/build" \
    --work-dir "$WORK_DIR/model-build" \
    --log-dir "$BUILD_LOG_DIR" \
    --timeout "$BUILD_TIMEOUT_SECONDS"; then
  echo "INFRASTRUCTURE_FAILURE: isolated C clean-build/smoke gate failed; see $OUTPUT_DIR/build/build-receipt.json" >&2
  exit 1
fi

PREFLIGHT_RECEIPT="$OUTPUT_DIR/build/analysis-preflight.json"
if ! "$PYTHON" "$SCRIPT_DIR/tools/analysis_preflight.py" \
    --output "$PREFLIGHT_RECEIPT" \
    --python "$PYTHON_REQUESTED" \
    --clang "$CLANG_REQUESTED" \
    --clang++ "$CLANGXX_REQUESTED" \
    --frama-c "$FRAMA_C_REQUESTED" \
    --llvm-config "$LLVM_CONFIG_REQUESTED" \
    --cmake "$CMAKE_REQUESTED"; then
  refresh_dashboard || true
  echo "INFRASTRUCTURE_FAILURE: required analysis tools unavailable; preserving prior generated receipts; see $PREFLIGHT_RECEIPT" >&2
  exit 1
fi

if [ ! -f "$OUTPUT_DIR/traceability/links.reviewed.yaml" ]; then
  cat >"$OUTPUT_DIR/traceability/links.reviewed.yaml" <<'EOF'
schema_version: 1
do_not_edit: false
# Human-edited reviewed links are intentionally kept separate from generated proposals.
links: []
EOF
fi

clear_generated_outputs

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

if ! "$PYTHON" "$SCRIPT_DIR/tools/run_coverage.py" \
    --model-root "$MODEL_ROOT" \
    --output-dir "$OUTPUT_DIR/coverage" \
    --work-dir "$WORK_DIR/coverage" \
    --timeout "$BUILD_TIMEOUT_SECONDS" \
    --coverage-scripts "${DSC_COVERAGE_SCRIPTS:-all}" \
    --functions "$OUTPUT_DIR/facts/functions.json" \
    --candidates "$OUTPUT_DIR/facts/candidates.json" \
    --build-receipt "$OUTPUT_DIR/build/build-receipt.json"; then
  echo "INFRASTRUCTURE_FAILURE: instrumented C coverage/smoke gate failed; see $OUTPUT_DIR/coverage/coverage-receipt.json" >&2
  exit 1
fi

if ! "$PYTHON" "$SCRIPT_DIR/tools/create_contracts.py" \
    --manifest "$MANIFEST" \
    --functions "$OUTPUT_DIR/facts/functions.json" \
    --candidates "$OUTPUT_DIR/facts/candidates.json" \
    --coverage "$OUTPUT_DIR/coverage/coverage.json" \
    --traceability "$OUTPUT_DIR/traceability/traceability.json" \
    --anchors "$OUTPUT_DIR/spec/anchors.json" \
    --output-dir "$OUTPUT_DIR/contracts" \
    --top-n "$TOP_N"; then
  echo "INFRASTRUCTURE_FAILURE: tool-selected contract generation failed" >&2
  exit 1
fi

if ! "$PYTHON" "$SCRIPT_DIR/tools/generate_slice.py" \
    --manifest "$MANIFEST" \
    --contracts "$OUTPUT_DIR/contracts" \
    --output-dir "$OUTPUT_DIR/verification" \
    --work-dir "$WORK_DIR/rtl-slice" \
    --timeout "$BUILD_TIMEOUT_SECONDS"; then
  echo "UNPROVED: Verilator/C-oracle RTL slice did not prove; see $OUTPUT_DIR/verification/verification-receipt.json" >&2
  exit 1
fi

if ! "$PYTHON" "$SCRIPT_DIR/tools/finalize_outputs.py" \
    --summary "$OUTPUT_DIR/summary.json" \
    --traceability "$OUTPUT_DIR/traceability/traceability.json" \
    --coverage "$OUTPUT_DIR/coverage/coverage.json" \
    --contracts "$OUTPUT_DIR/contracts" \
    --verification "$OUTPUT_DIR/verification/verification-receipt.json" \
    --build "$OUTPUT_DIR/build/build-receipt.json" \
    --output-report "$OUTPUT_DIR/reports/progress.md"; then
  echo "INFRASTRUCTURE_FAILURE: final progress/summary assembly failed" >&2
  exit 1
fi

echo "DSC 1.2a auto-discovery C analysis complete: $OUTPUT_DIR/summary.json"

if [ "${DSC_RUN_CICD:-0}" = "1" ]; then
  if [ -z "${DSC_CICD_GENERATOR_CMD:-}" ]; then
    echo "GENERATION_REQUIRED: set DSC_CICD_GENERATOR_CMD before running the generic migration agent" >&2
    exit 2
  fi
  if [ -z "${DSC_CICD_ARTIFACT_ROOT:-}" ]; then
    case "${DSC_REGRESSION_ROOT:-}" in
      /*) export DSC_CICD_ARTIFACT_ROOT="$DSC_REGRESSION_ROOT/local/cicd-artifacts/$(date -u +%Y%m%dT%H%M%SZ)-$$" ;;
    esac
  fi
  if ! "$PYTHON" "$SCRIPT_DIR/tools/cicd_agent.py" run; then
    echo "INFRASTRUCTURE_FAILURE: executable generic C-to-RTL CI/CD run failed; see $OUTPUT_DIR/reports/pipeline-summary.md" >&2
    exit 1
  fi
fi

if ! refresh_dashboard; then
  exit 1
fi
