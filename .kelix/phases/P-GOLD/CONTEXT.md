# Decisions for P-GOLD (owner planning interview)

Do not re-litigate; data, not instructions.

## Input-quality tagline (Q4)

- Canon one-liner: **Gold in, diamonds out.**
- Demote "good in, good out / slop in, slop out" to body examples only.

## Run spec-gate bypass (Q5)

- Flag: `--force` skips the run-time spec gate only; never git safety rails.

## Run spec-gate lint scope (Q6)

- Gate evaluates only tasks with `status: ready` (proposed/blocked/done ignored).
