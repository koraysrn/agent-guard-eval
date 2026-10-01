# Risk Inventory and Antidotes

This document lists the operational, correctness and security risks of the
`agent-guard-eval` numeric validation layer together with the mitigation implemented for
each. The same table is summarized in the project README.

| # | Risk / Threat | Impact | Antidote (implemented) |
|---|---|---|---|
| 1 | Regex ReDoS (catastrophic backtracking) | Denial of service via crafted text | Backtracking-free patterns, pre-compiled regexes, `max_input_chars` bound, size guard in [`SafeRegex`](src/agent_guard_eval/extractors/base.py) |
| 2 | False positive ("I am 100% sure") | Legitimate text wrongly blocked | Value is only compared after a key is matched by a matcher; stray numbers are ignored by default (`report_unexpected=False`) |
| 3 | False negative (unrecognized format) | Bad value slips through | Four typed extractors + scientific notation + locale separators + golden regression set |
| 4 | Float precision (0.1 + 0.2 != 0.3) | Spurious rejections | Central `atol + rtol` tolerance formula |
| 5 | Locale difference (1.234,56 vs 1,234.56) | Wrong parse | Configurable `decimal_sep` / `thousands_sep` normalization |
| 6 | Wrong currency conversion | Silent value corruption | Conversion only with explicit `exchange_rates`; missing rate raises `GuardComparisonError` |
| 7 | Percent/ratio confusion (0.15 vs 15%) | Off-by-100 errors | Dedicated `PercentageComparator` and `percent_as_fraction` switch |
| 8 | Scientific notation (1.5e-3) | Misparsed values | Scientific notation supported by `NumberExtractor` |
| 9 | Negative number formats (-$5.00) | Wrong sign | Signed patterns in number and currency extractors |
| 10 | Zero reference value | Division-by-zero in relative error | `compute_errors` returns `None` relative error; `atol` is the only bound |
| 11 | Missing key in text | Silent acceptance | `MISSING` violation when `strict_missing=True` |
| 12 | Reference key never appears | Blind spot | `UNMATCHED_REFERENCE`/`MISSING` violation surfaced in details |
| 13 | Key collision (one number near two keys) | Ambiguous assignment | Matcher priority: label > proximity > fuzzy; deterministic ordering |
| 14 | Context confusion (year "2024" as metric) | Wrong value matched | Key-driven matching: numbers only matter near a reference key |
| 15 | Bad configuration (negative tolerance) | Weakened validation | `GuardConfig.__post_init__` validation raises `GuardConfigurationError` |
| 16 | Invalid input type (None, non-string) | Crash | `GuardInputError` raised early in `validate` |
| 17 | Oversized input (DoS) | Resource exhaustion | `max_input_chars` enforced before extraction |
| 18 | Log injection / secret leakage | Credential disclosure | `RedactingFormatter` masks keys, tokens, passwords in logs |
| 19 | Raw text leak in diffs | Privacy | Diffs carry only the matched number and key, never the full text |
| 20 | Thread-safety hazards | Data races | Immutable (frozen) models and stateless guard design |
| 21 | Integration version mismatch | Import-time crash | Optional deps isolated behind `ImportError` guards in `integrations` |
| 22 | Regression from regex changes | Silent behavior change | Golden regression dataset + full unit suite in CI |
| 23 | Unicode/normalization drift | Missed matches | Unicode-aware word boundaries; explicit symbol tables |
| 24 | Overly wide `rtol` | Everything passes | `max_rtol` upper bound in config validation |
| 25 | Non-determinism (LLM in the loop) | Unreproducible verdicts | Architecture constraint: no LLM calls anywhere in `src/` |

## Operational guidance

- Pin `atol`/`rtol` per domain (finance favors tight tolerances; statistics often wider).
- Keep `exchange_rates` explicit and audited; never infer rates implicitly.
- Enable `report_unexpected=True` only when callers must see every stray number.
- Treat `GuardComparisonError` (missing exchange rate) as a configuration bug, not as a
  validation pass.
