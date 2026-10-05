# rust-perf-skills

Evidence-driven Rust UI performance engineering, with detailed Rux specialization.
Profile first, falsify hypotheses, change only what the evidence justifies, and
verify correctness and comparable performance before claiming a gain.

## Install

The repository is a skill-only Codex plugin: `.codex-plugin/plugin.json` points to
`skills/`. It can be registered by a Codex plugin marketplace pointing to this repository
root. A manifest alone does not register a marketplace; standalone installation
below is the direct path for this repository.

For standalone skill installation, ask Codex's skill installer:

> Install https://github.com/Swoorup/rust-perf-skills/tree/main/skills/rust-ui-performance

Or clone normally and copy the already named skill folder into the current
Agent Skills discovery directory; no clone-directory rename is needed:

```sh
git clone https://github.com/Swoorup/rust-perf-skills.git
mkdir -p ~/.agents/skills
cp -R rust-perf-skills/skills/rust-ui-performance ~/.agents/skills/
```

For a repository-scoped install use `.agents/skills/` in the target checkout.
Existing Codex skill-installer versions may use `~/.codex/skills`; use the path
supported by your client. Do not overwrite an existing installation blindly.
Restart/refresh skill discovery as required by the client.

## Use

Run in the target application checkout:

> Use $rust-ui-performance to investigate <workload>, targeting <metric>; audit only.

Audit requests authorize no application source edits. Request implementation when
wanted; a source search or allocation count alone cannot establish a speedup.

Start with [SKILL.md](skills/rust-ui-performance/SKILL.md). Its references provide
Rux architecture, profiling, ownership/layout, codegen and renderer details.
[Tooling](skills/rust-ui-performance/references/tooling.md) documents the three
portable Python scripts. [Profiler routing](skills/rust-ui-performance/references/profiler-routing.md)
selects the next measurement. Generic methodology remains in the main workflow;
Rux knowledge stays in the project reference rather than a second abstract skill.
Additional skills can later coexist under `skills/`.

## Validate and evaluate

```sh
python3 -m unittest discover -s tests -v
python3 tests/validate_repository.py
```

[Behavioral evals](skills/rust-ui-performance/evals/README.md) use the documented
Agent Skills eval format. Mechanical validation does not establish agent behavior;
run fresh-context eval sessions and grade their outputs/traces.

This repository needs Python 3.9+ and Git for its tools/tests, not a Rust build.
Target Rux benchmarks require their own pinned Rust/mise environment and GPU tools.
The inherited Rux snapshot lacks source identity/revision and is explicitly
unverified. Apple profiler guidance was checked against its WWDC25 primary transcript;
Instruments runtime checks require a supported Apple machine.
See [sources](skills/rust-ui-performance/references/sources.md) for provenance.
