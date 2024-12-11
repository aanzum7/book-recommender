import os
import pandas as pd  # type: ignore
from config.logging_configs import logger  # Assuming logging is already configured

def main():
    # Step 1: Read the saved Parquet file
    try:
        logger.info("Reading filtered data from Parquet file...")
        filtered_data = pd.read_parquet('data/preprocessed_files/raw_data.parquet')  # The file from previous steps
        logger.info("Parquet file read successfully.")
    except Exception as e:
        logger.error(f"Error reading Parquet file: {e}")
        raise

    # Step 2: Select relevant columns and drop duplicates
    try:
        logger.info("Processing user information...")
        # Select the relevant columns
        user_infos = filtered_data[['user_id', 'location', 'age', 'age_group']]

        # Drop duplicates based on user_id, location, and age
        user_infos = user_infos.drop_duplicates()

        # Reset the index
        user_infos = user_infos.reset_index(drop=True)

        logger.info("User information processed successfully.")
    except Exception as e:
        logger.error(f"Error processing user information: {e}")
        raise

    # Log the total number of distinct users
    total_users = user_infos.shape[0]  # Get the number of rows (distinct users)
    logger.info(f"Total distinct users: {total_users}")

    # Step 3: Save the result as a Parquet file
    try:
        logger.info("Saving distinct user information to Parquet file...")
        user_infos.to_parquet("data/preprocessed_files/distinct_user_age_location.parquet", index=False)
        logger.info("Distinct user_id, location, and age combinations saved successfully.")
    except Exception as e:
        logger.error(f"Error saving Parquet file: {e}")
        raise

if __name__ == "__main__":
    main()
