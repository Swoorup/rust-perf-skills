# UI, text and GPU investigation branches

Use the architecture map to locate current symbols. Begin with the selected
frame lane and its work counts; then investigate the dominant timed phase.

## Reactive/retained work

Correlate notification count, derivation recomputes/changed outputs, graph patch
targets, invalidation flags, structural remounts, lowered/reused nodes and actual
frame stages. A stable signal value should not cause avoidable recomputation,
but compare cost of equality checks against repeated work. `set_if_changed` and
keyed structural retention already exist. Dirty membership and subtree spines
must remain bounded under multiple batches, deletion and remount.

Ask whether a small prop write incorrectly escalates to structure/layout/paint.
Patch-only input/presentation changes can bypass rebuild; deleting that bypass
is a regression even if one rebuild is faster. Preserve dependency re-subscription,
owner disposal and creation/topological ordering. Many mounted boxes or callbacks
are not proof of a full-tree reactive scan.

## Layout and projection

The rebuild lane currently solves mounted roots, with widths before wrapped
height measurement and heights before positions. Measure nodes visited, wrapped
remeasures, layout retry count, scratch growth, snapping, scroll correction,
geometry comparison and projection separately. Incremental layout is a candidate
only after showing significant rebuild cost and designing ancestor/sibling
dependency closure for hug/fill/fraction/grid/fit/wrap/custom arrangements.
Do not cache a subtree solely because its own props are unchanged.

The full renderer-facing projection refreshes payloads in place; unchanged
identity does not imply unchanged resolved style/geometry/text. Measure complete
versus sparse paths, patch/copy work, retained capacity and reordered records.
Any narrowed projection must preserve same-frame source equivalence, generations,
insertion/removal and successful paired presentation authority.

## Scene and text

Trace display fragment/subtree reuse through main-scene revisions and lowerer
groups/op identities. Measure cache fallback reasons, sorted display items,
transform/clip rebuilds, command cloning, tessellation/vector cache misses and
changed payloads. Composition order/overlap can require separate runs; grouping
by pipeline alone can change pixels. Retained paint output and GPU retained output
are different caches. Count scene work even when the final image is reused.

For text inspect measure requests/hits/misses, shape/layout/placement hits, content
hashing, font fallback, span segmentation and glyph pinning/rasterization. Separate
first-use fonts/glyphs, repeated unchanged labels, frequently changing numeric
strings, rich text and large editor text. Numeric/template paths and caches are
already implemented; verify eligibility before proposing another fast path.
Hashing still happens on some cache-hit paths; profile long unchanged strings
before replacing content keys with revisions. Any revision key needs owner identity,
mutation coverage and safe equality/collision behavior.

Inspect cache budgets/bypasses, admission/evictions, reserved capacity and active
consumer lifetimes. Increasing a cache can reduce misses and worsen resident
memory. Font/DPI/raster configuration, atlas generation and relocated entries
affect correctness. Atlas fallback clears placement state; reducing invalidation
without preserving glyph ownership can produce stale UVs. Use `RUX_TEXT_ATLAS_AUDIT`
for a diagnostic run, not an always-on benchmark. Atlas upload bytes/regions and
glyph misses should be correlated with changed text, not guessed from draw counts.

## Events and latency

Measure stationary route reuse and changing-position routing separately. The
reverse record traversal does AABB rejection followed by exact clip/transform
tests; caches and scratch already exist. Direct-target controller dispatch is not
the same workload as hit-testing every pointer move. Vary interaction-record
count and overlap, not only backing collection size. Record candidates, cache
hits/evaluations, routes and allocations. Compare spatial indexing only if scans
dominate; include index maintenance and moving/virtualized/presentation bounds.
Preserve topmost paint order, modal occlusion, capture, scrollbar foreground,
transform/clip chains, bubbling/focus and text selection.

For latency follow event sampling -> source drain -> frame start -> submit ->
present commit. Runtime scroll-presentation metrics and CPU timings do not include
compositor/scanout. Use platform display tracing if that is the user's metric.
Idle wakeups and demand coalescing can matter more than one active frame's speed.

## wgpu resources, uploads and encoding

Rux uses wgpu 30, a retained scene plan, explicit target damage/execution and a
renderer-owned frame graph. Locate the miss/rejection before changing resources:

| Evidence | Investigation |
| --- | --- |
| High planning time | scene compatibility, topology, retained deltas, graph construction and diagnostics; existing bulk lifetime analysis must not regress to pairwise rescans |
| Prep misses on LIVE unchanged frames | scene/version/target compatibility and retained pages; screenshots reset this cache |
| High upload bytes/calls | source page dirtiness, growth/fragmentation, full-buffer versus dirty/packed sparse strategy and staging costs |
| Repeated buffer/texture/bind-group creation | capacity growth, FrameSlotRing reuse, target/effect/atlas pools, cache admission and compatibility |
| High command encode/finish CPU | pass openings, clip/run fragmentation, target switches, draw and pipeline/bind-group switches |
| High intermediate submit | reason-coded graph hazard boundaries/backend policy, not an assumed universal one-submit requirement |
| GPU execution dominates | region timing/capture, bandwidth, overdraw, blur resolution/pass count, vector/custom shaders and target area |
| Memory pressure | per-pool budget, live/retained target bytes, fragmentation, staging in flight, atlas pages and process RSS |

Full uploads use Queue writes; sparse paths already use StagingBelt. Queue writes
are scheduled with submission, not a synchronous proof GPU copied data immediately.
Staging buffers need finish/submit/recall/map lifecycle discipline. Compare bytes,
API calls, staging/copy commands AND CPU/GPU time: small sparse writes can lose to
one contiguous upload. Existing staging allocation counters describe operations;
verify their semantics before equating them to heap allocations.

Do not map/poll/wait synchronously in a frame just to obtain a timer. Do not pool a
resource whose in-flight use/lifetime is unknown. Preserve usage/alignment, dynamic
uniform offsets, atlas revisions, texture copy formats and shader/bind-layout
compatibility. Pipeline creation is startup unless the traced scene rebuilds it.

Fewer draw calls can increase overdraw or destroy retention; fewer passes can
change blend/effect dependencies. Compare total active CPU, actual GPU duration,
memory and pixel output. Apple-Silicon Metal encoder timestamps are deliberately
disabled and graph submit boundaries may be required for final-blit/read-after-write
hazards. Use vendor tools and keep unavailable timestamp data explicit.

Native naga acceptance is insufficient for browser shaders: Chrome's Tint and
WebGPU validation can reject them. Read `docs/browser-target.md`, shader ownership
and generated wrappers before editing; run web-smoke for shader/scheduler changes.
Never hand-edit generated shader output or add an alternate renderer path to hide
a backend issue.
