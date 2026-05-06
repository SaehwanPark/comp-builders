"""Result context and builder."""

from __future__ import annotations

from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Any, Generic, NoReturn, ParamSpec, TypeVar, cast, overload

from comp_builders.builder import Builder

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")
F = TypeVar("F")


class Result(Generic[T, E]):
  """Base type for computations that can succeed or fail."""

  def map(self, fn: Callable[[T], U]) -> Result[U, E]:
    """Transform the success value, preserving errors."""
    raise NotImplementedError

  def bind(self, fn: Callable[[T], Result[U, F]]) -> Result[U, E | F]:
    """Sequence another result-returning computation."""
    raise NotImplementedError

  @classmethod
  def pure(cls, value: U) -> Result[U, NoReturn]:
    """Lift a value into a successful result."""
    return Ok(value)


@dataclass(frozen=True)
class Ok(Result[T, E]):
  """Successful result value."""

  value: T

  def map(self, fn: Callable[[T], U]) -> Result[U, E]:
    return Ok[U, E](fn(self.value))

  def bind(self, fn: Callable[[T], Result[U, F]]) -> Result[U, E | F]:
    return cast(Result[U, E | F], fn(self.value))


@dataclass(frozen=True)
class Err(Result[T, E]):
  """Failed result value."""

  error: E

  def map(self, fn: Callable[[T], U]) -> Result[U, E]:
    return Err[U, E](self.error)

  def bind(self, fn: Callable[[T], Result[U, F]]) -> Result[U, E | F]:
    return Err[U, E | F](self.error)


class ResultBuilder(Builder):
  """Builder that sequences `Result` computations."""

  @overload
  def block(  # type: ignore[overload-overlap]
    self, func: Callable[P, Generator[Result[Any, E], Any, T]]
  ) -> Callable[P, Result[T, E]]: ...

  @overload
  def block(self, func: Callable[P, T]) -> Callable[P, Result[T, NoReturn]]: ...

  # The concrete builder intentionally wraps the base return type.
  def block(self, func: Callable[P, Any]) -> Callable[P, Result[Any, Any]]:
    return super().block(func)

  def bind(self, computation: Result[T, E]) -> T:
    match computation:
      case Ok(value):
        return cast(T, value)
      case Err(error):
        raise _ResultShortCircuit(error)
      case _:
        raise TypeError(
          "result blocks can only yield Result values; "
          f"got {type(computation).__name__}"
        )

  def pure(self, value: T) -> Result[T, NoReturn]:  # type: ignore[override]
    return Ok(value)

  def _run(  # type: ignore[override]
    self, gen: Generator[Result[Any, E], Any, T]
  ) -> Result[T, E]:
    try:
      return cast(Result[T, E], super()._run(gen))
    except _ResultShortCircuit as short_circuit:
      return Err(cast(E, short_circuit.error))


class _ResultShortCircuit(Exception):
  """Internal signal used to stop a result block."""

  def __init__(self, error: object) -> None:
    self.error = error


result = ResultBuilder()
