import pandas as pd
from pathlib import Path


def convert(src: Path, dst: Path) -> None:
    df = pd.read_csv(src)
    if "Score" in df.columns and "score" not in df.columns:
        df = df.rename(columns={"Score": "score"})
    # Ensure numeric and sorted by Rank if present
    if "score" in df.columns:
        df["score"] = pd.to_numeric(df["score"], errors="coerce")
    if "Rank" in df.columns:
        df = df.sort_values("Rank")
    df.to_csv(dst, index=False)


if __name__ == "__main__":
    base = Path(__file__).parent
    convert(base / "raw_leaderboard.csv", base / "leaderboard.csv")

