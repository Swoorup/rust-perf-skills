# Performance map of Rux

## Snapshot provenance — unverified historical orientation

- Reported inspection date: 2026-10-05 (inherited, not revalidated).
- Source repository identity: **unknown**; no Rux checkout or remote recorded.
- Source commit SHA: **unknown**; do not substitute the skill repository commit.
- Reported toolchain: rustc 1.97.1 / LLVM 22.1.6.
- Reported dependencies: wgpu/naga 30.0.1; lockfile hash unknown.

These versions and architectural descriptions are historical claims, not current
verified facts. Record remote identity, full HEAD SHA, dirty state, toolchain and
lockfile identity in an external refreshed snapshot using capture-environment.py.
The bundled [anchor manifest](project-anchors.json) deliberately has null provenance;
verification fails until a reviewed snapshot supplies it. Do not silently bless
an arbitrary checkout just because several symbols still exist.

Paths below are relative to the target Rux checkout. Rediscover full paths, e.g.
`rg --files | rg '(graph|box_store|timing)\.rs$'`, then
`rg -n 'RetainedNode|BoxSlot|RuntimeFrameMetrics' crates` and read implementations.
Symbol presence is not proof that semantics remain unchanged. If revision differs,
reinspect the relevant ownership, timing boundary and cache/invalidation behavior
before relying on this map.

## Inherited architecture description

Everything below describes the unverified reported inspection, not this cloud
host or a newly checked Rux revision.

## Build and crate boundaries

The root workspace includes `crates/*`, `demos/*`, `benchmarks/*`, `xtask` and
`xtask-lint`. Contrary to the opening of `benchmarks/README.md`, the benchmark
packages are currently root workspace members (`Cargo.toml`). Vendor
cosmic-text/Vello and the isolated facade-consumer check are excluded.

Rust edition 2024; mise pins rustc 1.97.1, LLVM 22.1.6 on this host. No root
`rust-version` declaration was found: the pin is not a declared MSRV. Read each
product's features and resolved Cargo metadata; feature unification affects
instrumentation. `rux-core` defaults to no features, `bench` enables test support;
`debug-ui` adds tracing/debug fields, `live-ui` adds live styles. Native, browser
`wasm32-unknown-unknown`, and platform-specific host boundaries exist; the Android
host was being changed and was not independently validated in this audit.

`release` sets thin LTO and one codegen unit, otherwise Cargo release defaults
(optimization 3, no debug assertions, no debuginfo, unwind on this native build).
Unstripped is not the same as source-level debug information. `dist` strips
symbols. `web-dist` uses size optimization `z`, fat LTO, one codegen unit and
abort. Debug selectively optimizes wgpu/text/Vello dependencies; it is still
not a throughput baseline. `.cargo/config.toml` adds a 16 MiB Wasm shadow stack;
no checked-in global native `target-cpu` flag was found. Local Cargo config,
wrappers and environment must also be recorded. Cargo.lock is generated and not
tracked; preserve its resolved versions/hash for paired runs.

| Owner | Relevant responsibility |
| --- | --- |
| `rux-base` | units, IDs, portable monotonic clock, shared CountingAllocator |
| `rux-state` / `rux-optics` | owner-scoped signals, revisions, stores/focus and thread ingress |
| `rux-core` | authored views, reactive/structural owners, retained graph/live boxes, layout, projection and interaction |
| `rux-style` / `rux-widgets` / `rux-visuals` | style resolution, components/controllers, visual descriptors |
| `rux-text` | font provider/assets, shaping/layout/editing contracts; vendored cosmic-text |
| `rux-font-wgpu` | shared text measurement/shaping caches and CPU glyph residency |
| `rux-paint` / `rux-render-protocol` | commands, retained groups, damage/demand and backend-neutral contracts |
| `rux-render` | UI compositor, retained display/text cache, canonical main scene |
| `rux-wgpu` | lowering, primitive/page storage, target planning, frame graph, GPU resources and submission |
| `rux-runtime` | winit lifecycle/scheduler, source/signal drains, frame phases, host input, present/commit |
| `rux-canvas`, `rux-chart-render`, materials | specialized surfaces/vector/custom renderer work |
| `xtask` / `xtask-lint` | runtime/visual/performance gates versus static architecture checks |

## Actual execution path

```text
OS input / deadline / signal wake / ordered accessibility request
  -> runtime source/signal drain; UI-thread writes and dependency propagation
  -> FrameDemand + invalidation -> FrameScheduler selects frame stages
  -> input lane routes against LAST SUCCESSFULLY PRESENTED interaction topology
  -> retained signal props / derivations patch or request a structural rebuild
  -> rebuild lane mounts changed structural regions and lowers retained nodes
       -> measure text -> X intrinsic/allocation -> width-dependent text
       -> Y intrinsic/allocation -> positions/constraints -> snap/scroll correction
       -> bounded retained-layout retries -> after-layout update
  -> paint lane completes renderer-facing projection + presentation candidate
       -> display fragment/text reuse -> publish RetainedMainScene
       -> atlas dirty regions/damage -> incremental retained paint lowering
  -> cached lane can reuse prepared scene when selected stages allow it
  -> renderer plan -> target damage execution -> frame graph/schedule
       -> retained primitive page preparation -> uploads/bind groups
       -> primitive/vector/effect/extension encode -> graph-required submits
  -> native surface present -> commit paired presentation/interaction
  -> next demand/deadline; idle waits instead of mandatory continuous frames
```

Preparation precedes surface acquisition on the native path. This is not a
mandatory full pipeline every frame. Follow `application/stages.rs` and
`application/runner.rs` in rux-runtime, not an assumed game-loop cadence.
Surface latency is configured to one (`window_frame.rs`); acquisition and
present calls are CPU wall intervals, not display scanout measurements.

## Ownership, identity and invalidation

- `rux-state/src/signal/arena.rs`: thread-local generation-checked headers,
  owner groups and per-type `Rc<dyn ErasedSlab>` holding `RefCell<Vec<Option<T>>>`.
  Copy signal handles are not per-value `Rc<RefCell<T>>` nodes. Reads validate
  generations/type; queued revisions and owner disposal govern lifetime.
- `rux-core/src/reactive/derivations.rs`: SlotMap cells, source reverse index,
  creation-order dirty `BTreeSet`, reusable frontier, `Rc<RefCell<Derivations>>`
  and `Rc<dyn Fn>` callbacks. Registration is mount-time; recomputation follows
  changed sources, not polling every closure each frame.
- `rux-core/src/structural.rs`: show/match/keyed owners rebuild fragment
  content; kept keys retain row ownership. Check remount causes before blaming
  reference counting.
- `rux-core/src/graph.rs`: `NodeId` keys a `SlotMap<RetainedNode>`;
  each node owns `Vec<NodeId>` children and boxed `NodeSpec` (intentional hot/cold
  split). Stable app `Id` differs from generation-bearing runtime `NodeId`.
  Signal reverse indexes, dirty membership, direct/ancestor invalidation and
  maintained subtree-dirty flags avoid deriving dirtiness through full scans.
- `rux-core/src/box_store.rs`: boxes persist in parallel arrays for box,
  LayoutNode, children and parent. `BoxSlot` checks generations at boundaries;
  `SmallVec<[usize;4]>` children use live slot indexes in layout. Clean subtree
  attachment is O(1); marked spines/refold/rescope and pulses have explicit owners.
- `rux-core/src/paint/erased.rs`: existing generation-checked frame bump arena,
  16 KiB chunks, typed payloads and promoted static vtables. Unsafe is isolated
  and allowlisted. A second arena would duplicate ownership without evidence.

UI data is intentionally single-threaded. `signal/crossing.rs` uses
`Arc`/Mutex/atomics for latest-value producer mailboxes and wake-on-ready;
ordered accessibility actions use an EventLoopProxy. Main UI does not need a
Tokio executor: native async GPU/fonts are driven at host boundaries; web awaits
promises. Network/terminal crates may use Tokio/background tasks independently.
Read `docs/thread-affinity.md` and its lock allowlist before changing a crossing.
No custom production allocator was identified in the inspected UI binaries:
optional CountingAllocator forwards to `System`; it is not an arena allocator.

## Layout, scene, input and text

`state/layout_drive.rs` solves all mounted roots on rebuild, snaps positions,
clamps/injects scroll state and records solved geometry. The solver
`layout/mod.rs` uses constant-axis passes and persistent `LayoutScratch`.
Built-in algorithms dispatch statically; `CustomLayout` uses
`Rc<Box<dyn LayoutAlgorithm>>` with identity equality (`layout/algorithm.rs`).
Wrapped text measures at assigned width. Component retries are budgeted by the
runtime. Local graph invalidation does not itself imply incremental layout.

`render_snapshot.rs`: one retained renderer-facing projection,
generation-aware lookup, transactional sparse patching and in-place complete
reconciliation. Full authoring still refreshes all relevant payloads; sparse
change counts are not sufficient to skip that refresh. Presented interaction is
published only with successful presentation, not when an unpresented frame is built.

`presented_interaction.rs`: unchanged route keys reuse scratch;
new geometric routes traverse records in reverse paint order with AABB rejection,
clip/transform caches, occlusion/capture/modal rules. Virtualized items do not
equal interaction-record count. Distinguish moving-pointer scans from stationary
sample reuse and direct-target dispatch.

`rux-render/src/composer/display_build.rs`, `retained_display_cache.rs`,
`main_scene/mod.rs`: retain fragment/display/subtree/text results; publish one
versioned main scene with topology/payload/resource changes. Clipping,
composition layers and late presentation transforms determine ordering/batching.
`rux-wgpu/src/paint_lowering.rs` maintains scene/group/op identities and text
instance reuse, so text-shaping hits alone do not prove scene/upload reuse.

`rux-font-wgpu/src/text_system.rs` owns measurement/layout/placement
caches, cosmic-text buffer reuse, numeric/template paths, glyph pinning and
diagnostics. Cache keys hash content/spans and include width/font/spacing/DPI;
measurement hits verify source identity/content. Tiered caches (`tiered_cache.rs`)
have hard entry/byte budgets, second-use admission and bounded activity scans.
Reserved cache bytes are not RSS. Font revisions and DPI changes invalidate them.
`atlas.rs` uses Swash rasterization and etagere fixed pages on the CPU, publishing
dirty upload regions with generations/entry changes/eviction fallbacks.

## GPU ownership and tools

`renderer/frame_encode/mod.rs` owns scene planning, execution selection,
resource registration, primitive prep, encoding and finalization.
`primitive_upload.rs` retains source pages and family storage, tracks dirty
ranges and fragmentation/compaction. `primitive_upload/transfer.rs` chooses
full `Queue::write_buffer` or dirty/packed sparse StagingBelt copies.
`frame_slot_ring.rs` reuses uniform/storage resource slots. Targets, effects,
Vello intermediates and textures have retained caches and a memory budget;
extensions participate in the renderer-owned graph rather than submitting at will.
`renderer/frame_graph.rs` builds dense frame-local resource/node plans and explicit
dependency/hazard boundaries. A dense append-only frame ID does not need generations.

`context.rs` deliberately disables encoder timestamps on Apple-Silicon Metal;
`renderer/timing.rs` has delayed optional query readbacks on supported paths.
`frame_encode/mod.rs` excludes graph submit-boundary frames from timestamps.
The runtime's `gpu_ms` times host work around submit/present. Native Metal hazards
can legitimately require intermediate submits. Resource lifetime or hazard policy
changes need backend tests and pixel evidence, not just a reduced counter.

Facilities: core layout/interaction/keyboard examples; widget mount, virtual list,
combobox/switch/button benches; allocation ratchets and keyed-row/signal tests;
release demo frame metrics; deterministic order-book current-thread CPU benchmark;
perf/compile/startup/canvas/dispatch gates; scene and pixel goldens; debug-ui tracing,
text-atlas audit and renderer/GPU-error diagnostics. See profiling reference for
commands and their limits. No Criterion dependency was found in these harnesses.
