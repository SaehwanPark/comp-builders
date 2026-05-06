"""Async Result context and builder."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Generator
from functools import wraps
from inspect import iscoroutinefunction, isgeneratorfunction
from typing import Any, Generic, NoReturn, ParamSpec, TypeVar, cast, overload

from comp_builders.result import Err, Ok, Result

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")
F = TypeVar("F")


class AsyncResult(Generic[T, E]):
  """Awaitable result for computations that can fail asynchronously."""

  def __init__(self, awaitable: Awaitable[Result[T, E]]) -> None:
    self._awaitable = awaitable

  def __await__(self) -> Generator[Any, None, Result[T, E]]:
    return self._awaitable.__await__()

  def map(self, fn: Callable[[T], U]) -> AsyncResult[U, E]:
    """Transform the eventual success value, preserving errors."""

    async def mapped() -> Result[U, E]:
      result = await self
      return result.map(fn)

    return AsyncResult(mapped())

  def bind(self, fn: Callable[[T], AsyncResult[U, F]]) -> AsyncResult[U, E | F]:
    """Sequence another async-result computation."""

    async def bound() -> Result[U, E | F]:
      result = await self
      match result:
        case Ok(value):
          return cast(Result[U, E | F], await fn(cast(T, value)))
        case Err(error):
          return Err[U, E | F](error)
      raise TypeError(f"unexpected result value: {type(result).__name__}")

    return AsyncResult(bound())

  @classmethod
  def pure(cls, value: U) -> AsyncResult[U, NoReturn]:
    """Lift a value into a successful async result."""

    async def completed() -> Result[U, NoReturn]:
      return Ok(value)

    return AsyncResult(completed())

  @classmethod
  def from_result(cls, result: Result[U, F]) -> AsyncResult[U, F]:
    """Lift an already-computed result into an async result."""

    async def completed() -> Result[U, F]:
      return result

    return AsyncResult(completed())

  @classmethod
  def from_awaitable(cls, awaitable: Awaitable[Result[U, F]]) -> AsyncResult[U, F]:
    """Wrap an awaitable that resolves to a result."""
    return AsyncResult(awaitable)


class AsyncResultBuilder:
  """Builder that sequences `AsyncResult` computations."""

  @overload
  def block(  # type: ignore[overload-overlap]
    self, func: Callable[P, Generator[AsyncResult[Any, E], Any, T]]
  ) -> Callable[P, AsyncResult[T, E]]: ...

  @overload
  def block(self, func: Callable[P, T]) -> Callable[P, AsyncResult[T, NoReturn]]: ...

  def block(self, func: Callable[P, Any]) -> Callable[P, AsyncResult[Any, Any]]:
    """Decorate a normal generator function as an async-result block."""
    if iscoroutinefunction(func):
      raise TypeError(
        "async_result.block does not support async def functions; "
        "use a normal generator function that yields AsyncResult values"
      )

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> AsyncResult[Any, Any]:
      if not isgeneratorfunction(func):
        return self.pure(func(*args, **kwargs))

      generator = cast(
        Generator[AsyncResult[Any, Any], Any, Any], func(*args, **kwargs)
      )
      return AsyncResult(self._run(generator))

    return wrapper

  def pure(self, value: T) -> AsyncResult[T, NoReturn]:
    """Wrap the final value produced by an async-result block."""
    return AsyncResult.pure(value)

  async def _run(self, gen: Generator[AsyncResult[Any, E], Any, T]) -> Result[T, E]:
    sent_value: object = None

    while True:
      try:
        yielded = gen.send(sent_value)
      except StopIteration as stop:
        return Ok(cast(T, stop.value))

      if not isinstance(yielded, AsyncResult):
        raise TypeError(
          "async_result blocks can only yield AsyncResult values; "
          f"got {type(yielded).__name__}"
        )

      result = await yielded
      match result:
        case Ok(value):
          sent_value = value
        case Err(error):
          return Err(cast(E, error))


async_result = AsyncResultBuilder()
