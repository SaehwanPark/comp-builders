# Examples

The `examples/` directory contains small deterministic workflows that can be read as documentation and executed by the test suite.

## API workflow

`examples/api_workflow.py` demonstrates request parsing and persistence-like orchestration with `Result`.

Core flow:

1. Parse a JSON request body.
2. Read required string fields.
3. Validate the email shape.
4. Return a persisted `UserRecord` or the first error.

## ETL job

`examples/etl_job.py` demonstrates extract-transform-load sequencing with `Result`.

Core flow:

1. Extract rows from an iterable source.
2. Validate and normalize numeric amounts.
3. Load rows into a deterministic summary object.

## ML-style pipeline

`examples/ml_pipeline.py` demonstrates combining `Result` for dependent numeric processing with `Option` for optional metadata.

Core flow:

1. Load required numeric features.
2. Normalize feature values.
3. Derive a deterministic label and score.
4. Attach an optional note when metadata is present.

Run all examples through the test suite:

```bash
uv run pytest
```
