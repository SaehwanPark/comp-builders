import pytest

from comp_builders import Invalid, Valid, Validation, validation


def test_valid_map_transforms_valid_value() -> None:
  assert Valid(2).map(lambda value: value + 3) == Valid(5)


def test_invalid_map_preserves_errors_without_calling_callback() -> None:
  called = False

  def fail(_value):
    nonlocal called
    called = True

  assert Invalid(("missing",)).map(fail) == Invalid(("missing",))
  assert called is False


def test_valid_bind_sequences_validation_returning_callback() -> None:
  assert Valid(2).bind(lambda value: Valid(value + 3)) == Valid(5)


def test_invalid_bind_preserves_errors_without_calling_callback() -> None:
  called = False

  def fail(_value):
    nonlocal called
    called = True
    return Valid("unreachable")

  assert Invalid(("missing",)).bind(fail) == Invalid(("missing",))
  assert called is False


def test_validation_pure_lifts_value_into_valid() -> None:
  assert Validation.pure(5) == Valid(5)


def test_invalid_accepts_single_error_value() -> None:
  assert Invalid("missing") == Invalid(("missing",))


def test_validation_builder_sequences_valid_values() -> None:
  @validation.block
  def workflow():
    first = yield Valid(2)
    second = yield Valid(first + 3)
    return second * 2

  assert workflow() == Valid(10)


def test_validation_builder_accumulates_invalid_errors() -> None:
  @validation.block
  def workflow():
    yield Invalid(("missing name",))
    yield Invalid(("invalid email", "weak password"))
    return "ignored"

  assert workflow() == Invalid(("missing name", "invalid email", "weak password"))


def test_validation_builder_preserves_empty_invalid_state() -> None:
  @validation.block
  def workflow():
    yield Invalid(())
    return "ignored"

  assert workflow() == Invalid(())


def test_validation_builder_continues_after_invalid_with_none_value() -> None:
  seen = []

  @validation.block
  def workflow():
    missing = yield Invalid(("missing",))
    seen.append(missing)
    present = yield Valid(3)
    return present

  assert workflow() == Invalid(("missing",))
  assert seen == [None]


def test_validation_builder_wraps_non_generator_return_value() -> None:
  @validation.block
  def workflow():
    return 5

  assert workflow() == Valid(5)


def test_validation_builder_preserves_function_metadata() -> None:
  @validation.block
  def workflow():
    """Workflow docstring."""
    return 5

  assert workflow.__name__ == "workflow"
  assert workflow.__doc__ == "Workflow docstring."


def test_validation_builder_rejects_non_validation_yields() -> None:
  @validation.block
  def workflow():
    value = yield 5
    return value

  with pytest.raises(
    TypeError, match="validation blocks can only yield Validation values"
  ):
    workflow()
