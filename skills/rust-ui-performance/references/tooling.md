# Deterministic experiment tools

All tools need Python 3.9+ and use only its standard library. Run them from any
working directory using absolute paths to the installed skill. Paths below are
relative to the skill directory; `TARGET` is the application checkout, not this
skill repository. Keep artifacts outside the target checkout or in ignored paths.

```sh
# Activate the target's pinned tools first; for Rux use mise exec -- python3 ...
python3 scripts/capture-environment.py TARGET --profile release --features bench \
  --workload 'scene/seed/viewport/DPI/backend/warmup/sample-count' \
  --command 'exact benchmark invocation' > /tmp/environment.json
python3 scripts/compare-runs.py /tmp/before.json /tmp/after.json
python3 scripts/verify-anchors.py TARGET --manifest /tmp/reviewed-anchors.json
```

Capture records HEAD, dirty status, rustc verbose output (including LLVM/host),
Cargo version, OS/CPU, declared target/profile/features, flag/wrapper overrides,
and SHA256 identities for root manifest/lockfile/toolchain and discovered Cargo
configuration. It does not dump config contents or the environment. Review flags
and command text for secrets before sharing; do not put credentials in them.
For a nested Cargo workspace, point TARGET at its workspace root. Record dirty
diff artifacts, effective feature resolution, GPU/backend, thermal/power state
and workload counters separately. Null means unavailable, not zero. A successful
capture with missing rustc does not validate the application's build environment.

Comparison input is JSON, one raw sample population per file:

```json
{"metric":"frame_active","unit":"ms","workload":"scene-A/warm/seed-1","samples":[10,11,9,12]}
```

Metric, unit and workload must match. Output includes n, median, MAD, min/max,
linearly interpolated p95/p99 and signed after-minus-before median delta (null
percentage for zero baseline). Lower/higher desirability depends on the metric.
Keep raw files and provenance; manually confirm equivalent hardware, build flags,
counters and boundary. Do not mix cold/warm, frame/trial averages, or unrelated
populations. For interleaved trials compare each matched population and retain
trial IDs/order; pooling hides drift and autocorrelation. Few samples produce
unstable tails. This tool intentionally makes no significance or causality claim.

Anchor manifests use `repository` (reviewed origin URL), full `commit`, and
`anchors` containing checkout-relative `path` plus literal `contains` symbol.
Null provenance, revision mismatch, dirty checkout, missing paths or symbols fail
with a nonzero exit code. Exact origin URL comparison is conservative: review
transport aliases explicitly instead of silently accepting another repository.
The shipped manifest is an unverified historical seed, not a certified snapshot.
On failure rediscover the current files/symbols and relevant semantics, then
write a refreshed manifest outside the skill; never just copy HEAD to make it pass.
