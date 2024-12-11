import os
import pandas as pd  # type: ignore
from scipy.sparse import csr_matrix # type: ignore
from sklearn.metrics.pairwise import cosine_similarity # type: ignore
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define paths
RAW_PARQUET_PATH = "data/preprocessed_files/raw_data.parquet"
OUTPUT_FILE = "data/recommender_result/book_similarities.csv"

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def read_raw_data(file_path: str) -> pd.DataFrame:
    """Reads the raw Parquet file."""
    try:
        logger.info(f"Reading raw data from {file_path}...")
        return pd.read_parquet(file_path)
    except Exception as e:
        logger.error(f"Error reading Parquet file: {e}")
        raise

def process_user_book_matrix(raw_data: pd.DataFrame) -> csr_matrix:
    """Processes the user-item matrix and converts it to a sparse format."""
    try:
        logger.info("Creating the user-item matrix...")
        user_book_matrix = raw_data.pivot_table(index='user_id', columns='isbn', values='book_rating').fillna(0)
        logger.info("Converting the user-item matrix to sparse format...")
        return csr_matrix(user_book_matrix.values), user_book_matrix.columns
    except Exception as e:
        logger.error(f"Error processing user-item matrix: {e}")
        raise

def compute_book_similarities(sparse_matrix: csr_matrix, book_ids: pd.Index, top_n: int = 10) -> pd.DataFrame:
    """Computes book-to-book similarities and generates top N recommendations for each book."""
    try:
        logger.info("Computing cosine similarity between books...")
        book_similarities = cosine_similarity(sparse_matrix.T)  # Transpose to calculate book similarity
        logger.info("Generating top N similar books for each book...")

        # Create a mapping of ISBN to similar books
        similar_books = []
        for i, isbn in enumerate(book_ids):
            # Get top N similar books (excluding itself)
            sim_scores = book_similarities[i]
            top_books = book_ids[sim_scores.argsort()[::-1][1:top_n + 1]].tolist()
            similar_books.append({"isbn": isbn, "similar_books": ",".join(top_books)})

        return pd.DataFrame(similar_books)
    except Exception as e:
        logger.error(f"Error computing book similarities: {e}")
        raise

def save_results(similar_books: pd.DataFrame, output_file: str) -> None:
    """Saves the book similarity results to a CSV file."""
    try:
        logger.info("Saving book similarity results to CSV...")
        similar_books.to_csv(output_file, index=False)
        logger.info(f"Results saved in {output_file}.")
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        raise

def main():
    """Main executable for book-to-book recommendations."""
    try:
        # Step 1: Read raw data
        raw_data = read_raw_data(RAW_PARQUET_PATH)

        # Step 2: Process user-book matrix
        user_book_sparse, book_ids = process_user_book_matrix(raw_data)

        # Step 3: Compute book similarities
        similar_books = compute_book_similarities(user_book_sparse, book_ids)

        # Step 4: Save results
        save_results(similar_books, OUTPUT_FILE)

    except Exception as e:
        logger.error(f"An error occurred in the main process: {e}")
        raise

if __name__ == "__main__":
    main()
