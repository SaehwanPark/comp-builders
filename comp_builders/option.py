"""Option context and builder."""

from __future__ import annotations

from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Any, Generic, NoReturn, ParamSpec, TypeVar, cast, overload

from comp_builders.builder import Builder

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")


class Option(Generic[T]):
  """Base type for computations that may not produce a value."""

  def map(self, fn: Callable[[T], U]) -> Option[U]:
    """Transform the present value, preserving absence."""
    raise NotImplementedError

  def bind(self, fn: Callable[[T], Option[U]]) -> Option[U]:
    """Sequence another option-returning computation."""
    raise NotImplementedError

  @classmethod
  def pure(cls, value: U) -> Option[U]:
    """Lift a value into an option."""
    return Some(value)


@dataclass(frozen=True)
class Some(Option[T]):
  """Present option value."""

  value: T

  def map(self, fn: Callable[[T], U]) -> Option[U]:
    return Some(fn(self.value))

  def bind(self, fn: Callable[[T], Option[U]]) -> Option[U]:
    return fn(self.value)


@dataclass(frozen=True)
class _Nothing(Option[NoReturn]):
  """Absent option value."""

  def map(self, fn: Callable[[NoReturn], U]) -> Option[U]:
    return cast(Option[U], self)

  def bind(self, fn: Callable[[NoReturn], Option[U]]) -> Option[U]:
    return cast(Option[U], self)


Nothing = _Nothing()


class OptionBuilder(Builder):
  """Builder that sequences `Option` computations."""

  @overload
  def block(
    self, func: Callable[P, Generator[Option[Any], Any, T]]
  ) -> Callable[P, Option[T]]: ...

  @overload
  def block(self, func: Callable[P, T]) -> Callable[P, Option[T]]: ...

  # The concrete builder intentionally wraps the base return type.
  def block(self, func: Callable[P, Any]) -> Callable[P, Option[Any]]:
    return super().block(func)

  def bind(self, computation: Option[T]) -> T:
    match computation:
      case Some(value):
        return cast(T, value)
      case _Nothing():
        raise _OptionShortCircuit
      case _:
        raise TypeError(
          "option blocks can only yield Option values; "
          f"got {type(computation).__name__}"
        )

  def pure(self, value: T) -> Option[T]:  # type: ignore[override]
    return Some(value)

  def _run(  # type: ignore[override]
    self, gen: Generator[Option[Any], Any, T]
  ) -> Option[T]:
    try:
      return cast(Option[T], super()._run(gen))
    except _OptionShortCircuit:
      return cast(Option[T], Nothing)


class _OptionShortCircuit(Exception):
  """Internal signal used to stop an option block."""


option = OptionBuilder()
