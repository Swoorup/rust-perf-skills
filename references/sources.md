# Rust UI performance sources

Consulted 2026-10-05 for `rust-ui-performance`. These are primary
documentation, not evidence that this application has a bottleneck. Verify version
and target applicability when following a link. Resolved audit build: rustc 1.97.1,
LLVM 22.1.6, wgpu/naga 30.0.1. Online Rust documentation currently describes a
newer compiler; pinned local documentation and compile probes settle availability.

| Source | What informed the skill | Applicability |
| --- | --- | --- |
| [Cargo profiles](https://doc.rust-lang.org/cargo/reference/profiles.html) | Release/debug defaults, thin/fat LTO, codegen units, debug info and profile overrides | Root manifests override defaults; package features and local configuration also matter |
| [rustc codegen options](https://doc.rust-lang.org/rustc/codegen-options/index.html) | Target CPU/features, remarks, emit/codegen and debug settings | Check pinned compiler help; native flags can change deployment requirements |
| [Rust Reference: codegen attributes](https://doc.rust-lang.org/reference/attributes/codegen.html) | Inlining and target-feature semantics | CPU-specific functions require supported-feature execution |
| [Rust Reference: type layout](https://doc.rust-lang.org/reference/type-layout.html) | Default layout versus representation guarantees | Size/alignment measured on one target/compiler is not a permanent Rust ABI |
| [Rustonomicon: alternative representations](https://doc.rust-lang.org/nomicon/other-reprs.html) | FFI representation and packed/aligned tradeoffs | No blanket repr(C)/packed optimization; preserve GPU wire/FFI invariants |
| [std::rc](https://doc.rust-lang.org/std/rc/index.html) | Non-atomic shared ownership, clone identity and cycles | Rux UI is single-threaded; payload sharing is intentional |
| [std::sync::Arc](https://doc.rust-lang.org/std/sync/struct.Arc.html) | Atomic counts and Send/Sync dependence on payload | Cross-thread/native handle ownership; not a substitute for thread-safe data |
| [std::cell](https://doc.rust-lang.org/std/cell/index.html) | Interior mutation and dynamic borrow semantics | Investigate dynamic checks/reentrancy rather than banning RefCell |
| [std::arch](https://doc.rust-lang.org/std/arch/index.html) | Architecture-specific intrinsics and feature detection | ARM/NEON and x86 dispatch/fallback need deployment constraints |
| [std::simd](https://doc.rust-lang.org/std/simd/index.html) | Portable SIMD API/status | Newer online docs do not establish support on pinned 1.97.1; local Simd probe failed E0658 |
| [LLVM vectorizers](https://llvm.org/docs/Vectorizers.html) | Loop/SLP vectorization, cost models, missed remarks, alias and reduction blockers | LLVM upstream docs can differ from pinned LLVM; clang remark flags are not rustc flags |
| [rustc PGO](https://doc.rust-lang.org/rustc/profile-guided-optimization.html) | Generate/train/merge/use and matching toolchain | Conditional future experiment with representative and held-out scenes |
| [LLVM BOLT](https://github.com/llvm/llvm-project/blob/main/bolt/README.md) | Binary optimizer prerequisites and platform scope | Not selected for this Apple-Metal/Wasm project audit |
| [wgpu Queue 30.0.1](https://docs.rs/wgpu/30.0.1/wgpu/struct.Queue.html) | Queue write transfer scheduling, temporary staging, timestamp period | Version matches resolved renderer; host submit time is not GPU execution |
| [wgpu StagingBelt 30.0.1](https://docs.rs/wgpu/30.0.1/wgpu/util/struct.StagingBelt.html) | Reusable staging and finish/recall lifecycle | Rux already uses it for sparse uploads; compare cost with full writes |
| [wgpu Features 30.0.1](https://docs.rs/wgpu/30.0.1/wgpu/struct.Features.html) | Optional device features and encoder-timestamp support | Apple GPU encoder timestamps are not a portable assumption; Rux normalizes support |
| [naga 30.0.1](https://docs.rs/naga/30.0.1/naga/) | Shader parsing/validation/translation scope | Native validation does not replace Chrome Tint/WebGPU smoke tests |
| [Apple: analyzing Metal performance](https://developer.apple.com/documentation/xcode/analyzing-the-performance-of-your-metal-app/) | Game Performance, Time Profiler, system/thread/display/resource/GPU traces | macOS/Apple GPU profiling; distinguish CPU, queue, GPU and display |
| [Apple: optimizing GPU performance](https://developer.apple.com/documentation/xcode/optimizing-gpu-performance) | GPU capture/counter attribution and shader analysis | Vendor tools for unavailable or inadequate application GPU timestamps |
| [cargo-flamegraph](https://github.com/flamegraph-rs/flamegraph) | Sampling and symbol configuration | Conditional Linux/native profiling; permissions/backend vary |
| [KDE heaptrack](https://github.com/KDE/heaptrack) | Allocation stack attribution | Linux alternative; not used on this macOS host |
| [DHAT crate](https://docs.rs/dhat/latest/dhat/) | Heap instrumentation capabilities | Optional isolated harness; do not replace the project's shared allocator by default |
| [Valgrind Cachegrind manual](https://valgrind.org/docs/manual/cg-manual.html) | Synthetic instruction/cache analysis | Conditional supported native targets; not GPU or real-time presentation evidence |

The W3C WebGPU specification and GPUWeb spec URLs were attempted but the browsing
tool returned errors; they were not used to assert normative behavior. wgpu's
versioned documentation and the project's browser contract support the GPU rules
here. The perf wiki redirected without readable content; no hardware-event claim
is sourced from that failed fetch. Criterion was not researched or added because
the inspected project harnesses do not use it.

Project-owned sources are the implementation anchors in
[project-architecture.md](project-architecture.md),
`CODING_GUIDELINE.md`, `docs/thread-affinity.md`, `docs/browser-target.md`,
`docs/gpu-performance-captures.md`, `docs/core-layout-engine.md`,
`docs/retained-ui-architecture.md`, `docs/rendering-architecture.md`, and
`benchmarks/CONTRACT.md`. Their contracts take precedence over generic tuning advice.
