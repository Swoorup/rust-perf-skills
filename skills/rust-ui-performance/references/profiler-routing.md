# Choose the next measurement

Start with a representative optimized workload and the actual metric boundary.
Source matches (`Rc`, `RefCell`, `.clone()`, `Box`, maps) only locate candidates.

| Observed symptom | First measurement | Follow-up | Evidence needed to justify change |
| --- | --- | --- | --- |
| High CPU phase | phase work counts + sampled hot stacks | CPU counters, disassembly of attributed hot function | material cost of unnecessary work or limiting loop; comparable timing |
| Allocation spikes | allocation stacks/counts by phase | capacity/lifetime distribution + uninstrumented timing | hot allocation traffic, ownership-safe reuse, timing or memory benefit |
| Memory growth | RSS/live heap and retained pool bytes over churn | allocation generations, owners, eviction/free-slot behavior | retained leak or excessive working set; bounded plateau after change |
| Cache/locality or pointer chasing | hot traversal stacks + accessed fields/cardinality | supported PMU memory/cache events, access stride, layout experiment | locality-related stalls on actual path, not simply many pointers |
| Rc/Arc/RefCell/Box suspicion | clone/drop/borrow frequency and sampled owner path | generated checks/indirections, allocation topology | material attributed overhead; preserve sharing, generations and reentrancy |
| Tail-latency spikes | raw frame/event samples + time-aligned phase spans | scheduler/locks, allocation, cold cache/pipeline events | culprit aligned with tails; equivalent p95/p99 without shifting populations |
| SIMD opportunity | prove hot loop and runtime share | LLVM remarks + final binary assembly | inadequate vectorization, suitable dependencies, representative length crossover |
| Suspected GPU bound | verify timer semantics; actual GPU intervals/capture | GPU counters, shader/pass/overdraw attribution | GPU execution dominates; region-specific gain with unchanged pixels |
| Upload/submission bound | host encode/submit spans, bytes/calls/resource creation | Metal timeline + staging/in-flight lifecycle | CPU transfer/submission cost or queue starvation attributable to current strategy |
| Locks/atomics/contention | wait/hold time, wakeups, throughput and fanout | scheduling timeline; supported coherence events | observed contention/false sharing; ordering and latency remain correct |
| Code size/front-end pressure | hot code footprint + attributed instruction behavior | inlining/monomorphization, LTO experiment | front-end cost in shipping binary; no startup/tail/deployment regression |

Counters constrain hypotheses; they do not prove that a proposed alternative is
faster. Follow the optimization hierarchy in SKILL.md, and use the detailed
ownership, codegen and renderer references only for the measured branch.

## macOS / Apple Silicon tool choice

Discover installed tools with `xcrun xctrace list templates`; record macOS, Xcode,
Instruments and chip model. Template names, event sets, permissions and hardware
support vary. Do not promise a counter or trace feature exists on every M-series
machine. Use matching optimized source-visible binaries; logging/instrumentation
can change both scheduling and samples.

- **Where CPU resources go:** prefer **CPU Profiler** when available. Apple's
  WWDC25 session explains that independent cycle-based sampling avoids Time
  Profiler timer aliasing and weights asymmetric CPU frequencies. Use **Time
  Profiler** for time-distribution/concurrent-thread questions and as a fallback;
  cycle-weighted samples and wall time are different quantities. Deferred mode
  reduces analysis overhead for bounded automated captures.
- **Why a proven hot path stalls:** **CPU Counters** Bottleneck Analysis separates
  Instruction Delivery (front end), Instruction Processing (back end) and
  Instruction Discards (speculation/branches). Use follow-up modes/events for
  branches and memory behavior. A back-end category is not automatically a cache
  diagnosis: dependencies and other resources can constrain it. Remove software
  overhead before drawing microarchitectural conclusions.
- **Unexpected generated control flow:** **Processor Trace** reconstructs
  user-space control flow/function calls from hardware trace. Apple's WWDC25
  session reports Instruments 16.3 introduction and support on M4-or-later Macs/
  iPad Pro and iPhone 16/16 Pro or later, with device settings required.
  Apple's current guide requires macOS 15.4 / iPadOS 18.4 / iOS 18.4 or later;
  any Mac can analyze saved traces even if it cannot record them. Keep captures
  short: data volume is large. Check current hardware/OS/tool permissions rather
  than assuming support across all M-series chips. Fall back to final-binary
  assembly, LLVM remarks and bounded sampling on unsupported devices.
- **Allocator traffic / retained heap:** Allocations and allocation generations;
  compare instrumentation overhead, live bytes and RSS separately.
- **CPU/queue/GPU/display relationship:** Game Performance / Metal System Trace
  where installed, then GPU capture/counters for expensive passes and shaders.
  Distinguish CPU preparation, uploads, submission, queue gaps, GPU execution and
  display pacing. CPU Profiler does not establish shader execution duration.

Primary source: [Apple WWDC25: Optimize CPU performance with Instruments](https://developer.apple.com/videos/play/wwdc2025/308/),
including transcript sections 8:50 (profilers), 14:05 (Processor Trace), and
19:51 (bottleneck analysis), read 2026-10-05. Its Swift binary-search example is
an illustration of measured investigation, not a prescription for Rust UI data
structures. Check current installed support before using any tool; this Linux
cloud machine cannot validate Instruments recordings or hardware capabilities.

Also checked Apple's [Processor Trace guide](https://developer.apple.com/documentation/xcode/analyzing-cpu-usage-with-processor-trace)
and [Metal performance guide](https://developer.apple.com/documentation/xcode/analyzing-the-performance-of-your-metal-app/)
on 2026-10-05 via their official documentation JSON. Game Performance includes
Time Profiler, scheduler/thread state, Metal resource/GPU and display tracks;
performance counters are opt-in. GPU idle gaps can reflect host or scheduling
stalls, not shader cost. Match the captured events to the requested workload.
