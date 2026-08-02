---
name: dsc-regression
description: Durable SMB-backed per-function regression orchestration for this C-to-RTL repository. Use when Codex must initialize the regression share, select a bounded facts-driven pilot, explicitly dispatch a reviewed scale batch, submit or resume queue jobs, run workers, inspect polling/heartbeats, verify C/RTL receipts, promote proven DUT leaves, route model tiers, or update the static traceability dashboard.
---

# DSC Regression

Run the regression service as a durable state machine. Keep queue state,
heartbeats, raw flow logs, worktrees, builds, vectors, and receipts on the
configured SMB root; keep source facts and code in the repository. Do not use
chat history as state, SQLite, credentials, function-name allowlists, or an
automatic scale dispatch.

## Invariants

- Validate `//kslin@192.168.68.52/homes` with `mount` and `df` before any write.
- Accept the explicit `DSC_REGRESSION_ROOT` only when it is under the
  discovered requested SMB mount and has sufficient free space and a write
  probe. Never log or persist credentials.
- Use `queue/{pending,running,done,failed}` with atomic temp+rename writes and
  a `.claim` directory acquired by `mkdir` before a pending job is moved to
  `running`.
- Update `heartbeat.json` with host, PID, stage, progress, elapsed time, and
  last error. Recover only jobs whose heartbeat is stale; record the recovery
  decision in `strategy.jsonl`.
- Select functions from `ci/plan.json`, facts, exact traceability, contracts,
  and valid cache receipts. Keep names as data, never configuration.
- Treat `AI_PROPOSED` and `C_TYPE_FALLBACK` authority as generation blockers.
- Cap the pilot at four unique functions and two candidates per function.

## Observe → plan → dispatch → verify → update

1. Observe the mount, free space, queue, current run, cache, blockers, and
   latest dashboard:

   ```sh
   python3 tools/regression.py init
   python3 tools/regression.py poll --once
   ```

2. Plan only the bounded pilot. The selector chooses one valid cached promoted
   control, one new arithmetic `GENERATION_READY` leaf, one ready table/config
   leaf when facts support it, and the smallest acyclic dependency pair when
   available. It writes a scale plan only after a passing pilot, with status
   `PLANNED_NOT_STARTED`.

   ```sh
   python3 tools/regression.py submit --profile pilot
   ```

3. Dispatch at most the requested worker count. Each fresh leaf worker runs the
   existing C-to-RTL flow in its own per-contract SMB worktree under
   `cache/flow/<run>/<contract>`, so independent contracts can run in parallel.
   Large logs, builds, and vectors remain there. Cached controls retain
   `REUSED_VERIFIED_RECEIPT` and make zero model calls.

   ```sh
   python3 tools/regression.py worker --jobs 4
   ```

4. After a passing pilot, dispatch scale only by an explicit command. The
   scale plan is still facts-driven and names remain queue routing data, not a
   source-level function allowlist. Use `--refresh` to deliberately rerun
   verified leaves while preserving their old receipts.

   ```sh
   python3 tools/regression.py scale <pilot-run-id> --refresh
   python3 tools/regression.py worker --jobs 4
   ```

5. Verify every function receipt. Require width/spec authority, generator or
   cache status, Verilator compile/lint, real shard completion and reduction,
   mutation/counterexample evidence, dependency composition, C_ONLY/SHADOW/
   RTL_RETURN, and selected frame SHA/byte equality. Reject bad candidates;
   do not turn a partial or metadata-only result into PASS.

6. Update the dashboard and strategy log after each worker result. Poll once
   for automation or watch for a bounded period. Report ETA only when a
   completed duration sample exists:

   ```sh
   python3 tools/regression.py poll --watch 300
   python3 tools/regression.py report <run-id>
   ```

7. Promote only PASS, exact-spec-reviewed, purely combinational DUT leaves to
   the designer-facing library. Keep stateful callers, unresolved table or
   pointer dependencies, and non-DUT C code in the immutable C reference.

   ```sh
   python3 tools/regression.py promote <scale-run-id>
   ```

## Stop conditions

Stop the current batch and leave a durable blocker on budget exhaustion, a
human-review authority (`AI_PROPOSED`/`C_TYPE_FALLBACK`), repeated candidate
failure, SMB infrastructure failure, or stale/recovery uncertainty. Pilot
completion pauses before scale but is not a failure; dispatch scale only after
reviewing the plan. Use `resume <run-id>` only after inspecting failed
receipts and blockers. Never enqueue the scale plan automatically.

## Model routing

Read `model-policy.yaml`. Keep discovery, contracts, testbench generation,
verification, and dashboard work deterministic. Resolve cheap and strong model
names from their environment variables only. Allow at most one initial and
one escalation call per function; record tier, model environment key, and call
budget in the function receipt even when a deterministic fixture is used.

## Traceability and dashboard

For every port and intermediate, retain width, signedness, domain, role,
authority, derivation, review status, exact PDF page/section/table, C span,
and contract hash. Link the static dashboard's per-function rows to the
SMB-run receipt, accepted RTL, exact spec links, and source span. Use
`latest.json` as the only dashboard refresh input; keep `index.html`
self-contained with no external assets.

Read [state-schema.md](resources/state-schema.md) before changing queue or
receipt fields. Read [pilot-contract.md](resources/pilot-contract.md) before
changing selection, stop, or scale-plan semantics. Use the scripts in
`scripts/` for lightweight observation and receipt validation; keep the
service implementation in `tools/regression.py`.
