"""
Centralized Configuration for Book Recommender Pipeline.
Defines paths, thresholds, and hyperparameters for all data and ML stages.
"""
import os
from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data Directories
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw_files")
PREPROCESSED_DATA_DIR = os.path.join(DATA_DIR, "preprocessed_files")
RECOMMENDER_RESULT_DIR = os.path.join(DATA_DIR, "recommender_result")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Data File Paths
BOOKS_RAW_CSV = os.path.join(RAW_DATA_DIR, "Books.csv")
RATINGS_RAW_CSV = os.path.join(RAW_DATA_DIR, "Ratings.csv")
USERS_RAW_CSV = os.path.join(RAW_DATA_DIR, "Users.csv")

RAW_PARQUET = os.path.join(PREPROCESSED_DATA_DIR, "raw_data.parquet")
DISTINCT_USERS_PARQUET = os.path.join(PREPROCESSED_DATA_DIR, "distinct_user_age_location.parquet")
DISTINCT_BOOKS_PARQUET = os.path.join(PREPROCESSED_DATA_DIR, "distinct_books.parquet")

TOP_ISBN_AGE_GROUP_JSON = os.path.join(RECOMMENDER_RESULT_DIR, "top_isbn_per_age_group.json")
TOP_ISBN_LOCATION_JSON = os.path.join(RECOMMENDER_RESULT_DIR, "top_isbn_per_location.json")
USER_CLUSTERS_CSV = os.path.join(RECOMMENDER_RESULT_DIR, "user_clusters.csv")
CLUSTER_RECOMMENDATION_CSV = os.path.join(RECOMMENDER_RESULT_DIR, "cluster_recommendation.csv")
BOOK_SIMILARITIES_CSV = os.path.join(RECOMMENDER_RESULT_DIR, "book_similarities.csv")
USER_COMBINED_RECOMMENDATIONS_CSV = os.path.join(RECOMMENDER_RESULT_DIR, "user_combined_recommendations.csv")

# Remote Ingestion Config (Google Drive)
DRIVE_FOLDER_ID = "1fhUg8fnBsAe-ktK0Eq3o7zWtvkmh0J7M"
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "config", "service_account", "json_key_google_drive.json")
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Preprocessing Thresholds
MIN_USER_RATINGS = 5
MIN_BOOK_RATINGS = 10

# Recommendation Model Hyperparameters
SVD_COMPONENTS = 100
KMEANS_CLUSTERS = 30
RANDOM_STATE = 42

# Demographic & Geographic Scoring Weights
WEIGHT_AVG_RATING = 0.8
WEIGHT_USER_COUNT = 0.2
TOP_N_RECOMMENDATIONS = 10
