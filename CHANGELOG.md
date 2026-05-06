# Changelog

## 1.0.0 - 2026-05-06

### Added

- Public `Result`, `Option`, `AsyncResult`, and `Validation` context types.
- Generator-based builders for readable railway-oriented workflows.
- Typed package marker and strict typing checks for the public API.
- Runnable examples for API workflows, ETL jobs, and ML-style pipelines.
- First-time-user documentation: README, quickstart, user guide, API reference, and railway-oriented programming guide.
- Apache 2.0 license and public repository packaging metadata.

### Notes

- `async_result.block` supports normal generator functions that yield `AsyncResult` values. It intentionally rejects `async def` functions.
- Strict type checkers may need explicit generator annotations or `typing.cast` at yield binding points.
- Coroutine-backed `AsyncResult` values are single-await and should be recreated for repeated runs.
