---
name: rust-ui-performance
description: Investigate and prove CPU, latency, allocation, memory, text, retained UI, and wgpu performance changes in Rust UI systems, especially Rux using its existing release benchmarks, frame lanes, retained-scene counters, and platform profilers. Use for performance audits, regressions, or requested optimizations.
---

# Rux performance engineering

Produce falsifiable findings and reproducible experiments. Inspection alone can
justify a hypothesis, never a speedup claim. An audit does not authorize application
changes. Say **no optimization is justified yet** when evidence is insufficient.

## Orient before measuring

Read the target repository's agent/build instructions. In Rux, read
`AGENTS.md` and `CODING_GUIDELINE.md` and follow its Jujutsu/issue workflow
when implementation is requested. Preserve unrelated work.
Read [project-architecture.md](references/project-architecture.md), then verify its
named symbols in current source. All Rux-specific claims in these references
are historical until verified against the target. The snapshot needs matching
repository identity, revision and anchors.
Run `scripts/verify-anchors.py TARGET_CHECKOUT` before relying on it; on failure,
rediscover paths and symbols with `rg`, read their owners, and record current
provenance. For Rux UI authoring changes read the authoring, styling, and design
guides; before dependencies, clocks, or shaders read `docs/browser-target.md`.

Choose only the references needed:

- Baselines, clocks, allocation attribution, sampling, commands and correctness:
  [profiling.md](references/profiling.md).
- Ownership, arena/deletion decisions, layout and collections:
  [ownership-memory-layout.md](references/ownership-memory-layout.md).
- Rust/LLVM/architecture-specific investigation:
  [cpu-codegen-simd.md](references/cpu-codegen-simd.md).
- Frame lanes, layout, scene, text, input, GPU resources and submission:
  [ui-rendering.md](references/ui-rendering.md).
- Authoritative sources, versions and applicability: [sources.md](references/sources.md).

## Investigation loop

1. **Define scope.** Record the triggering action, scene size, viewport/DPI,
   target/backend, cold versus warm behavior, and success metric. Choose CPU work,
   real presentation latency, GPU duration or memory deliberately; they differ.
2. **Trace the path.** Follow the action through signals/derivations, selected
   frame stages, graph/live boxes, measurement/layout, projection/presentation,
   retained scene/lowering, renderer planning/uploads/encoding, submit/present.
   Identify skipped work and the lifetime owner at each relevant boundary.
3. **Find a harness.** Prefer existing examples, widget benches, structural gates
   or deterministic order-book runs. Read their timed regions and fixtures before
   using numbers. Extend a fixture only if it cannot express the real workload.
4. **Capture baseline.** Use [deterministic tooling](references/tooling.md) to
   capture provenance and compare raw measurements. Activate the target toolchain
   (`mise exec --` in Rux) and use an optimized production-equivalent
   profile. Record environment, code identity/diff, commands, workload counters,
   warmup, raw samples and several sequential trials. Run baseline correctness.
5. **Collect evidence.** Use the [profiler routing table](references/profiler-routing.md)
   to select the next measurement; sample with
   logging disabled. Attribute hot samples, allocations, cache misses, dirty work,
   upload bytes, draw/pass counts or GPU regions to actual source. Mark unavailable
   measurements explicitly. Preserve tails and variability, not only averages.
6. **Rank hypotheses.** Prefer unnecessary work → algorithms/complexity →
   invalidation granularity → representation/locality → allocation/lifetime →
   synchronization → compiler/codegen → SIMD/unsafe. Rank by measured share,
   expected benefit, confidence and risk; give a falsification condition.
7. **Experiment when requested.** Make one meaningful, isolated change with clear
   ownership; preserve deletion, generation, ordering, dirty propagation, text and
   presentation correctness. Consolidate helpers and migrate fully. Do not leave
   parallel old/new paths. Consult existing decisions before reopening one.
8. **Compare.** Repeat the same workload and features in interleaved A/B trials,
   after builds finish. Check correctness, tails, work counts and memory as well
   as the primary metric. Confirm instrumentation overhead when material.
9. **Keep or revert.** Retain only a representative, reproducible gain without
   unacceptable regressions. Revert only the experiment's edits, preserving other
   work. For an inconclusive result, report that and the next discriminating test.
   Record measured decisions/rejections in the canonical owning doc as repository
   policy requires when implementing a task.
10. **Report.** State baseline and after values, absolute/relative delta, dispersion,
    measurement boundary, correctness results, tradeoffs, confidence, artifacts,
    reproduction commands and the next candidate. Never imply a baseline-only
    audit proved an improvement.

## Evidence states and reporting

Keep **suspicion**, **measured bottleneck**, **proposed optimization**, and
**verified optimization** separate. A source search is a discovery aid, not cost
attribution. A correctness-only borrow panic is outside this skill unless the
request also concerns performance.

For investigation, use a short **Working hypothesis**: location (path + symbol),
observation/evidence, hypothesis, falsifier, next measurement. Audit-only means
no application source edits. Unmeasured hypotheses do not need a full finding.

Reserve the following contract for validated final findings. Add measurement
boundary, raw artifact paths, exact reproduction commands, comparable before/after
values when changed, correctness results and regression risks. A baseline finding
can establish a bottleneck but cannot establish an optimization.

## Final finding contract

Every validated finding includes **Location** (path and symbol; current line optional), **Observation**,
**Classification**, **Severity**, **Evidence**, **Why it matters**, **Estimated
impact**, **Confidence**, **Proposed experiment**, **Suggested change**,
**Benchmark/measurement required**, and **Risks/tradeoffs**.

- Classification: `MEASURED BOTTLENECK` (a material limiting cost demonstrated
  for the stated workload/metric, not merely a nonzero timer),
  or `VERIFIED OPTIMIZATION` (comparable measurements and correctness checks
  support the change). Keep unmeasured costs in working hypotheses.
- Severity: `P0` catastrophic/dominant; `P1` major measurable bottleneck;
  `P2` worthwhile optimization; `P3` small optimization; `P4` speculative/cleanup.
- Confidence: `HIGH`, `MEDIUM`, or `LOW`, independent of severity.
- Estimated impact: measured share or a conditional bound; otherwise unknown.
  Never invent percentage gains. Counter growth proves work, not saved time.

## Reject cargo-cult changes

Do not replace `Rc`, `Arc`, `RefCell`, collections, or the allocator merely because
they exist. Measure clone/drop, borrows, locality, lifetime, cardinality, security,
and contention in the requested path. The historical Rux snapshot describes generation-safe node and
box storage; rediscover those owners before proposing an arena.

Do not add threads without useful parallel work and a measured crossover. Keep
UI ownership single-threaded and respect the signal/accessibility ingress.
Do not add SIMD to an unproven hot loop or unsafe for a theoretical bounds check.
Prefer safe Rust, deletion of work, compact storage, reuse and autovectorization.

Do not optimize debug builds, infer speed from aesthetics, trust means alone or
an unrepresentative microbenchmark, or include first-use pipelines in a warm
baseline. Do not optimize CPU when GPU dominates, or draws when scene creation
dominates. Fewer allocations/draws/uploads do not automatically mean faster.

Do not call runtime `gpu_ms` GPU execution time, treat absent allocator/timestamp
data as zero, use screenshot-reset upload misses as live-window evidence, or
delete graph-authored Metal hazard boundaries to force one submission.
