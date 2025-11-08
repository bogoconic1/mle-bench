import shutil
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm.auto import tqdm

from mlebench.utils import read_csv


def prepare(raw: Path, public: Path, private: Path):
    """
    Splits the CSIRO biomass dataset into train and test sets.

    Each image has 5 target measurements, so we split by unique images
    rather than by rows to keep all targets together.

    Uses stratified splitting by month to ensure temporal balance.
    """
    # Load training data
    old_train = read_csv(raw / "train.csv")

    # Get unique image IDs (each image has 5 target rows)
    # Extract image ID from image_path (e.g., "train/ID1011485656.jpg" -> "ID1011485656")
    old_train["image_id"] = old_train["image_path"].apply(
        lambda x: Path(x).stem
    )

    # Extract month for stratification
    old_train["month"] = pd.to_datetime(old_train["Sampling_Date"]).dt.month

    # Create stratification variable combining State and month
    old_train["strata"] = old_train["State"].astype(str) + "_" + old_train["month"].astype(str)

    # Get unique images with their corresponding strata
    # Use groupby to get one row per image (they all have the same strata for a given image)
    image_strata_df = old_train.groupby("image_id")[["strata"]].first().reset_index()
    unique_images = image_strata_df["image_id"].values
    strata = image_strata_df["strata"].values

    # Split unique images into train/test (10% test, 90% train) stratified by State and month
    train_images, test_images = train_test_split(
        unique_images, test_size=0.1, random_state=0, stratify=strata
    )

    # Create train and test dataframes based on image splits
    new_train = old_train[old_train["image_id"].isin(train_images)].copy()
    new_test = old_train[old_train["image_id"].isin(test_images)].copy()

    # Update image paths for the new split
    new_train["image_path"] = new_train["image_id"].apply(lambda x: f"train/{x}.jpg")
    new_test["image_path"] = new_test["image_id"].apply(lambda x: f"test/{x}.jpg")

    # Drop temporary columns (image_id, month, and strata)
    new_train = new_train.drop(columns=["image_id", "month", "strata"])
    new_test = new_test.drop(columns=["image_id", "month", "strata"])

    # Create public test (without targets and metadata features)
    new_test_without_labels = new_test[["sample_id", "image_path", "target_name"]].copy()

    # Create sample submission
    sample_submission = new_test[["sample_id", "target"]].copy()
    sample_submission["target"] = 0.0  # Placeholder predictions

    # Create private answers
    answers = new_test[["sample_id", "target"]].copy()

    # Save CSV files
    new_train.to_csv(public / "train.csv", index=False)
    new_test_without_labels.to_csv(public / "test.csv", index=False)
    sample_submission.to_csv(public / "sample_submission.csv", index=False)
    answers.to_csv(private / "answers.csv", index=False)

    # Copy train images
    (public / "train").mkdir(exist_ok=True)
    for img_id in tqdm(train_images, desc="Copying train images"):
        src = raw / "train" / f"{img_id}.jpg"
        dst = public / "train" / f"{img_id}.jpg"
        if src.exists():
            shutil.copy(src, dst)

    # Copy test images
    (public / "test").mkdir(exist_ok=True)
    for img_id in tqdm(test_images, desc="Copying test images"):
        src = raw / "train" / f"{img_id}.jpg"  # Test images come from train folder
        dst = public / "test" / f"{img_id}.jpg"
        if src.exists():
            shutil.copy(src, dst)

    # Assertions
    assert len(train_images) + len(test_images) == len(
        unique_images
    ), "Train and test image counts should sum to total unique images"

    # Each image should have exactly 5 target rows
    assert len(new_train) == len(train_images) * 5, "Train should have 5 rows per image"
    assert len(new_test) == len(test_images) * 5, "Test should have 5 rows per image"

    assert len(sample_submission) == len(
        new_test
    ), "Sample submission should match test set length"
    assert len(answers) == len(new_test), "Answers should match test set length"

    # Check that all 5 target types are present for each image
    train_targets_per_image = new_train.groupby(new_train["image_path"])["target_name"].nunique()
    assert (
        train_targets_per_image == 5
    ).all(), "Each train image should have all 5 target types"

    test_targets_per_image = new_test.groupby(new_test["image_path"])["target_name"].nunique()
    assert (
        test_targets_per_image == 5
    ).all(), "Each test image should have all 5 target types"

    # Verify no overlap between train and test images
    assert set(train_images).isdisjoint(
        set(test_images)
    ), "Train and test images should not overlap"

    # Verify images were copied successfully
    assert len(list((public / "train").glob("*.jpg"))) == len(
        train_images
    ), "Train images should match train image count"
    assert len(list((public / "test").glob("*.jpg"))) == len(
        test_images
    ), "Test images should match test image count"

    # Verify sample_ids match between submission and answers
    assert (
        sample_submission["sample_id"].values == answers["sample_id"].values
    ).all(), "Sample submission and answers sample_ids must match"
