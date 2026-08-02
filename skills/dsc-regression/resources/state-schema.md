# Durable state schema

The service stores all mutable state below `DSC_REGRESSION_ROOT`:

```text
queue/pending/<job-id>/{job.json,status.json}
queue/running/<job-id>/{job.json,status.json,heartbeat.json,.claim/}
queue/{done,failed}/<job-id>/{job.json,status.json,heartbeat.json}
runs/<run-id>/{run.json,strategy.jsonl,report.json,scale-plan.json}
runs/<run-id>/functions/<contract-id>/{plan.json,receipt.json,traceability.json,accepted/}
cache/flow/<run-id>/{flow-receipt.json,flow.log,repo/}
dashboard/{index.html,latest.json}
```

`status.json` must contain `status`, `stage`, `progress`, `elapsed_seconds`,
`last_error`, `run_id`, and `contract_id`. A running `heartbeat.json` must
also contain `host`, `pid`, and `updated_at`. Queue transitions are:

```text
pending --claim mkdir + rename--> running --PASS--> done
pending --claim mkdir + rename--> running --failure--> failed
stale running --recovery lock + rename--> pending
```

Write JSON with a same-directory temporary file and `os.replace`. Do not add a
database or mutate queue state in place without an atomic replacement.
