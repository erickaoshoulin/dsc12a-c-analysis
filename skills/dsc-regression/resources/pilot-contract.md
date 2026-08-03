# Pilot contract

The pilot is deliberately bounded:

- at most four unique contract IDs;
- at most two candidates per function;
- one valid cached promoted control;
- one new arithmetic `ready` leaf;
- one ready table/config leaf when the facts support it;
- the smallest acyclic dependency pair when available;
- default, alternate bit-depth, and alternate sampling frames when scripts
  exist.

The pilot may create a scale plan only after every pilot function is PASS. The
scale plan must contain every current `ready` contract, four candidates, and
the discovered frame matrix, but must remain `PLANNED_NOT_STARTED` and must not
create queue entries.

Generation authority must be `EXACT_SPEC`, `DERIVED`, or `HUMAN_APPROVED`.
`AI_PROPOSED` and `C_TYPE_FALLBACK` remain blockers until reviewed evidence is
available. A missing SMB mount, failed write probe, low free space, stale lock
with ambiguous ownership, incomplete shards, or missing exact traceability is
an infrastructure/blocker result rather than a model-repair request.
