# Overview

**Your Goal:** Predict the probability that a borrower will pay back their loan.

----------------------
# Evaluation

Submissions are evaluated on [area under the ROC curve](https://en.wikipedia.org/wiki/Receiver_operating_characteristic) between the predicted probability and the observed target.

## Submission File
For each `id` in the test set, you must predict a probability for the `loan_paid_back` variable. The file should contain a header and have the following format:

    id,loan_paid_back
    593994,0.5
    593995,0.2
    593996,0.1
    etc.
    
----------------------

# Dataset Description

The dataset for this competition (both train and test) was generated from a deep learning model trained on the [Loan Prediction dataset](https://www.kaggle.com/datasets/nabihazahid/loan-prediction-dataset-2025). Feature distributions are close to, but not exactly the same, as the original. Feel free to use the original dataset as part of this competition, both to explore differences as well as to see whether incorporating the original in training improves model performance.


## Files

*   **train.csv** - the training set
*   **test.csv** - the test set
*   **sample_submission.csv** - a sample submission file in the correct format