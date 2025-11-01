import pandas as pd
from sklearn.metrics import roc_auc_score

from mlebench.grade_helpers import InvalidSubmissionError


def prepare_for_metric(submission: pd.DataFrame, answers: pd.DataFrame) -> dict:

    id_col = "id"
    target_col = "loan_paid_back"

    if id_col not in submission.columns or id_col not in answers.columns:
        raise InvalidSubmissionError(
            "Both submission and answers DataFrames must contain an 'id' column."
        )

    if target_col not in submission.columns:
        raise InvalidSubmissionError(
            f"Submission DataFrame must contain '{target_col}' column."
        )

    assert (
        target_col in answers.columns
    ), f"Answers DataFrame must contain '{target_col}' column."

    if len(submission) != len(answers):
        raise InvalidSubmissionError("Submission must be the same length as the answers.")

    answers_sorted = answers.sort_values(id_col)
    submission_sorted = submission.sort_values(id_col)

    if (submission_sorted[id_col].values != answers_sorted[id_col].values).any():
        raise InvalidSubmissionError("Submission and answers have mismatched 'id' columns")

    y_true = answers_sorted[target_col].to_numpy()
    y_pred = submission_sorted[target_col].to_numpy()

    return {"y_true": y_true, "y_score": y_pred}


def grade(submission: pd.DataFrame, answers: pd.DataFrame) -> float:
    inputs = prepare_for_metric(submission, answers)
    auc = roc_auc_score(**inputs)
    return float(auc)

