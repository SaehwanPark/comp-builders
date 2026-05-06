"""ETL-style workflow example using `Result`."""

from __future__ import annotations

from collections.abc import Generator, Iterable
from dataclasses import dataclass
from typing import Any, cast

from comp_builders import Err, Ok, Result, result


@dataclass(frozen=True)
class LoadedBatch:
  """Summary of rows loaded by the example ETL job."""

  row_count: int
  total_amount: float


def extract_rows(source: Iterable[dict[str, Any]]) -> Result[list[dict[str, Any]], str]:
  """Extract rows from an iterable source."""
  rows = list(source)
  if not rows:
    return Err("no rows")
  return Ok(rows)


def transform_rows(
  rows: Iterable[dict[str, Any]],
) -> Result[list[dict[str, float]], str]:
  """Validate and normalize ETL row values."""
  transformed: list[dict[str, float]] = []
  for index, row in enumerate(rows):
    raw_amount = row.get("amount")
    if raw_amount is None:
      return Err(f"row {index} missing amount")
    try:
      amount = float(raw_amount)
    except (TypeError, ValueError):
      return Err(f"row {index} has invalid amount")
    if amount < 0:
      return Err(f"row {index} has negative amount")
    transformed.append({"amount": amount})
  return Ok(transformed)


def load_rows(rows: Iterable[dict[str, float]]) -> Result[LoadedBatch, str]:
  """Pretend to load rows while returning a deterministic summary."""
  materialized = list(rows)
  if not materialized:
    return Err("nothing to load")
  return Ok(
    LoadedBatch(
      row_count=len(materialized),
      total_amount=sum(row["amount"] for row in materialized),
    )
  )


@result.block
def run_etl(
  source: Iterable[dict[str, Any]],
) -> Generator[Result[Any, str], object, LoadedBatch]:
  """Run extract, transform, and load steps."""
  rows = cast(list[dict[str, Any]], (yield extract_rows(source)))
  transformed = cast(list[dict[str, float]], (yield transform_rows(rows)))
  return cast(LoadedBatch, (yield load_rows(transformed)))
