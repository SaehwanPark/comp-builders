"""Validation context and builder."""

from __future__ import annotations

from collections.abc import Callable, Generator, Iterable
from dataclasses import dataclass
from functools import wraps
from inspect import isgeneratorfunction
from typing import Any, Generic, NoReturn, ParamSpec, TypeVar, cast, overload

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")
F = TypeVar("F")


class Validation(Generic[T, E]):
  """Base type for computations that can accumulate validation errors."""

  def map(self, fn: Callable[[T], U]) -> Validation[U, E]:
    """Transform the valid value, preserving errors."""
    raise NotImplementedError

  def bind(self, fn: Callable[[T], Validation[U, F]]) -> Validation[U, E | F]:
    """Sequence another validation-returning computation."""
    raise NotImplementedError

  @classmethod
  def pure(cls, value: U) -> Validation[U, NoReturn]:
    """Lift a value into a valid result."""
    return Valid(value)


@dataclass(frozen=True)
class Valid(Validation[T, E]):
  """Successful validation value."""

  value: T

  def map(self, fn: Callable[[T], U]) -> Validation[U, E]:
    return Valid[U, E](fn(self.value))

  def bind(self, fn: Callable[[T], Validation[U, F]]) -> Validation[U, E | F]:
    return cast(Validation[U, E | F], fn(self.value))


@dataclass(frozen=True)
class Invalid(Validation[T, E]):
  """Failed validation with one or more accumulated errors."""

  errors: tuple[E, ...]

  def __init__(self, errors: Iterable[E] | E) -> None:
    normalized: tuple[E, ...]
    if isinstance(errors, str):
      normalized = (cast(E, errors),)
    else:
      try:
        normalized = tuple(cast(Iterable[E], errors))
      except TypeError:
        normalized = (cast(E, errors),)

    object.__setattr__(self, "errors", normalized)

  def map(self, fn: Callable[[T], U]) -> Validation[U, E]:
    return Invalid[U, E](self.errors)

  def bind(self, fn: Callable[[T], Validation[U, F]]) -> Validation[U, E | F]:
    return Invalid[U, E | F](self.errors)


class ValidationBuilder:
  """Builder that accumulates `Validation` errors."""

  @overload
  def block(  # type: ignore[overload-overlap]
    self, func: Callable[P, Generator[Validation[Any, E], Any, T]]
  ) -> Callable[P, Validation[T, E]]: ...

  @overload
  def block(self, func: Callable[P, T]) -> Callable[P, Validation[T, NoReturn]]: ...

  def block(self, func: Callable[P, Any]) -> Callable[P, Validation[Any, Any]]:
    """Decorate a function as a generator-driven validation block."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Validation[Any, Any]:
      if not isgeneratorfunction(func):
        return self.pure(func(*args, **kwargs))

      generator = cast(Generator[Validation[Any, Any], Any, Any], func(*args, **kwargs))
      return self._run(generator)

    return wrapper

  def pure(self, value: T) -> Validation[T, NoReturn]:
    """Wrap the final value produced by a validation block."""
    return Valid(value)

  def _run(self, gen: Generator[Validation[Any, E], Any, T]) -> Validation[T, E]:
    sent_value: object = None
    errors: list[E] = []
    saw_invalid = False

    while True:
      try:
        yielded = gen.send(sent_value)
      except StopIteration as stop:
        if saw_invalid:
          return Invalid(errors)
        return Valid(cast(T, stop.value))

      match yielded:
        case Valid(value):
          sent_value = value
        case Invalid(invalid_errors):
          saw_invalid = True
          errors.extend(cast(tuple[E, ...], invalid_errors))
          sent_value = None
        case _:
          raise TypeError(
            "validation blocks can only yield Validation values; "
            f"got {type(yielded).__name__}"
          )


validation = ValidationBuilder()
