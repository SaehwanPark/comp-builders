# Quickstart

This guide gets you from a fresh checkout to a working `Result` workflow in about five minutes.

## 1. Install

From an application project:

```bash
uv add comp-builders
```

From this repository:

```bash
git clone https://github.com/your-org/comp-builders.git
cd comp-builders
uv sync --all-groups
```

## 2. Write a small result-returning function

```python
from comp_builders import Err, Ok, Result


def read_user_id(raw: str) -> Result[str, str]:
  user_id = raw.strip()
  if not user_id:
    return Err("missing user id")
  return Ok(user_id)
```

## 3. Sequence it with a builder block

```python
from comp_builders import result


@result.block
def normalize_user_id(raw: str):
  user_id = yield read_user_id(raw)
  return user_id.upper()
```

## 4. Run it

```python
assert normalize_user_id(" ada ") == Ok("ADA")
assert normalize_user_id(" ") == Err("missing user id")
```

## 5. Run checks locally

```bash
uv run pytest
uv run mypy .
uv run ruff check .
```

## Next steps

Read the [User Guide](USER_GUIDE.md) for `Option`, `AsyncResult`, `Validation`, and larger workflow examples.
