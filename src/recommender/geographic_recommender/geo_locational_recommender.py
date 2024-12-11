import os
import pandas as pd  # type: ignore
import json
import argparse
import logging
from config.logging_configs import logger  # Assuming logging is already configured

def read_parquet(file_path: str) -> pd.DataFrame:
    """Reads the Parquet file and returns the DataFrame."""
    try:
        logger.info(f"Reading data from {file_path}...")
        return pd.read_parquet(file_path)
    except Exception as e:
        logger.error(f"Error reading Parquet file from {file_path}: {e}")
        raise

def process_geo_location_data(df: pd.DataFrame) -> pd.DataFrame:
    """Processes the data to group by location and ISBN, calculating ratings and number of unique users."""
    try:
        logger.info("Selecting relevant columns for ratings and geo-location...")
        ratings_with_geo_location_data = df[['user_id', 'isbn', 'book_rating', 'location']]

        logger.info("Grouping ratings by location and ISBN...")
        book_ratings_with_each_location = (
            ratings_with_geo_location_data.groupby(['location', 'isbn'])
            .agg(
                avg_rating=('book_rating', 'mean'),
                user_rated=('user_id', 'nunique')
            )
            .reset_index()
        ).sort_values(by='user_rated', ascending=False)

        logger.info("Geo-location data processed successfully.")
        return book_ratings_with_each_location
    except Exception as e:
        logger.error(f"Error processing geo-location data: {e}")
        raise

def calculate_weighted_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates the weighted score for each book based on average rating and number of unique users."""
    try:
        logger.info("Calculating weighted score for each book...")
        df["weighted_score"] = 0.8 * df["avg_rating"] + 0.2 * df["user_rated"]
        return df
    except Exception as e:
        logger.error(f"Error calculating weighted scores: {e}")
        raise

def get_top_isbn_per_location(df: pd.DataFrame) -> pd.Series:
    """Gets the top ISBNs per location based on weighted score."""
    try:
        logger.info("Selecting top ISBNs per location...")
        top_isbn_per_location = (
            df.sort_values(by=["location", "weighted_score"], ascending=[True, False])
            .groupby("location")
            .head(10)
            .groupby("location")["isbn"]
            .apply(list)
        )
        logger.info("Top ISBNs per location selected successfully.")
        return top_isbn_per_location
    except Exception as e:
        logger.error(f"Error selecting top ISBNs: {e}")
        raise

def save_top_isbn_to_json(top_isbn_dict: dict, output_dir: str) -> None:
    """Saves the top ISBNs per location to a JSON file."""
    try:
        os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists
        output_file_path = os.path.join(output_dir, "top_isbn_per_location.json")
        with open(output_file_path, "w") as json_file:
            json.dump(top_isbn_dict, json_file)
        logger.info(f"Top ISBNs saved to {output_file_path} successfully.")
    except Exception as e:
        logger.error(f"Error saving top ISBNs to JSON: {e}")
        raise

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Process and recommend books by geo-location.")
    parser.add_argument(
        '--input_file', type=str, default='data/preprocessed_files/raw_data.parquet', help='Path to the input Parquet file with ratings data.'
    )
    parser.add_argument(
        '--output_dir', type=str, default='data/recommender_result', help='Directory to save the results.'
    )
    return parser.parse_args()

def main():
    """Main function to process data and generate recommendations."""
    # Step 1: Parse arguments
    args = parse_args()

    # Step 2: Read Parquet file
    filtered_data = read_parquet(args.input_file)

    # Step 3: Process data by location and ISBN
    ratings_with_geo_location_data = process_geo_location_data(filtered_data)

    # Step 4: Calculate weighted scores
    weighted_ratings_data = calculate_weighted_scores(ratings_with_geo_location_data)

    # Step 5: Get top ISBNs per location
    top_isbn_per_location = get_top_isbn_per_location(weighted_ratings_data)

    # Step 6: Convert to dictionary and save to JSON
    top_isbn_dict = top_isbn_per_location.to_dict()
    save_top_isbn_to_json(top_isbn_dict, args.output_dir)

if __name__ == "__main__":
    main()
