# API Reference

This page documents the public API exported from `comp_builders`.

## Package exports

```python
from comp_builders import (
  AsyncResult,
  AsyncResultBuilder,
  Builder,
  Err,
  Invalid,
  Nothing,
  Ok,
  Option,
  OptionBuilder,
  Result,
  ResultBuilder,
  Some,
  Valid,
  Validation,
  ValidationBuilder,
  async_result,
  builder,
  option,
  result,
  validation,
)
```

## Result

### `Result[T, E]`

Base type for computations that can succeed with `T` or fail with `E`.

Methods:

- `map(fn: Callable[[T], U]) -> Result[U, E]`
- `bind(fn: Callable[[T], Result[U, F]]) -> Result[U, E | F]`
- `pure(value: U) -> Result[U, NoReturn]`

### `Ok(value: T)`

Successful result value. Supports dataclass equality, representation, and structural pattern matching.

### `Err(error: E)`

Failed result value. Supports dataclass equality, representation, and structural pattern matching.

### `ResultBuilder` and `result`

`result` is the default `ResultBuilder` instance.

- `result.block(func)` decorates a generator-driven result workflow.
- `result.pure(value)` returns `Ok(value)`.
- Yielding `Ok(value)` sends `value` back into the generator.
- Yielding `Err(error)` short-circuits and returns `Err(error)`.

## Option

### `Option[T]`

Base type for computations that may produce a value.

Methods:

- `map(fn: Callable[[T], U]) -> Option[U]`
- `bind(fn: Callable[[T], Option[U]]) -> Option[U]`
- `pure(value: U) -> Option[U]`

### `Some(value: T)`

Present option value.

### `Nothing`

Singleton absent option value.

### `OptionBuilder` and `option`

`option` is the default `OptionBuilder` instance.

- `option.block(func)` decorates a generator-driven option workflow.
- `option.pure(value)` returns `Some(value)`.
- Yielding `Some(value)` sends `value` back into the generator.
- Yielding `Nothing` short-circuits and returns `Nothing`.

## AsyncResult

### `AsyncResult[T, E]`

Awaitable wrapper around `Result[T, E]` for asynchronous computations.

Methods:

- `__await__()`: awaiting an `AsyncResult` returns a `Result[T, E]`.
- `map(fn: Callable[[T], U]) -> AsyncResult[U, E]`
- `bind(fn: Callable[[T], AsyncResult[U, F]]) -> AsyncResult[U, E | F]`
- `pure(value: U) -> AsyncResult[U, NoReturn]`
- `from_result(result: Result[U, F]) -> AsyncResult[U, F]`
- `from_awaitable(awaitable: Awaitable[Result[U, F]]) -> AsyncResult[U, F]`

### `AsyncResultBuilder` and `async_result`

`async_result` is the default `AsyncResultBuilder` instance.

- `async_result.block(func)` decorates a normal generator function that yields `AsyncResult` values.
- `async_result.pure(value)` returns an awaitable successful result.
- `async def` functions are intentionally rejected by `async_result.block`; use a normal generator function and yield `AsyncResult` values.

## Validation

### `Validation[T, E]`

Base type for computations that can accumulate validation errors.

Methods:

- `map(fn: Callable[[T], U]) -> Validation[U, E]`
- `bind(fn: Callable[[T], Validation[U, F]]) -> Validation[U, E | F]`
- `pure(value: U) -> Validation[U, NoReturn]`

### `Valid(value: T)`

Successful validation value.

### `Invalid(errors: Iterable[E] | E)`

Failed validation containing one or more errors. String inputs are treated as a single error rather than an iterable of characters.

### `ValidationBuilder` and `validation`

`validation` is the default `ValidationBuilder` instance.

- `validation.block(func)` decorates a generator-driven validation workflow.
- `validation.pure(value)` returns `Valid(value)`.
- Yielding `Valid(value)` sends `value` back into the generator.
- Yielding `Invalid(errors)` accumulates errors and continues execution.

## Base Builder

### `Builder` and `builder`

`Builder` is the generic generator runner used by concrete builders.

Methods:

- `block(func)` decorates a generator-driven workflow.
- `bind(computation)` defines how yielded values are unwrapped.
- `pure(value)` defines how returned values are wrapped.

Most users should use `result`, `option`, `async_result`, or `validation` directly.
