# User Guide

`comp-builders` helps you write workflows where each step returns a context value such as `Result`, `Option`, `AsyncResult`, or `Validation`. Builder blocks unwrap successful values and handle failure behavior consistently.

## Result workflows

Use `Result[T, E]` when a step can either produce a value of type `T` or fail with an error of type `E`.

```python
from comp_builders import Err, Ok, Result, result


def parse_amount(raw: str) -> Result[float, str]:
  try:
    return Ok(float(raw))
  except ValueError:
    return Err("amount must be numeric")


def require_positive(amount: float) -> Result[float, str]:
  return Ok(amount) if amount > 0 else Err("amount must be positive")


@result.block
def read_amount(raw: str):
  amount = yield parse_amount(raw)
  return yield require_positive(amount)
```

Behavior:

- `Ok(value)` is unwrapped and assigned to the left-hand side of `yield`.
- `Err(error)` stops the block immediately and returns that `Err`.
- A normal `return value` is wrapped as `Ok(value)`.

## Option workflows

Use `Option[T]` when a value may be absent and absence is expected, not exceptional.

```python
from comp_builders import Nothing, Option, Some, option


def get_name(user: dict[str, str]) -> Option[str]:
  name = user.get("name")
  return Some(name) if name else Nothing


@option.block
def greeting(user: dict[str, str]):
  name = yield get_name(user)
  return f"Hello, {name}!"
```

Behavior:

- `Some(value)` is unwrapped.
- `Nothing` stops the block and returns `Nothing`.
- A normal `return value` is wrapped as `Some(value)`.

## AsyncResult workflows

Use `AsyncResult[T, E]` when each step is awaitable and returns a `Result`.

```python
import asyncio
from comp_builders import AsyncResult, Err, Ok, Result, async_result


async def fetch_user(user_id: str) -> Result[dict[str, str], str]:
  if user_id == "missing":
    return Err("user not found")
  return Ok({"id": user_id, "name": "Ada"})


@async_result.block
def load_user_name(user_id: str):
  user = yield AsyncResult.from_awaitable(fetch_user(user_id))
  return user["name"]


assert asyncio.run(load_user_name("u-1")) == Ok("Ada")
```

Notes:

- `async_result.block` decorates a normal generator function, not an `async def` function.
- Coroutine-backed `AsyncResult` values are single-await. Recreate them when repeating a workflow.

## Validation workflows

Use `Validation[T, E]` when checks are independent and users benefit from seeing all errors at once.

```python
from comp_builders import Invalid, Valid, validation


def require_present(data: dict[str, str], key: str):
  value = data.get(key, "").strip()
  return Valid(value) if value else Invalid(f"missing {key}")


@validation.block
def validate_signup(data: dict[str, str]):
  name = yield require_present(data, "name")
  email = yield require_present(data, "email")
  yield Valid(email) if "@" in email else Invalid("invalid email")
  return {"name": name, "email": email}
```

Behavior:

- `Valid(value)` is unwrapped.
- `Invalid(errors)` is collected, and the block continues.
- When any invalid values were seen, the final result is `Invalid((...errors))`.
- When yielding `Invalid`, the value sent back into the generator is `None`; use validation blocks for independent checks rather than dependent transformations.

## Typing guidance

Strict type checkers cannot always infer the exact value sent back from a generator `yield`. For larger functions, annotate the generator return type or use `typing.cast` at binding points.

```python
from collections.abc import Generator
from typing import Any, cast
from comp_builders import Result, result


@result.block
def workflow(raw: str) -> Generator[Result[Any, str], object, str]:
  value = cast(str, (yield read_user_id(raw)))
  return value.upper()
```

## Choosing a context

| Need | Use |
| --- | --- |
| Stop at first explicit failure | `Result` |
| Stop when a value is absent | `Option` |
| Await result-returning async work | `AsyncResult` |
| Collect independent validation errors | `Validation` |

## Examples

The `examples/` directory includes deterministic examples for API-style request handling, ETL jobs, and ML-style prediction pipelines. Run the full suite with:

```bash
uv run pytest
```
