import pytest

from comp_builders import AsyncResult, Err, Ok, async_result


async def ok_after(value: int) -> Ok[int, str]:
  return Ok(value)


def test_async_result_from_result_can_be_awaited() -> None:
  async def run() -> None:
    assert await AsyncResult.from_result(Ok(2)) == Ok(2)

  import asyncio

  asyncio.run(run())


def test_async_result_map_transforms_success_value() -> None:
  async def run() -> None:
    value = AsyncResult.from_result(Ok(2))

    assert await value.map(lambda item: item + 3) == Ok(5)

  import asyncio

  asyncio.run(run())


def test_async_result_bind_sequences_async_result_callback() -> None:
  async def run() -> None:
    value = AsyncResult.from_result(Ok(2))

    assert await value.bind(lambda item: AsyncResult.from_result(Ok(item + 3))) == Ok(5)

  import asyncio

  asyncio.run(run())


def test_async_result_bind_preserves_failure_without_callback() -> None:
  called = False

  async def run() -> None:
    value = AsyncResult.from_result(Err("invalid"))

    def fail(_item: int) -> AsyncResult[int, bool]:
      nonlocal called
      called = True
      return AsyncResult.from_result(Ok(1))

    assert await value.bind(fail) == Err("invalid")

  import asyncio

  asyncio.run(run())
  assert called is False


def test_async_result_builder_sequences_ok_values() -> None:
  @async_result.block
  def workflow():
    first = yield AsyncResult.from_awaitable(ok_after(2))
    second = yield AsyncResult.from_result(Ok(first + 3))
    return second * 2

  async def run() -> None:
    assert await workflow() == Ok(10)

  import asyncio

  asyncio.run(run())


def test_async_result_builder_short_circuits_on_err() -> None:
  reached = False

  @async_result.block
  def workflow():
    yield AsyncResult.from_result(Ok(2))
    yield AsyncResult.from_result(Err("invalid"))

    nonlocal reached
    reached = True
    return "unreachable"

  async def run() -> None:
    assert await workflow() == Err("invalid")

  import asyncio

  asyncio.run(run())
  assert reached is False


def test_async_result_builder_wraps_non_generator_return_value() -> None:
  @async_result.block
  def workflow():
    return 5

  async def run() -> None:
    assert await workflow() == Ok(5)

  import asyncio

  asyncio.run(run())


def test_async_result_builder_preserves_function_metadata() -> None:
  @async_result.block
  def workflow():
    """Workflow docstring."""
    return 5

  assert workflow.__name__ == "workflow"
  assert workflow.__doc__ == "Workflow docstring."


def test_async_result_builder_rejects_coroutine_functions() -> None:
  with pytest.raises(
    TypeError, match="async_result.block does not support async def functions"
  ):

    @async_result.block
    async def workflow():
      return 5


def test_async_result_builder_rejects_non_async_result_yields() -> None:
  @async_result.block
  def workflow():
    value = yield 5
    return value

  async def run() -> None:
    with pytest.raises(
      TypeError, match="async_result blocks can only yield AsyncResult values"
    ):
      await workflow()

  import asyncio

  asyncio.run(run())
