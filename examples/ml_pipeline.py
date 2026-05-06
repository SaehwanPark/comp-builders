"""ML-style pipeline example using `Result` and `Option`."""

from __future__ import annotations

from collections.abc import Generator, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, cast

from comp_builders import Err, Nothing, Ok, Option, Result, Some, option, result

FeatureValue = str | int | float


@dataclass(frozen=True)
class Prediction:
  """Small deterministic prediction result for the example pipeline."""

  label: str
  score: float
  note: str | None = None


def load_features(
  row: Mapping[str, FeatureValue], names: Sequence[str]
) -> Result[list[float], str]:
  """Read numeric features in a stable order."""
  values: list[float] = []
  for name in names:
    value = row.get(name)
    if value is None:
      return Err(f"missing feature {name}")
    try:
      values.append(float(value))
    except (TypeError, ValueError):
      return Err(f"invalid feature {name}")
  return Ok(values)


def normalize(values: Sequence[float]) -> Result[list[float], str]:
  """Normalize values by their total magnitude."""
  total = sum(abs(value) for value in values)
  if total == 0:
    return Err("empty signal")
  return Ok([value / total for value in values])


def lookup_note(metadata: Mapping[str, str], key: str) -> Option[str]:
  """Find optional metadata for a prediction."""
  note = metadata.get(key)
  if note is None or not note.strip():
    return cast(Option[str], Nothing)
  return Some(note.strip())


@option.block
def optional_prediction_note(
  metadata: Mapping[str, str], key: str
) -> Generator[Option[str], object, str]:
  """Return an optional note for a prediction."""
  note = cast(str, (yield lookup_note(metadata, key)))
  return note


@result.block
def predict_label(
  row: Mapping[str, FeatureValue],
  metadata: Mapping[str, str],
  feature_names: Sequence[str] = ("bias", "signal"),
) -> Generator[Result[Any, str], object, Prediction]:
  """Predict a label from a row of numeric features."""
  features = cast(list[float], (yield load_features(row, feature_names)))
  normalized = cast(list[float], (yield normalize(features)))
  score = normalized[-1]
  label = "positive" if score >= 0.5 else "negative"
  note = optional_prediction_note(metadata, label)
  match note:
    case Some(value):
      return Prediction(label=label, score=score, note=value)
    case _:
      return Prediction(label=label, score=score)
