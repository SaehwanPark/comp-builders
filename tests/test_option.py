import pytest

from comp_builders import Nothing, Option, Some, option


def test_some_map_transforms_present_value() -> None:
  assert Some(2).map(lambda value: value + 3) == Some(5)


def test_nothing_map_preserves_absence_without_calling_callback() -> None:
  called = False

  def fail(_value):
    nonlocal called
    called = True

  assert Nothing.map(fail) is Nothing
  assert called is False


def test_some_bind_sequences_option_returning_callback() -> None:
  assert Some(2).bind(lambda value: Some(value + 3)) == Some(5)


def test_nothing_bind_short_circuits_without_calling_callback() -> None:
  called = False

  def fail(_value):
    nonlocal called
    called = True
    return Some("unreachable")

  assert Nothing.bind(fail) is Nothing
  assert called is False


def test_option_pure_lifts_value_into_some() -> None:
  assert Option.pure(5) == Some(5)


def test_option_builder_sequences_some_values() -> None:
  @option.block
  def workflow():
    first = yield Some(2)
    second = yield Some(first + 3)
    return second * 2

  assert workflow() == Some(10)


def test_option_builder_short_circuits_on_nothing() -> None:
  reached = False

  @option.block
  def workflow():
    yield Some(2)
    yield Nothing

    nonlocal reached
    reached = True
    return "unreachable"

  assert workflow() is Nothing
  assert reached is False


def test_option_builder_wraps_non_generator_return_value() -> None:
  @option.block
  def workflow():
    return 5

  assert workflow() == Some(5)


def test_option_builder_rejects_non_option_yields() -> None:
  @option.block
  def workflow():
    value = yield 5
    return value

  with pytest.raises(TypeError, match="option blocks can only yield Option values"):
    workflow()
