# Reproducible measurements

Run from the repository root. Start with `mise exec -- rustc -Vv` and
`mise exec -- cargo metadata --format-version 1 --no-deps`. Record stable change
and current commit IDs, working diff, resolved lockfile hash, features, profile,
Cargo/rustc flags/config/wrapper, CPU/GPU/backend, OS, viewport/DPI, scene size,
seed, warmup, sample count, command and relevant environment. Never dump the whole
environment (it can contain secrets). The toolchain pin is in `mise.toml`.

Build first, then measure sequentially with unrelated compilation stopped.
Capture cold startup separately. Warm until pipeline, font, glyph and retained
targets stabilize for steady-state measurements. Use several trials and rotate
A/B order; report median, p95/p99 where raw samples support them, spread/MAD or
variance and budget exceedances. Do not derive percentiles from averages. Tiny
nanosecond timings need timer-overhead/quantization checks and batched validation.

Budget references: 60 Hz = 16.667 ms, 120 = 8.333 ms, 144 = 6.944 ms. CPU work
exceedances are not physical display misses. Use presentation tracing for actual
input-to-display latency. On-demand idle work, cache-hit work and animation/update
work are separate populations; do not silently mix them into one distribution.

## Existing harnesses

```sh
mise exec -- cargo run --release -p rux-core --features bench --example layout_baseline -- 1000
mise exec -- cargo run --release -p rux-core --features bench --example interaction_baseline -- --warmup 2000 --samples 20000
mise exec -- cargo run --release -p rux-core --features bench --example keyboard_baseline -- --warmup 2000 --samples 20000
mise exec -- cargo bench -p rux-widgets --bench mount_load
mise exec -- cargo bench -p rux-widgets --bench virtual_list
mise exec -- cargo bench -p rux-widgets --bench combobox_interaction
mise exec -- cargo bench -p rux-widgets --bench switch_interaction
mise exec -- cargo bench -p rux-widgets --bench button_action_status
```

Read boundaries before use:

- `layout_benchmark.rs::solve_once` clones nodes OUTSIDE timing but creates fresh
  default scratch INSIDE the solve. It reports mean/min/max, not warm-scratch
  tails or real text/GPU cost. For steady allocation evidence use
  `representative_solves_allocate_only_to_grow_their_scratch`; add a focused
  harness using the same persistent scratch only if timing that is required.
- Interaction example reports p50/p95/p99, exact warmed allocation counts, route
  reuse, candidate/clip/transform counts. Fixtures use test text, not full fonts.
  `pointer_route_reuse` times a changing-position route AND its repeated call;
  its percentile is not an isolated cache-hit latency. Divide operation counts
  by actual operations, not blindly by timed samples.
- Keyboard example reports p50/p95 and allocations; it does not report p99.
- Widget benches are standalone `harness=false` programs, not Criterion. Mount
  includes construction/first presentation and excludes teardown; virtual list
  separates cold mount, within-window scrolling and crossing a mounted window.
  Their fields named CPU can use monotonic elapsed clocks: inspect `support`.
- Allocation ratchets and large CPU ceilings are regression guards, not proof a
  system is optimal. Keep workload/layout probes constant when comparing.

GPU-backed single-toolkit profiling:

```sh
mise exec -- cargo run --release -p orderbook-bench-rad-ui -- --rows 40 --update-hz 100 --frame-hz 120 --warmup-frames 60 --measured-frames 600
```

For comparative results use `orderbook-bench-runner` with at least three trials
and `--audit-instrumentation true`; read `benchmarks/CONTRACT.md`. Only
`end_to_end_active` (current-thread CPU callback boundary) is cross-toolkit
rankable. Runtime wall-clock phases cannot be summed with CPU-clock phases.
Keep workload totals, scale, seed, machine and build metadata identical. Missing
values are null/unavailable, never zero. The logical update schedule is not a
measurement of display refresh. Per-frame printing is diagnostic overhead.

## Frame/render investigation

```sh
mise exec -- cargo xtask perf-budgets /tmp/rux-perf --list
mise exec -- cargo xtask perf-budgets /tmp/rux-perf --case dashboard
mise exec -- cargo run --release -p rux-demo -- --screenshot /tmp/rux-frame.png --screenshot-frames 8 --print-frame-metrics
mise exec -- cargo run --release -p rux-demo --features frame-alloc-metrics -- --exit-after-frames 120 --print-frame-metrics
```

Verify the case name with `--list`; the substring is an example. Live-window
idle apps may not produce a requested number of frames without demand; use an
animation or deterministic update workload. `--exit-after-frames` is a steady
demo facility; startup uses `RUX_EXIT_AFTER_FIRST_PRESENT`, governed by
`docs/gpu-performance-captures.md` and `xtask/src/startup_budget.rs`.

Read `RuntimeFrameMetrics` and current renderer diagnostics for metric names.
The old `rad-ui-frame-timing` skill's rad-app/rad-gpu commands and dashboard
numbers were stale at inspection; do not reuse them as a threshold. CPU fields
include rebuild/input/measure/layout/paint, acquire, renderer submit and present.
`frame_active_ms` excludes acquire from elapsed wall time; it is still not a CPU
clock. `gpu_ms` is host wall time, not GPU execution. Timers can nest; do not sum
unverified buckets. Counters explain stage selection, cache misses, invalidation,
lowered groups, upload API calls/bytes, runs/draws/passes, graph submits, target
retention, memory and text cache/atlas behavior.

Deterministic screenshots deliberately reset prepared primitive uploads. They
also add texture-target/final-blit/readback work. Use them for correctness and
structural evidence; use live windows for upload reuse and presentation pacing.
Zero intermediate-submit expectations are backend/scene-specific. Apple-Silicon
Metal disables encoder timestamps; use Instruments for GPU execution. Supported
timestamp paths have delayed results and exclude graph-boundary frames: correlate
frame identities and report missing samples instead of attributing stale timings.

## Allocation and memory attribution

Use `rux_base::allocation_diagnostics::CountingAllocator`, never another wrapper.
Install it at the measuring binary's global allocator and enable diagnostics.
`rux-demo`'s `frame-alloc-metrics` wires both binary and runtime attribution.
Library features alone cannot install an allocator. Counts cover successful alloc,
alloc_zeroed and realloc on the measured thread; realloc bytes count the full new
size. Deallocation, worker allocations, live bytes and peak RSS are different
metrics. `count_allocations` regions cannot nest. Tiered text-cache reserved bytes
and renderer budget ownership are useful but do not measure process residency.
Use platform allocations tools when retained memory or cross-thread work matters.
Compare instrumented/uninstrumented timing; zero without installation is not proof.

## Platform profiling

On macOS/Apple Silicon, use Instruments Time Profiler for CPU, Allocations for
allocation sites, and Game Performance/Metal System Trace or GPU counters for
submission, execution, display and resource lifetime. Build source-visible release
artifacts with temporary `CARGO_PROFILE_RELEASE_DEBUG=line-tables-only` and
`CARGO_PROFILE_RELEASE_STRIP=none`; retain optimization and pair identical settings.
`xcrun xctrace list templates` discovers installed templates; use bounded record
sessions and logging-disabled workloads. A sampled call tree establishes where
time is spent; it does not measure the benefit of an unimplemented alternative.

On Linux (conditional, not available in this macOS audit), use `perf stat` for
supported cycles/instructions/branches/cache events and `perf record`/flamegraph
for attribution. Record permissions, CPU PMU event support and multiplexing;
IPC/cache misses alone do not establish root cause. Use heaptrack for allocation
stacks; DHAT/Cachegrind are optional synthetic CPU/heap experiments, not GPU or
real-time frame-latency measurements. Do not add a profiler dependency to product
crates just to diagnose a local issue. Browser profiling uses the shipped Wasm
profile and browser tooling; native LLVM/Metal numbers do not generalize to it.

## Correctness and result policy

Capture baseline failures before changes. Run relevant crate tests and behavioral
probes; implementation completion also follows every canonical verification gate
in `CODING_GUIDELINE.md`. Layout: arrangement/wrap/scroll/pixel-grid invariants.
Ownership: deletion/generation/reentrancy and owner-disposal tests. Rendering:
`scene-golden`, `retained-scene-check --release`, visual regression and local PNG
comparison. Shaders/scheduler: browser web-smoke in addition to native checks.
Open both PNGs visually when assessing image differences. Keep raw logs/images in
ignored/temp paths. Do not regenerate goldens merely to silence a baseline failure.

Report unsuccessful commands, environment limitations and unrun checks explicitly.
An audit can finish with unverified hypotheses; an optimization cannot be called
faster or complete without its required before/after and correctness evidence.
