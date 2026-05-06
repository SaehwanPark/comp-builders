import pytest

from comp_builders import Err, Ok, Result, result


def test_ok_map_transforms_success_value() -> None:
  assert Ok(2).map(lambda value: value + 3) == Ok(5)


def test_err_map_preserves_error_without_calling_callback() -> None:
  called = False

  def fail(_value):
    nonlocal called
    called = True

  assert Err("invalid").map(fail) == Err("invalid")
  assert called is False


def test_ok_bind_sequences_result_returning_callback() -> None:
  assert Ok(2).bind(lambda value: Ok(value + 3)) == Ok(5)


def test_err_bind_short_circuits_without_calling_callback() -> None:
  called = False

  def fail(_value):
    nonlocal called
    called = True
    return Ok("unreachable")

  assert Err("invalid").bind(fail) == Err("invalid")
  assert called is False


def test_result_pure_lifts_value_into_ok() -> None:
  assert Result.pure(5) == Ok(5)


def test_result_builder_sequences_ok_values() -> None:
  @result.block
  def workflow():
    first = yield Ok(2)
    second = yield Ok(first + 3)
    return second * 2

  assert workflow() == Ok(10)


def test_result_builder_short_circuits_on_err() -> None:
  reached = False

  @result.block
  def workflow():
    yield Ok(2)
    yield Err("invalid")

    nonlocal reached
    reached = True
    return "unreachable"

  assert workflow() == Err("invalid")
  assert reached is False


def test_result_builder_wraps_non_generator_return_value() -> None:
  @result.block
  def workflow():
    return 5

  assert workflow() == Ok(5)


def test_result_builder_rejects_non_result_yields() -> None:
  @result.block
  def workflow():
    value = yield 5
    return value

  with pytest.raises(TypeError, match="result blocks can only yield Result values"):
    workflow()
