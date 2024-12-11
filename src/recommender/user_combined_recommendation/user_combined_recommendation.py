import os
import pandas as pd # type: ignore
import json
import logging
from config.logging_configs import logger  # Ensure logging is set up

# Define paths
USER_AGE_LOCATION_PATH = "data/preprocessed_files/distinct_user_age_location.parquet"
AGE_GROUP_RECOMMENDATION_PATH = "data/recommender_result/top_isbn_per_age_group.json"
GEO_LOCATION_RECOMMENDATION_PATH = "data/recommender_result/top_isbn_per_location.json"
USER_CLUSTER_MAPPING_PATH = "data/recommender_result/user_clusters.csv"
CLUSTER_RECOMMENDATION_PATH = "data/recommender_result/cluster_recommendation.csv"
OUTPUT_PATH = "data/recommender_result/user_combined_recommendations.csv"

def load_user_info(file_path: str) -> pd.DataFrame:
    """Loads user info including user_id, location, and age_group."""
    try:
        logger.info(f"Loading user info from {file_path}...")
        return pd.read_parquet(file_path)
    except Exception as e:
        logger.error(f"Error loading user info: {e}")
        raise

def load_recommendations(file_path: str, is_json: bool = False) -> dict:
    """Loads recommendation data from a file."""
    try:
        logger.info(f"Loading recommendation data from {file_path}...")
        if is_json:
            with open(file_path, 'r') as file:
                return json.load(file)
        else:
            return pd.read_csv(file_path)
    except Exception as e:
        logger.error(f"Error loading recommendations: {e}")
        raise

def map_recommendations(
    user_info: pd.DataFrame, 
    age_group_rec: dict, 
    geo_rec: dict, 
    cluster_mapping: pd.DataFrame, 
    cluster_rec: pd.DataFrame
) -> pd.DataFrame:
    """
    Maps recommendations to each user based on demographic, geographic, and collaborative cluster filtering.
    """
    try:
        logger.info("Starting the mapping of recommendations to users...")

        # Step 1: Validate user_info DataFrame and add missing columns if necessary
        if "age_group" not in user_info.columns:
            logger.warning("'age_group' column not found in user_info. Adding default value.")
            user_info["age_group"] = "Unknown"
        if "location" not in user_info.columns:
            logger.warning("'location' column not found in user_info. Adding default value.")
            user_info["location"] = "Unknown"

        # Step 2: Map cluster IDs to users
        logger.info("Mapping cluster IDs to users...")
        cluster_mapping_dict = cluster_mapping.set_index("user_id")["cluster_id"].to_dict()
        user_info["cluster_id"] = user_info["user_id"].map(cluster_mapping_dict)

        # Step 3: Map collaborative cluster recommendations
        logger.info("Mapping collaborative recommendations based on cluster IDs...")
        cluster_rec_dict = cluster_rec.set_index("cluster_id")["isbn"].apply(eval).to_dict()  # Ensure isbn is a list
        user_info["collaborative_cluster_recommendation"] = user_info["cluster_id"].map(cluster_rec_dict)

        # Step 4: Map demographic recommendations based on age group
        logger.info("Mapping demographic recommendations...")
        user_info["demographic_recommendation"] = user_info["age_group"].map(age_group_rec)

        # Step 5: Map geographic recommendations based on location
        logger.info("Mapping geographic recommendations...")
        user_info["geographic_recommendation"] = user_info["location"].map(geo_rec)

        # Step 6: Fill missing values with empty lists
        logger.info("Filling missing recommendations with empty lists...")
        recommendation_columns = [
            "collaborative_cluster_recommendation", 
            "demographic_recommendation", 
            "geographic_recommendation"
        ]
        for column in recommendation_columns:
            user_info[column] = user_info[column].apply(lambda x: x if isinstance(x, list) else [])

        logger.info("Recommendations mapped successfully.")
        return user_info

    except KeyError as ke:
        logger.error(f"KeyError during mapping: {ke}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during recommendation mapping: {e}")
        raise

def save_combined_recommendations(user_info: pd.DataFrame, output_path: str) -> None:
    """Saves the combined recommendations to a CSV file."""
    try:
        logger.info(f"Saving combined recommendations to {output_path}...")
        user_info.to_csv(output_path, index=False)
        logger.info(f"Combined recommendations saved successfully to {output_path}.")
    except Exception as e:
        logger.error(f"Error saving combined recommendations: {e}")
        raise

def main():
    """Main executable for mapping user recommendations."""
    try:
        # Step 1: Load user info
        user_info = load_user_info(USER_AGE_LOCATION_PATH)

        # Step 2: Load recommendations
        age_group_rec = load_recommendations(AGE_GROUP_RECOMMENDATION_PATH, is_json=True)
        geo_rec = load_recommendations(GEO_LOCATION_RECOMMENDATION_PATH, is_json=True)
        cluster_mapping = load_recommendations(USER_CLUSTER_MAPPING_PATH)
        cluster_rec = load_recommendations(CLUSTER_RECOMMENDATION_PATH)

        # Step 3: Map recommendations
        combined_user_info = map_recommendations(user_info, age_group_rec, geo_rec, cluster_mapping, cluster_rec)

        # Step 4: Save combined recommendations
        save_combined_recommendations(combined_user_info, OUTPUT_PATH)

    except Exception as e:
        logger.error(f"An error occurred in the main process: {e}")
        raise

if __name__ == "__main__":
    main()
