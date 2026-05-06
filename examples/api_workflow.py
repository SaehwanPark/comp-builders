"""API-style workflow example using `Result`."""

from __future__ import annotations

import json
from collections.abc import Generator
from dataclasses import dataclass
from typing import Any, cast

from comp_builders import Err, Ok, Result, result


@dataclass(frozen=True)
class UserRecord:
  """Persisted user record returned by the example workflow."""

  user_id: str
  email: str


def parse_json(body: str) -> Result[dict[str, Any], str]:
  """Parse a JSON request body into an object."""
  try:
    value = json.loads(body)
  except json.JSONDecodeError:
    return Err("invalid json")

  if not isinstance(value, dict):
    return Err("request body must be an object")
  return Ok(value)


def read_required_string(data: dict[str, Any], key: str) -> Result[str, str]:
  """Read a non-empty string field from a request object."""
  value = data.get(key)
  if not isinstance(value, str) or not value.strip():
    return Err(f"missing {key}")
  return Ok(value.strip())


def save_user(user_id: str, email: str) -> Result[UserRecord, str]:
  """Pretend to persist a user while keeping the example deterministic."""
  if "@" not in email:
    return Err("invalid email")
  return Ok(UserRecord(user_id=user_id, email=email.lower()))


@result.block
def create_user(body: str) -> Generator[Result[Any, str], object, UserRecord]:
  """Create a user from a JSON request body."""
  data = cast(dict[str, Any], (yield parse_json(body)))
  user_id = cast(str, (yield read_required_string(data, "user_id")))
  email = cast(str, (yield read_required_string(data, "email")))
  return cast(UserRecord, (yield save_user(user_id, email)))
