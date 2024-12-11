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
        logger.info("Processing book information...")
        # Select the relevant columns for book information
        book_infos = filtered_data[['isbn', 'book_title', 'book_author', 'year_of_publication', 'publisher', 'image_url']]

        # Drop duplicates based on the selected columns
        book_infos = book_infos.drop_duplicates()

        # Reset the index
        book_infos = book_infos.reset_index(drop=True)

        logger.info("Book information processed successfully.")
    except Exception as e:
        logger.error(f"Error processing book information: {e}")
        raise

    # Log the total number of books
    books_count = book_infos.shape[0]  # Get the number of rows (distinct books)
    logger.info(f"Books count: {books_count}")

    # Step 3: Save the result as a Parquet file
    try:
        logger.info("Saving distinct book information to Parquet file...")
        book_infos.to_parquet("data/preprocessed_files/distinct_books.parquet", index=False)
        logger.info("Distinct book information saved successfully.")
    except Exception as e:
        logger.error(f"Error saving Parquet file: {e}")
        raise

if __name__ == "__main__":
    main()
