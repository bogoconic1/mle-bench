from pathlib import Path

from sklearn.model_selection import train_test_split
import pandas as pd


def prepare(raw: Path, public: Path, private: Path):

    # Load raw competition files
    train = pd.read_csv(raw / "train.csv")

    # Identify columns
    id_col = "id"
    target_col = "loan_paid_back"

    assert id_col in train.columns, f"Expected '{id_col}' in train.csv"
    assert target_col in train.columns, f"Expected '{target_col}' in train.csv"
    # Create public train and test split from the Kaggle train
    train_fold, holdout_fold = train_test_split(train, test_size=0.1, random_state=0)

    # Public files visible to agents
    train_fold.to_csv(public / "train.csv", index=False)

    public_test = holdout_fold.drop(columns=[target_col]).copy()
    public_test.to_csv(public / "test.csv", index=False)

    # Sample submission matching required schema for the public test IDs
    sample = public_test[[id_col]].copy()
    sample[target_col] = 0.5
    sample.to_csv(public / "sample_submission.csv", index=False)

    # Private answers aligned to the public test
    private_answers = holdout_fold[[id_col, target_col]].copy()
    private_answers.to_csv(private / "answers.csv", index=False)

    # Checks
    assert (public / "sample_submission.csv").is_file()
    assert (public / "train.csv").is_file()
    assert (public / "test.csv").is_file()
    assert (private / "answers.csv").is_file()

