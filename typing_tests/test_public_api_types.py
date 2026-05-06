from collections.abc import Generator
from typing import Never, assert_type

from comp_builders import (
  AsyncResult,
  Err,
  Invalid,
  Nothing,
  Ok,
  Option,
  Result,
  Some,
  Valid,
  Validation,
  async_result,
  option,
  result,
  validation,
)


def result_map_preserves_error_type() -> None:
  value: Result[int, str] = Ok(2)

  assert_type(value.map(lambda item: str(item)), Result[str, str])


def result_bind_combines_error_types() -> None:
  value: Result[int, str] = Ok(2)

  assert_type(value.bind(lambda item: Ok(float(item))), Result[float, str])
  assert_type(value.bind(lambda item: Err(False)), Result[Never, str | bool])


def result_block_returns_result() -> None:
  @result.block
  def workflow() -> Generator[Result[int, str], object, str]:
    value = yield Ok(2)
    return str(value)

  assert_type(workflow(), Result[str, str])


def option_map_preserves_absence() -> None:
  value: Option[int] = Some(2)

  assert_type(value.map(lambda item: str(item)), Option[str])


def option_bind_preserves_option() -> None:
  value: Option[int] = Some(2)

  assert_type(value.bind(lambda item: Some(str(item))), Option[str])
  assert_type(Nothing.map(lambda item: item), Option[Never])


def option_block_returns_option() -> None:
  @option.block
  def workflow() -> Generator[Option[int], object, str]:
    value = yield Some(2)
    return str(value)

  assert_type(workflow(), Option[str])


def async_result_map_preserves_error_type() -> None:
  value: AsyncResult[int, str] = AsyncResult.from_result(Ok(2))

  assert_type(value.map(lambda item: str(item)), AsyncResult[str, str])


def async_result_bind_combines_error_types() -> None:
  value: AsyncResult[int, str] = AsyncResult.from_result(Ok(2))

  assert_type(
    value.bind(lambda item: AsyncResult.from_result(Ok(float(item)))),
    AsyncResult[float, str],
  )
  assert_type(
    value.bind(lambda item: AsyncResult.from_result(Err(False))),
    AsyncResult[Never, str | bool],
  )


def async_result_block_returns_async_result() -> None:
  @async_result.block
  def workflow() -> Generator[AsyncResult[int, str], object, str]:
    value = yield AsyncResult.from_result(Ok(2))
    return str(value)

  assert_type(workflow(), AsyncResult[str, str])


def validation_map_preserves_error_type() -> None:
  value: Validation[int, str] = Valid(2)

  assert_type(value.map(lambda item: str(item)), Validation[str, str])


def validation_bind_combines_error_types() -> None:
  value: Validation[int, str] = Valid(2)

  assert_type(value.bind(lambda item: Valid(float(item))), Validation[float, str])
  assert_type(
    value.bind(lambda item: Invalid[Never, bool]((False,))),
    Validation[Never, str | bool],
  )


def validation_block_returns_validation() -> None:
  @validation.block
  def workflow() -> Generator[Validation[int, str], object, str]:
    value = yield Valid(2)
    return str(value)

  assert_type(workflow(), Validation[str, str])
