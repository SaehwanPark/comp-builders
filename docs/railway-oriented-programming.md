# Railway-Oriented Programming for Python Users

Railway-oriented programming is a gentle way to structure workflows that can fail. Imagine a railway with two tracks: a success track and a failure track. Each step receives a value from the success track, does some work, and either keeps the workflow on the success track or moves it to the failure track. Once a workflow is on the failure track, later success-only steps are skipped.

This idea is common in functional programming, but it is useful in everyday Python code too. It helps make failure explicit, keeps the happy path readable, and avoids spreading repeated error checks across a function.

## Why it matters

Python gives you several ways to represent failure: exceptions, `None`, booleans, sentinel values, and custom objects. Each can be appropriate. The problem appears when a workflow combines many steps and every step has a different failure convention.

Railway-oriented programming encourages a consistent return shape:

- `Ok(value)` means continue with `value`.
- `Err(error)` means stop and return the error.
- `Some(value)` means continue with an optional value.
- `Nothing` means stop because the value is absent.
- `Valid(value)` means a validation check passed.
- `Invalid(errors)` means collect validation problems.

The benefit is not only fewer lines. The larger benefit is that the function contract tells readers where failure can happen.

## What it looks like in functional languages

In F#, a `Result` pipeline often looks like this:

```fsharp
let createUser raw =
  raw
  |> parseJson
  |> Result.bind readUserId
  |> Result.bind saveUser
```

In Haskell-like pseudocode, the same shape often appears in `do` notation:

```haskell
createUser raw = do
  payload <- parseJson raw
  userId <- readUserId payload
  saveUser userId
```

Both examples do the same thing: unwrap the successful value at each step, then automatically stop if a step returns a failure.

## Traditional Python without railway-oriented programming

A conventional Python workflow often checks after each step:

```python
def create_user(raw: str):
  parsed = parse_json(raw)
  if isinstance(parsed, Err):
    return parsed

  user_id = read_user_id(parsed.value)
  if isinstance(user_id, Err):
    return user_id

  saved = save_user(user_id.value)
  if isinstance(saved, Err):
    return saved

  return saved
```

This is explicit, but the control flow can become noisy. The business logic is mixed with repeated plumbing.

Exception-based code can make the happy path shorter:

```python
def create_user(raw: str):
  payload = parse_json_or_raise(raw)
  user_id = read_user_id_or_raise(payload)
  return save_user_or_raise(user_id)
```

That can be a good fit for truly exceptional failures. But for expected domain outcomes such as invalid input, missing records, or validation errors, explicit return values can be easier to test and document.

## Python with `comp-builders`

`comp-builders` uses normal Python generators to provide a compact workflow syntax.

```python
from comp_builders import Err, Ok, Result, result


def parse_json(raw: str) -> Result[dict[str, str], str]:
  if not raw.startswith("{"):
    return Err("invalid json")
  return Ok({"user_id": "ada"})


def read_user_id(payload: dict[str, str]) -> Result[str, str]:
  user_id = payload.get("user_id", "").strip()
  return Ok(user_id) if user_id else Err("missing user id")


def save_user(user_id: str) -> Result[str, str]:
  return Ok(user_id.upper())


@result.block
def create_user(raw: str):
  payload = yield parse_json(raw)
  user_id = yield read_user_id(payload)
  return yield save_user(user_id)
```

Inside a `@result.block` function:

1. The function yields a `Result`.
2. If the value is `Ok(value)`, the builder sends `value` back into the function.
3. If the value is `Err(error)`, the builder stops the function and returns that error.
4. A final `return value` becomes `Ok(value)`.

## A side-by-side comparison

### Without `comp-builders`

```python
def normalize_email(raw: str):
  stripped = strip_email(raw)
  if isinstance(stripped, Err):
    return stripped

  lower = lowercase_email(stripped.value)
  if isinstance(lower, Err):
    return lower

  checked = require_at_sign(lower.value)
  if isinstance(checked, Err):
    return checked

  return Ok(checked.value)
```

### With `comp-builders`

```python
@result.block
def normalize_email(raw: str):
  stripped = yield strip_email(raw)
  lower = yield lowercase_email(stripped)
  return yield require_at_sign(lower)
```

The second version keeps the same explicit `Result` contract while removing repeated short-circuit plumbing.

## When to use each builder

### Use `Result` for dependent workflows

Choose `Result` when step two depends on the successful value from step one.

```python
@result.block
def checkout(cart_id: str):
  cart = yield load_cart(cart_id)
  total = yield calculate_total(cart)
  return yield charge_customer(total)
```

### Use `Option` for expected absence

Choose `Option` when missing data is normal and should stop the current workflow.

```python
@option.block
def display_name(profile: dict[str, object]):
  name = yield profile.get("name", Nothing)
  return name.strip().title()
```

### Use `AsyncResult` for awaitable result workflows

Choose `AsyncResult` when operations are asynchronous but still return explicit `Result` values.

```python
@async_result.block
def load_profile(user_id: str):
  user = yield AsyncResult.from_awaitable(fetch_user(user_id))
  settings = yield AsyncResult.from_awaitable(fetch_settings(user["id"]))
  return {"user": user, "settings": settings}
```

### Use `Validation` for independent checks

Choose `Validation` when you want all validation errors at once.

```python
@validation.block
def validate_form(data: dict[str, str]):
  name = yield require_present(data, "name")
  email = yield require_present(data, "email")
  yield require_email_shape(email)
  return {"name": name, "email": email}
```

## Practical guidance

Railway-oriented programming is most helpful at application boundaries and workflow seams: parsing, validation, ETL steps, API handlers, data quality checks, and service orchestration. It is less useful for tiny functions where an ordinary expression is already clear.

A good rule of thumb: use a builder block when three or more steps share the same failure convention and repeated checks are starting to obscure the main workflow.
