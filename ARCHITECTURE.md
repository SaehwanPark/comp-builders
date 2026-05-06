# Architecture

`comp-builders` is intentionally small. The package is organized around a generic generator runner plus concrete context types.

## Module layout

```text
comp_builders/
  builder.py        generic generator-driven Builder
  result.py         Result, Ok, Err, ResultBuilder, result
  option.py         Option, Some, Nothing, OptionBuilder, option
  async_result.py   AsyncResult, AsyncResultBuilder, async_result
  validation.py     Validation, Valid, Invalid, ValidationBuilder, validation
  __init__.py       public package exports
  py.typed          typing marker
```

## Control flow

A decorated block is a normal Python function. When the function contains `yield`, Python creates a generator. The builder drives that generator, receives each yielded context value, and decides what to send back.

```text
@result.block function
  -> generator yields Ok(value)
  -> ResultBuilder sends value back
  -> generator yields Err(error)
  -> ResultBuilder returns Err(error) without continuing
```

`OptionBuilder` follows the same shape with `Some` and `Nothing`. `ValidationBuilder` differs because it keeps running after `Invalid` values and accumulates errors. `AsyncResultBuilder` awaits each yielded `AsyncResult` before deciding whether to continue.

## Design principles

- Keep runtime dependencies at zero.
- Prefer explicit values over hidden side channels for expected failures.
- Preserve Python syntax and standard debugging behavior as much as possible.
- Keep public exports small and stable.
- Provide enough typing information for strict mypy projects while acknowledging current generator-yield inference limits.
