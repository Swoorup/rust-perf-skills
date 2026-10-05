# Review evidence and decisions

Read the entire original skill repository: README, SKILL and all six references.
There were no scripts, tests, CI/config or repository agent instructions. The
initial working tree was clean. Primary packaging/eval sources and Apple material
checked are recorded in the skill's sources reference.

## Confirmed issues and changes

- Root directory `rust-perf-skills` disagreed with skill name
  `rust-ui-performance`; moved the unchanged identity into `skills/` and added
  a minimal skill-only plugin manifest. README installs the nested folder.
- Benchmark provenance/statistics and anchor checks were manual. Added three
  Python standard-library scripts with explicit unavailable/error outcomes.
- Snapshot date/line anchors had no source repository/SHA. Removed line numbers,
  marked provenance unknown, supplied symbol rediscovery and a conservative
  manifest check. No source revision was invented.
- macOS routing only named Time Profiler. Added documented CPU Profiler,
  CPU Counters and Processor Trace distinctions/support/fallback, while retaining
  Time Profiler and Metal/Allocations routes for their appropriate questions.
- Formal reporting applied to speculation. Added short falsifiable hypotheses
  and distinct evidence states; final findings retain reviewable measurements.
- No skill evals existed. Added 15 positive/adversarial behavior cases in the
  Agent Skills recommended JSON format, a grading procedure, and tooling tests.

## Deliberately retained or omitted

Retained the optimization hierarchy, Rux ownership/rendering knowledge and its
measurement-boundary warnings. Most requested low-level topics were already
covered well; added profiler routing and RwLock-specific questions rather than
repeating a tuning checklist. Did not prescribe arena/SIMD/allocator changes,
split generic/project knowledge into multiple skills, globally replace Time
Profiler, add nightly Rust, or invent statistical significance. Optional UI agent
metadata and a custom agent-eval framework add no necessary capability here.

## Validation

- 11 unittest cases pass: raw statistics/tails, malformed and incompatible data,
  zero baseline, CLI failure, provenance/hash/secret exclusion, anchor identity,
  revision, dirty state, missing symbols/paths and checkout escape.
- Repository validator passes: local Markdown links, name/directory, plugin skill
  path, 15 eval schemas/resources. Official `skills-ref validate` passes.
- OpenAI skill-installer validation/copy helpers successfully installed the new
  folder in `/tmp`, with no rename; copied skill passes the official validator.
  Remote installation awaits these changes being published to the repository.
- Capture and comparison CLIs exercised. Bundled anchor verification rejects
  this skill checkout as expected: it is not a verified Rux source snapshot.
- `git diff --check` passes. All 29 Markdown external links attempted: 11 reachable;
  18 blocked by network policy, not established broken. Results captured at
  `/tmp/rust-perf-link-audit.json` in this instance. Local links all resolve.

## Limits and environment state

This is a Python/Git skill-authoring environment; no Rust application build or
service is required. Python/Git and the current-instance tooling checks work.
Network additions for Apple/OpenAI/Agent Skills documentation were saved in the
cloud draft; no install/start scripts are necessary for the standard-library
workflow. Saving a draft does not publish an environment.

Behavioral agent evals are specified but not executed/graded: no behavioral pass
rate is claimed. Run them in fresh sessions with real or disposable target
fixtures, comparing the previous skill. The target Rux source identity/revision
and original audit artifacts are unavailable. macOS Instruments runtime checks
need supported Apple hardware. Direct OpenAI web documentation remained blocked;
current primary GitHub sources were used. Plugin marketplace registration/client
discovery and fresh cloud-task restoration were not exercised.
