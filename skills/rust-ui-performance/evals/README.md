# Skill behavior evaluation

`evals.json` follows Agent Skills evaluation guidance: prompts, expected output,
optional input files and observable assertions. It is not a standardized execution
API. Cases include adversarial optimization requests and justified investigation/
review requests; refusal to optimize everything is not the only success behavior.

Run each case in a fresh Codex session with this skill installed or explicitly
provided. Repeat against the previous skill or without the skill, using the same
model, tools and target checkout/fixtures. Save transcripts, source diffs and
outputs outside the skill, e.g. `/tmp/rust-perf-evals/iteration-1/case-1/with_skill/`.
For cases lacking a real target, the correct behavior is to identify missing
measurement/architecture evidence, not invent stacks or benchmark results.
For implementation-sensitive cases, supply a disposable application fixture or
checkout and inspect actual edits/tool calls, not just the final response.

Grade each assertion against the trace/output. Save `grading.json` with
`assertion_results` entries `{text, passed, evidence}`. Require a concrete quote,
artifact or tool action for each pass; fabricated measurements and unauthorized
source edits are hard failures. Report unavailable tools separately from behavior
failures. Do not grade by keyword matching: mentioning “profile” while making a
blanket rewrite fails. Use repeat runs and human review for ambiguous judgments.

`python3 tests/validate_repository.py` from the repository root validates suite
shape and resources; it does **not** run or grade behavioral sessions. Unit tests
exercise deterministic tooling. No behavioral pass rate should be reported until
fresh agent runs and their evidence-based grades have actually been collected.
