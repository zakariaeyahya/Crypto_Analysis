import os
from pathlib import Path
import logging

import pandas as pd


def ensure_directory(path: Path) -> None:
	if not path.exists():
		path.mkdir(parents=True, exist_ok=True)


def assign_temporal_split(df: pd.DataFrame, date_column: str) -> pd.Series:
	"""
	Create a split label based on the first 30 unique calendar days in the dataset
	(ordered ascending). Days 1-21 -> train, 22-25 -> validation, 26-30 -> test.

	If there are fewer than 30 unique days, the later buckets may be empty.
	"""
	# Sort and compute unique dates (date-level, no time)
	df_sorted = df.sort_values(by=date_column)
	unique_days = (
		df_sorted[date_column]
		.dt.normalize()
		.drop_duplicates()
		.reset_index(drop=True)
	)

	# Take the first 30 unique days (if available)
	first_30_days = set(unique_days.head(30))

	# Map each day to a 1-based index within the first 30 days
	day_to_index = {day: idx + 1 for idx, day in enumerate(sorted(first_30_days))}

	# Compute the split label
	def map_to_split(ts: pd.Timestamp) -> str:
		day = pd.Timestamp(ts.normalize())
		idx = day_to_index.get(day)
		if idx is None:
			return "out_of_window"
		if 1 <= idx <= 21:
			return "train"
		if 22 <= idx <= 25:
			return "validation"
		if 26 <= idx <= 30:
			return "test"
		return "out_of_window"

	return df[date_column].apply(map_to_split)


def main() -> None:
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
	logger = logging.getLogger(__name__)
	project_root = Path(__file__).resolve().parents[2]
	input_csv = project_root / "data" / "silver" / "reddit" / "cleaned_reddit_dataset.csv"
	output_dir = project_root / "data" / "silver" / "reddit"

	if not input_csv.exists():
		raise FileNotFoundError(f"Input file not found: {input_csv}")

	ensure_directory(output_dir)

	# Load data
	df = pd.read_csv(input_csv)

	# Validate required column
	if "created_date" not in df.columns:
		raise ValueError("Column 'created_date' is required in the cleaned dataset.")

	# Parse to datetime (UTC-naive acceptable for ordering)
	df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
	if df["created_date"].isna().all():
		raise ValueError("All 'created_date' values failed to parse to datetime.")

	# Assign temporal split without shuffling to avoid leakage
	df["split"] = assign_temporal_split(df, "created_date")

	# Filter to the 30-day evaluation window
	df_window = df[df["split"] != "out_of_window"].copy()

	# Optional: If a 'sentiment' column exists, we only report distributions.
	# Temporal splits must not shuffle, so no stratification across time.
	has_sentiment = "sentiment" in df_window.columns

	# Save outputs
	train_df = df_window[df_window["split"] == "train"].drop(columns=["split"])  # type: ignore[arg-type]
	val_df = df_window[df_window["split"] == "validation"].drop(columns=["split"])  # type: ignore[arg-type]
	test_df = df_window[df_window["split"] == "test"].drop(columns=["split"])  # type: ignore[arg-type]

	train_path = output_dir / "train_data.csv"
	val_path = output_dir / "validation_data.csv"
	test_path = output_dir / "test_data.csv"

	train_df.to_csv(train_path, index=False)
	val_df.to_csv(val_path, index=False)
	test_df.to_csv(test_path, index=False)

	# Log summary
	logger.info("Saved:")
	logger.info(" - %s -> %d rows", train_path, len(train_df))
	logger.info(" - %s -> %d rows", val_path, len(val_df))
	logger.info(" - %s -> %d rows", test_path, len(test_df))

	if has_sentiment:
		def dist(name: str, part: pd.DataFrame) -> None:
			logger.info("Sentiment distribution (%s):", name)
			# Log normalized value counts
			vc = part["sentiment"].value_counts(normalize=True)
			for label, frac in vc.items():
				logger.info("   %s: %.4f", label, frac)

		dist("train", train_df)
		dist("validation", val_df)
		dist("test", test_df)


if __name__ == "__main__":
	main()


