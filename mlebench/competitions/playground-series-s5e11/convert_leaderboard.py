import pandas as pd
from pathlib import Path


def convert(src: Path, dst: Path) -> None:
    df = pd.read_csv(src)
    if "Score" in df.columns and "score" not in df.columns:
        df = df.rename(columns={"Score": "score"})
    # Ensure numeric and sorted by Rank if present
    if "score" in df.columns:
        df["score"] = pd.to_numeric(df["score"], errors="coerce")
        df["score"] = df["score"].round(5)
    if "Rank" in df.columns:
        # Separate baselines (Rank=0) from actual entries
        baselines = df[df["Rank"] == 0].copy()
        actual_entries = df[df["Rank"] != 0].copy()
        # Sort actual entries by Rank
        actual_entries = actual_entries.sort_values("Rank")
        # Combine: actual entries first, then baselines at the end
        df = pd.concat([actual_entries, baselines], ignore_index=True)
    df.to_csv(dst, index=False)


if __name__ == "__main__":
    base = Path(__file__).parent
    convert(base / "raw_leaderboard.csv", base / "leaderboard.csv")

