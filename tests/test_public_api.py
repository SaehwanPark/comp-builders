import asyncio

import comp_builders
from comp_builders import AsyncResult, Err, Invalid, Nothing, Ok, Some, Valid


def test_public_exports_are_frozen() -> None:
  assert comp_builders.__all__ == [
    "AsyncResult",
    "AsyncResultBuilder",
    "Builder",
    "Err",
    "Invalid",
    "Nothing",
    "Ok",
    "Option",
    "OptionBuilder",
    "Result",
    "ResultBuilder",
    "Some",
    "Valid",
    "Validation",
    "ValidationBuilder",
    "async_result",
    "builder",
    "option",
    "result",
    "validation",
  ]


def test_public_exports_resolve_from_package_root() -> None:
  for name in comp_builders.__all__:
    assert getattr(comp_builders, name) is not None


def test_result_values_support_stable_repr_equality_and_matching() -> None:
  assert Ok("value") == Ok("value")
  assert repr(Err("failure")) == "Err(error='failure')"

  match Ok(3):
    case Ok(value):
      assert value == 3
    case _:
      raise AssertionError("Ok value did not match")


def test_option_and_validation_values_support_stable_contracts() -> None:
  assert Some("name") == Some("name")
  assert Nothing is comp_builders.Nothing
  assert Invalid(["missing", "invalid"]) == Invalid(("missing", "invalid"))
  assert repr(Valid(2)) == "Valid(value=2)"


def test_async_result_public_contract_is_awaitable_result() -> None:
  async def await_result() -> object:
    return await AsyncResult.from_result(Ok("ready"))

  result = asyncio.run(await_result())

  assert result == Ok("ready")
