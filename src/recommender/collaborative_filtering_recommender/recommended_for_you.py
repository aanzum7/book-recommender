import os
import pandas as pd  # type: ignore
from scipy.sparse import csr_matrix  # type: ignore
from sklearn.decomposition import TruncatedSVD  # type: ignore
from sklearn.cluster import MiniBatchKMeans  # type: ignore
import logging
from config.logging_configs import logger  # Assuming your logging is set up

# Define paths
RAW_PARQUET_PATH = "data/preprocessed_files/raw_data.parquet"
OUTPUT_DIR = "data/recommender_result"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
        raw_data = raw_data[['user_id', 'isbn', 'book_rating', 'location', 'age_group']]
        user_book_matrix = raw_data.pivot_table(index='user_id', columns='isbn', values='book_rating').fillna(0)
        logger.info("Converting the user-item matrix to sparse format...")
        return csr_matrix(user_book_matrix.values), user_book_matrix.index
    except Exception as e:
        logger.error(f"Error processing user-item matrix: {e}")
        raise

def perform_svd(user_book_sparse: csr_matrix, n_components: int = 100) -> pd.DataFrame:
    """Performs dimensionality reduction using TruncatedSVD."""
    try:
        logger.info(f"Performing SVD with {n_components} components...")
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        return svd.fit_transform(user_book_sparse)
    except Exception as e:
        logger.error(f"Error performing SVD: {e}")
        raise

def cluster_users(reduced_matrix: pd.DataFrame, n_clusters: int = 30) -> pd.DataFrame:
    """Clusters users into groups using MiniBatchKMeans."""
    try:
        logger.info(f"Clustering users into {n_clusters} clusters...")
        kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, batch_size=1000)
        clusters = kmeans.fit_predict(reduced_matrix)
        logger.info("User clustering completed.")
        return clusters
    except Exception as e:
        logger.error(f"Error clustering users: {e}")
        raise

def generate_cluster_recommendations(data: pd.DataFrame, clusters: pd.DataFrame, user_indices) -> pd.DataFrame:
    """Generates top ISBN recommendations for each cluster."""
    try:
        logger.info("Mapping clusters to users...")
        user_cluster_mapping = pd.DataFrame({
            'user_id': user_indices,
            'cluster_id': clusters
        })

        logger.info("Merging cluster information with raw data...")
        data['cluster_id'] = data['user_id'].map(dict(zip(user_indices, clusters)))

        logger.info("Generating top ISBN recommendations for each cluster...")
        top_books_per_cluster = (
            data.groupby(['cluster_id', 'isbn'])['book_rating']
            .mean()
            .reset_index()
            .sort_values(by=['cluster_id', 'book_rating'], ascending=[True, False])
            .groupby('cluster_id')
            .head(10)
            .groupby('cluster_id')['isbn']
            .apply(list)
            .reset_index()
        )

        logger.info("Cluster recommendations generated successfully.")
        return user_cluster_mapping, top_books_per_cluster
    except Exception as e:
        logger.error(f"Error generating cluster recommendations: {e}")
        raise

def save_results(user_cluster_mapping: pd.DataFrame, top_books_per_cluster: pd.DataFrame, output_dir: str) -> None:
    """Saves the results to CSV files."""
    try:
        logger.info("Saving user-cluster mapping to CSV...")
        user_cluster_mapping_path = os.path.join(output_dir, "user_clusters.csv")
        user_cluster_mapping.to_csv(user_cluster_mapping_path, index=False)

        logger.info("Saving cluster recommendations to CSV...")
        cluster_recommendations_path = os.path.join(output_dir, "cluster_recommendation.csv")
        top_books_per_cluster.to_csv(cluster_recommendations_path, index=False, chunksize=10000)

        logger.info(f"Results saved in {output_dir}.")
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        raise

def main():
    """Main executable for collaborative filtering with clustering."""
    try:
        # Step 1: Read raw data
        raw_data = read_raw_data(RAW_PARQUET_PATH)

        # Step 2: Process user-book matrix
        user_book_sparse, user_indices = process_user_book_matrix(raw_data)

        # Step 3: Perform SVD
        reduced_matrix = perform_svd(user_book_sparse)

        # Step 4: Cluster users
        clusters = cluster_users(reduced_matrix)

        # Step 5: Generate cluster recommendations
        user_cluster_mapping, top_books_per_cluster = generate_cluster_recommendations(raw_data, clusters, user_indices)

        # Step 6: Save results
        save_results(user_cluster_mapping, top_books_per_cluster, OUTPUT_DIR)

    except Exception as e:
        logger.error(f"An error occurred in the main process: {e}")
        raise

if __name__ == "__main__":
    main()
