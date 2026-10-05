# rust-perf-skills

An Agent Skill for evidence-driven performance investigation in the Rux Rust UI
and rendering codebase. It follows the actual signal, retained-tree, layout,
text, scene and wgpu paths instead of prescribing generic source-level changes.

## Install

Clone this repository into `~/.codex/skills/rust-ui-performance`, or copy its
contents into your Rux checkout at `.codex/skills/rust-ui-performance`.
Refresh skill discovery or restart your agent if necessary.

## Use

Run the agent in the Rux source checkout, then ask:

> Use $rust-ui-performance to investigate <workload>, targeting <metric>; audit only.

Request an isolated implementation explicitly when you want changes. The skill
requires a baseline, representative evidence, correctness checks and before/after
measurements before calling an optimization faster.

Start with [SKILL.md](SKILL.md). Supporting references cover
[architecture](references/project-architecture.md),
[profiling](references/profiling.md),
[ownership and memory layout](references/ownership-memory-layout.md),
[CPU/codegen/SIMD](references/cpu-codegen-simd.md),
[UI and rendering](references/ui-rendering.md), and
[authoritative sources](references/sources.md).

## Scope

This package is project-specific. Its source anchors and commands describe Rux
as inspected on 2026-10-05 and must be verified against the current checkout.
Application sources, build artifacts, raw profiling captures and the validation
audit are not included. No supporting benchmark framework is required: the skill
uses the target repository's existing facilities.
