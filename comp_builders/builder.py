"""Generator-driven builder blocks."""

from collections.abc import Callable, Generator
from functools import wraps
from inspect import isgeneratorfunction
from typing import Any, ParamSpec, TypeVar, cast

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")


class Builder:
  """Drive generator-based computation expression blocks."""

  def bind(self, computation: Any) -> Any:
    """Extract the value sent back into a builder block."""
    return computation

  def pure(self, value: T) -> T:
    """Wrap the final value produced by a builder block."""
    return value

  def block(self, func: Callable[P, Any]) -> Callable[P, Any]:
    """Decorate a function as a generator-driven builder block."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
      if not isgeneratorfunction(func):
        return self.pure(func(*args, **kwargs))

      generator = cast(Generator[Any, Any, Any], func(*args, **kwargs))
      return self._run(generator)

    return wrapper

  def _run(self, gen: Generator[U, Any, T]) -> T:
    sent_value: object = None

    while True:
      try:
        yielded = gen.send(sent_value)
      except StopIteration as stop:
        return self.pure(cast(T, stop.value))

      sent_value = self.bind(yielded)


builder = Builder()
