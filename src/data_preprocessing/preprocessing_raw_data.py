import os
import pandas as pd  # type: ignore
import logging
from config.logging_configs import logger  # Import logger from your existing logging configuration

def main():
    # Step 1: Read CSV files into DataFrames
    try:
        logger.info("Reading CSV files...")
        # Set low_memory=False to handle columns with mixed data types
        books_df = pd.read_csv('data/raw_files/Books.csv', low_memory=False)
        ratings_df = pd.read_csv('data/raw_files/Ratings.csv', low_memory=False)
        users_df = pd.read_csv('data/raw_files/Users.csv', low_memory=False)
        logger.info(f"CSV files read successfully. Rows in Books: {len(books_df)}, Rows in Ratings: {len(ratings_df)}, Rows in Users: {len(users_df)}")
    except Exception as e:
        logger.error(f"Error reading CSV files: {e}")
        raise

    # Step 2: Rename columns to match the required names
    try:
        logger.info("Renaming columns...")
        users_df_v2 = users_df.rename(columns={
            'User-ID': 'user_id',
            'Location': 'location',
            'Age': 'age'
        })

        ratings_df_v2 = ratings_df.rename(columns={
            'User-ID': 'user_id',
            'ISBN': 'isbn',
            'Book-Rating': 'book_rating'
        })

        # Step 3: Select the required columns for books and rename
        books_v2 = books_df[['ISBN', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Image-URL-L']].copy()
        books_v2.rename(columns={
            'ISBN': 'isbn',
            'Book-Title': 'book_title',
            'Book-Author': 'book_author',
            'Year-Of-Publication': 'year_of_publication',
            'Publisher': 'publisher',
            'Image-URL-L': 'image_url'
        }, inplace=True)
        logger.info(f"Columns renamed successfully. Rows in Books: {len(books_v2)}, Rows in Ratings: {len(ratings_df_v2)}, Rows in Users: {len(users_df_v2)}")
    except Exception as e:
        logger.error(f"Error renaming columns: {e}")
        raise

    # Step 4: Merge Ratings with Books
    try:
        logger.info("Merging Ratings with Books...")
        ratings_with_books = ratings_df_v2.merge(books_v2, on="isbn", how="inner")
        logger.info(f"Merge with Books completed. Rows after merge: {len(ratings_with_books)}")
    except Exception as e:
        logger.error(f"Error merging Ratings with Books: {e}")
        raise

    # Step 5: Merge Ratings with Users (age)
    try:
        logger.info("Merging Ratings with Users (age)...")
        ratings_with_age_books = ratings_with_books.merge(users_df_v2, on="user_id", how="inner")
        logger.info(f"Merge with Users completed. Rows after merge: {len(ratings_with_age_books)}")
    except Exception as e:
        logger.error(f"Error merging Ratings with Users: {e}")
        raise

    # Step 6: Reset the index and drop the old index column
    ratings_data_with_age_books_infos = ratings_with_age_books.reset_index(drop=True)

    # Step 7: Categorize Age Groups
    try:
        logger.info("Categorizing Age Groups...")
        def categorize_age(age):
            if pd.isna(age):
                return "Unknown"
            elif age <= 19:
                return "Teenager"
            elif 20 <= age <= 35:
                return "Young Adult"
            elif 36 <= age <= 55:
                return "Middle-aged"
            else:
                return "Senior"

        ratings_data_with_age_books_infos["age_group"] = ratings_data_with_age_books_infos["age"].apply(categorize_age)
        logger.info(f"Age categorization completed. Rows after categorization: {len(ratings_data_with_age_books_infos)}")
    except Exception as e:
        logger.error(f"Error categorizing age: {e}")
        raise

    # Step 8: Filter for users with more than 5 ratings
    try:
        logger.info("Filtering users with more than 5 ratings...")
        valid_users = ratings_data_with_age_books_infos.groupby('user_id').filter(lambda x: len(x) > 5)
        logger.info(f"Filtered {len(valid_users)} valid users.")
    except Exception as e:
        logger.error(f"Error filtering users: {e}")
        raise

    # Step 9: Filter for books (ISBNs) with more than 10 ratings
    try:
        logger.info("Filtering books with more than 10 ratings...")
        valid_books = valid_users.groupby('isbn').filter(lambda x: len(x) > 10)
        logger.info(f"Filtered {len(valid_books)} valid books.")
    except Exception as e:
        logger.error(f"Error filtering books: {e}")
        raise

    # Step 10: Save the filtered data to a Parquet file
    try:
        logger.info("Saving filtered data to a Parquet file...")
        valid_books.to_parquet('data/preprocessed_files/raw_data.parquet')
        logger.info("Filtered data saved successfully to data/preprocessed_files/raw_data.parquet.")
    except Exception as e:
        logger.error(f"Error saving data to Parquet: {e}")
        raise

    logger.info("Data processing and sampling completed successfully.")

if __name__ == "__main__":
    main()
