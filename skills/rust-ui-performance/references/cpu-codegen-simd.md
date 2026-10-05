# CPU and codegen experiments

Only enter this branch when a release profile shows a meaningful hot function or
loop after algorithm/invalidation/locality work. Record rustc/LLVM, target triple,
profile and the target's deployed CPU floor. Native release already uses thin LTO
and one codegen unit; Cranelift desktop-dev is an iteration workflow, not the
production LLVM throughput baseline. Browser web-dist deliberately optimizes size.

## Inspect before prescribing

Locate the actual monomorphization in the final binary or emit assembly/LLVM IR
for a focused owner. For example, after baseline compilation:

```sh
mise exec -- cargo rustc --release -p rux-core --features bench --example layout_baseline -- --emit=asm,llvm-ir
mise exec -- rustc --print target-features
```

LTO can inline/remove a library symbol; inspect the consuming binary and call
sites, not an unrelated toy function. Use pinned llvm-tools/llvm-objdump or
platform disassembly tools. If source correlation is needed temporarily enable
release line-table debuginfo without enabling debug assertions. Use rustc's
`-C remark=...` support for LLVM pass remarks after checking the pinned compiler
help; clang `-Rpass` flags are not Cargo/rustc flags. Keep emitted artifacts in
target/tmp output. Absence of a convenient named loop is not proof of scalar code.

Investigate bounds checks, alias/dependency chains, indirect calls, inlining,
monomorphization/code size, conversions, branches and access stride. Compare a
safe slice/iterator or layout simplification before unchecked indexing. Rux's
layout axes are already const-specialized. Tree traversal is irregular; an
arithmetic-containing loop is not automatically a SIMD candidate.

## Vectorization gate

Require all four: hot loop, meaningful share of runtime, inadequate generated
vectorization, and plausible dependencies/layout. LLVM loop and SLP vectorizers
already perform cost-based transformations. Check successful/missed remarks and
assembly; reduction order, callbacks, branch divergence, aliasing and gather
loads can defeat a proposed widening. Floating-point reassociation may alter
geometry, snapping and golden pixels, so precision is part of correctness.

On Apple Silicon inspect ARM/NEON loads, arithmetic, conversions and scalar tails;
on x86 inspect the supported SSE/AVX variants. A memcpy/copy_from_slice may already
use a tuned vector implementation. Measure realistic lengths/alignment, not only
huge aligned arrays. A vector-width improvement may increase instruction/code
size or hurt small cases. The historical audit is not evidence for the current workload.

`std::simd` availability is compiler-sensitive. The inherited snapshot reports an E0658 (`portable_simd`) probe on 1.97.1;
that probe is not reproducible here. Check the actual pinned compiler and run a
minimal compile probe rather than assuming current stability from online docs. Do not upgrade the toolchain or add nightly merely
to use it. `std::arch` is architecture-specific: any justified intrinsic design
needs target gating/runtime dispatch where appropriate, scalar fallback,
before/after tails, maintenance cost, and the unsafe allowlist/SAFETY invariants
if applicable. Validate browser compilation and deployment compatibility.

## Compiler flags and advanced optimization

`target-cpu=native` changes the hardware requirement; it is a machine-local
experiment, not a library default. Compare identical flags in A/B builds; do not
attribute a compiler-flag change to a source change. Explicit target-feature code
must not execute on unsupported CPUs. Inlining and LTO trade build time/code size
for speed and can regress instruction locality; measure the actual shipping
binary, startup and representative scenes.

PGO is conditional on a representative training corpus after dominant costs are
understood. Follow rustc's generate/merge/use procedure with matching compiler,
LLVM tools and absolute profile paths; validate on held-out scenes, not only the
training workload. BOLT is a separate, platform/object-format-specific option
for suitable native binaries, not a general Apple-Metal or Wasm recommendation.
Check tool support before experimenting; neither was warranted here.

Do not infer gains from branch/cache/IPC counters alone. Report samples and
before/after elapsed work with a fixed result checksum/scene; a loop deleted by
the optimizer or a different amount of work is not a successful optimization.
