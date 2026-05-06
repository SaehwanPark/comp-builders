from comp_builders import Err, Nothing, Ok, Some
from examples.api_workflow import UserRecord, create_user
from examples.etl_job import LoadedBatch, run_etl
from examples.ml_pipeline import Prediction, optional_prediction_note, predict_label


def test_api_workflow_creates_user_record() -> None:
  body = '{"user_id": " ada ", "email": "ADA@example.com"}'

  assert create_user(body) == Ok(UserRecord(user_id="ada", email="ada@example.com"))


def test_api_workflow_short_circuits_on_invalid_email() -> None:
  body = '{"user_id": "ada", "email": "invalid"}'

  assert create_user(body) == Err("invalid email")


def test_ml_pipeline_predicts_label_with_optional_note() -> None:
  prediction = predict_label(
    {"bias": 1.0, "signal": 3.0},
    {"positive": "review quickly"},
  )

  assert prediction == Ok(
    Prediction(label="positive", score=0.75, note="review quickly")
  )


def test_ml_pipeline_reports_missing_features() -> None:
  assert predict_label({"bias": 1.0}, {}) == Err("missing feature signal")


def test_ml_pipeline_reports_invalid_features() -> None:
  assert predict_label({"bias": 1.0, "signal": "x"}, {}) == Err(
    "invalid feature signal"
  )


def test_ml_pipeline_optional_note_can_be_absent() -> None:
  assert optional_prediction_note({}, "positive") is Nothing
  assert optional_prediction_note({"positive": "monitor"}, "positive") == Some(
    "monitor"
  )


def test_etl_job_loads_transformed_rows() -> None:
  rows = [{"amount": "2.5"}, {"amount": 3}]

  assert run_etl(rows) == Ok(LoadedBatch(row_count=2, total_amount=5.5))


def test_etl_job_short_circuits_on_invalid_row() -> None:
  rows = [{"amount": 2}, {"amount": -1}]

  assert run_etl(rows) == Err("row 1 has negative amount")


def test_etl_job_short_circuits_on_non_numeric_amount() -> None:
  rows = [{"amount": 2}, {"amount": "abc"}]

  assert run_etl(rows) == Err("row 1 has invalid amount")
