# main.py

# Importing required functions from different modules for the main script.
from src.data_inject import fetch_raw_data
from src.data_preprocessing import preprocessing_raw_data, users, books
from src.recommender.deomgraphic_recommender import age_group_recommender
from src.recommender.geographic_recommender import geo_locational_recommender
from src.recommender.collaborative_filtering_recommender import recommended_for_you
from src.recommender.collaborative_filtering_recommender import people_also_read
from src.recommender.user_combined_recommendation import user_combined_recommendation

def main():
    # Step 1: Fetch raw data from the source and save it for further processing.
    fetch_raw_data.main()  # Call the fetch function to download files

    # Step 2: Preprocess the raw data to make it suitable for analysis.
    preprocessing_raw_data.main()

    # Step 3: Process and prepare user data for recommendation purposes.
    users.main()

    # Step 4: Process and prepare book data for recommendation purposes.
    books.main()

    # Step 5: Generate age-group-based recommendations.
    age_group_recommender.main()

    # Step 6: Generate location-based recommendations.
    geo_locational_recommender.main()

    # Step 7: Generate personalized recommendations using cluster collaborative filtering.
    recommended_for_you.main()

    # Step 8: Combine recommendations (collaborative filtering, demographic, and geographic)
    # This step aggregates and maps all personalized recommendations for each user
    # including cluster-based recommendations, demographic-based suggestions, and geographic-based suggestions.
    user_combined_recommendation.main()
    
    # Step 9: The "people_also_read.main()" method will suggest books that other users, in the same cluster, have also interacted with.
    people_also_read.main()


    
if __name__ == "__main__":
    main()
