# Investigate ownership and storage

Start from the requested workload's hot call tree and allocation stacks. Separate
mount-time construction, owner disposal, steady traversal and signal propagation.
Source presence is not cost evidence. Preserve the existing owner/lifetime contract
when constructing an alternative.

## Reference counting and dynamic borrowing

Rux's structural graph already uses `NodeId -> SlotMap<RetainedNode>` and live boxes
use generation-checked parallel arrays. Signals are Copy handles into owner-scoped
typed slabs. `Rc` still intentionally shares node planes, immutable text layouts,
callbacks, derivations and UI-thread state; native GPU/window handles use `Arc`.

For `Rc`/`Arc`, measure clone/drop frequency on hot paths, distinct allocations,
pointer chasing, object lifetime, cache working set and cross-thread sharing.
An `Rc` clone shares payload; it is not a deep clone. `Arc` atomics belong at real
crossings. A change that removes counts but copies large text/layout payloads may
lose. Separate refcount CPU cost from the allocation topology it represents.

For `RefCell`, measure borrow frequency in traversal and generated code; inspect
nested access, callback reentrancy and conflicts. The signal slab's closure-based
read/write/lend protocol and derivation registry have deliberate borrowing scopes.
A negligible dynamic check is different from a confused ownership graph. Do not
replace it with unsafe interior mutation or move the graph across threads merely
to evade a borrow. `Cell` is appropriate for Copy interior state where semantics fit.

## Choosing handles or an arena

Before comparing dense arena, generational arena/slotmap, slab, stable Vec index,
hierarchical ownership, bump/frame arena or pool, write down:

| Question | Rux consequence |
| --- | --- |
| Can objects be deleted/reinserted? | NodeId/BoxSlot generations reject stale references; bare indexes cannot replace them at public/lifetime boundaries. |
| Do records move/reorder? | Stable app Id, slot index and presentation order differ; compaction needs reverse-index repair. |
| Who disposes state/callbacks? | Owner-scoped derivations/signals and leaving fragments must not outlive or lose their region. |
| Can a frame be discarded? | Candidate projection must not become input authority until paired presentation commits. |
| Are payloads independently shared? | Text-layout Rc lifetime can span frame/cache eviction; arena reset cannot invalidate an active consumer. |
| What grows under churn? | Track free slots, high-water capacity, fragmentation, generation exhaustion and retained budgets. |

Compare iteration locality and checked lookup cost against deletion behavior,
fragmentation, memory bounds, ergonomic cost and maintenance. A bump arena suits
one bulk lifetime, not arbitrary retained deletion; Rux already has one for typed
paint payloads. A pool trades allocation for retained footprint and reset cost.
Do not add a parallel storage path; an accepted migration must consolidate ownership.

## Layout and collections

Measure `size_of`/`align_of` with the actual compiler/target/features; inspect hot
fields touched per pass, not just total struct bytes. Rust's default layout does
not promise a permanent field order. `RetainedNode` boxes its cold spec; BoxStore
already separates layouts and links from the large UiBox; renderer projection
uses parallel arrays. Compare remaining hot/cold splitting, AoS/SoA/hybrid layouts,
enum payload size, padding and traversal order only where sampled/cache evidence
shows meaningful working-set cost. Record growth and rebuild/reorder costs too.

Do not remove `Rc<Box<dyn LayoutAlgorithm>>`'s second indirection mechanically:
it keeps the common Arrangement small; only custom layouts pay dynamic dispatch.
Likewise AnyView handles heterogeneity/recursion while typed views keep normal
dispatch static. Compare code size/monomorphization against dynamic overhead.

For collections, measure cardinality distribution, iteration-to-lookup ratio,
mutation/deletion, key costs, ordering and attacker control. Rux already uses
FxHashMap for internal IDs, SmallVec for short child/source lists, BTreeSet to
order dirty derivations and dense frame-graph IDs. Linear search can win for tiny
lists but not unbounded fanout; sorted vectors buy locality at insertion cost.
Do not substitute a fast non-resistant hasher for externally controlled strings
without checking the threat/workload boundary. Keep deterministic creation/order
semantics when replacing a tree/set.

## Allocations, locks and reuse

Attribute temporary Vec/collect/String/format/boxed closure/cloning/capacity
growth to timed phases. `clear()` preserves capacity; reservations/scratch,
SmallVec/ArrayVec/stack storage or pools need actual cardinality and footprint
measurements. Larger inline storage can worsen traversal, stack use and copying.
The warmed layout solver and routing benchmarks already assert zero allocations;
fresh-scratch layout and cold mount legitimately allocate. GPU staging allocation
counters are not necessarily underlying heap allocation calls.

Inspect lock frequency/duration, contention and wake/drain throughput in
`signal/crossing.rs` rather than flagging every Mutex. Record producer fanout,
coalesced messages, ordering and latency. Test cache-line bouncing/false sharing
and atomic-order weakening only with a correctness argument. UI state remains
single-threaded; parallel workers should deliver messages, immutable snapshots or
explicit double-buffered results where useful. Keep latest-value mailbox semantics
distinct from ordered accessibility/input requests. Threads have scheduling,
copying and synchronization costs; compare crossover sizes and tail latency.
