import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

from mlebench.grade_helpers import InvalidSubmissionError


def grade(submission: pd.DataFrame, answers: pd.DataFrame) -> float:
    """
    Grades submissions using a weighted average of R² scores across five biomass targets.

    Weights:
    - Dry_Green_g: 0.1
    - Dry_Dead_g: 0.1
    - Dry_Clover_g: 0.1
    - GDM_g: 0.2
    - Dry_Total_g: 0.5
    """
    # Define weights for each target type
    weights = {
        "Dry_Green_g": 0.1,
        "Dry_Dead_g": 0.1,
        "Dry_Clover_g": 0.1,
        "GDM_g": 0.2,
        "Dry_Total_g": 0.5,
    }

    id_col = "sample_id"
    target_col = "target"

    # Validation
    if id_col not in submission.columns:
        raise InvalidSubmissionError(
            f"Submission DataFrame must contain '{id_col}' column."
        )

    if id_col not in answers.columns:
        raise InvalidSubmissionError(
            f"Answers DataFrame must contain '{id_col}' column."
        )

    if target_col not in submission.columns:
        raise InvalidSubmissionError(
            f"Submission DataFrame must contain '{target_col}' column."
        )

    assert (
        target_col in answers.columns
    ), f"Answers DataFrame must contain '{target_col}' column."

    if len(submission) != len(answers):
        raise InvalidSubmissionError(
            f"Submission length ({len(submission)}) must match answers length ({len(answers)})."
        )

    # Sort both dataframes by sample_id
    answers_sorted = answers.sort_values(id_col).reset_index(drop=True)
    submission_sorted = submission.sort_values(id_col).reset_index(drop=True)

    # Verify sample_ids match
    if (submission_sorted[id_col].values != answers_sorted[id_col].values).any():
        raise InvalidSubmissionError(
            "Submission and answers have mismatched 'sample_id' values."
        )

    # Extract target_name from sample_id (format: ImageID__TargetName)
    # e.g., "ID1001187975__Dry_Green_g" -> "Dry_Green_g"
    answers_sorted["target_name"] = answers_sorted[id_col].str.split("__").str[1]
    submission_sorted["target_name"] = submission_sorted[id_col].str.split("__").str[1]

    # Verify all expected target types are present
    expected_targets = set(weights.keys())
    actual_targets = set(answers_sorted["target_name"].unique())

    if not expected_targets.issubset(actual_targets):
        missing = expected_targets - actual_targets
        raise InvalidSubmissionError(
            f"Missing target types in answers: {missing}"
        )

    # Calculate R² for each target type
    weighted_score = 0.0

    for target_name, weight in weights.items():
        # Filter data for this target type
        mask = answers_sorted["target_name"] == target_name
        y_true = answers_sorted[mask][target_col].values
        y_pred = submission_sorted[mask][target_col].values

        if len(y_true) == 0:
            raise InvalidSubmissionError(
                f"No samples found for target type '{target_name}'"
            )

        # Calculate R² score with force_finite=True to handle edge cases
        # (matches Kaggle's metric implementation)
        r2 = r2_score(y_true, y_pred)

        # Handle non-finite R² scores (as per sklearn's force_finite behavior)
        # When y_true is constant:
        # - R² is 1.0 if predictions are perfect (all equal to the constant)
        # - R² is 0.0 otherwise
        if not np.isnan(r2) and not np.isinf(r2):
            weighted_score += weight * r2
        elif np.isnan(r2):
            # NaN occurs when predictions are perfect on constant y_true
            weighted_score += weight * 1.0
        else:
            # -Inf occurs when predictions are imperfect on constant y_true
            weighted_score += weight * 0.0

    return float(weighted_score)
