import streamlit as st # type: ignore
import pandas as pd # type: ignore
import ast

# Paths to the data files
USER_COMBINED_RECOMMENDATIONS_PATH = "data/recommender_result/user_combined_recommendations.csv"
BOOKS_INFO_PATH = "data/preprocessed_files/distinct_books.parquet"

# Load user recommendations data
def load_data():
    user_combined_recommendations = pd.read_csv(USER_COMBINED_RECOMMENDATIONS_PATH)
    book_data = pd.read_parquet(BOOKS_INFO_PATH)
    return user_combined_recommendations, book_data

# Convert string to list if necessary
def convert_to_list(value):
    """Safely convert string representation of a list to an actual list."""
    if isinstance(value, str):
        try:
            # Clean the value and convert it to a list
            value = value.strip().replace("'", '"')
            return ast.literal_eval(value)
        except (ValueError, SyntaxError) as e:
            print(f"Error converting value to list: {value} - {e}")
            return []  # Return empty list if conversion fails
    return value  # If it's already a list, return as is

# Fetch book details from book_data based on ISBNs
def get_book_details(isbns, book_data):
    """Fetch book details from book_data based on ISBNs."""
    # Clean ISBNs by trimming spaces and quotes, then filter the book data
    isbns = [str(isbn).strip().replace('"', '').replace("'", "") for isbn in isbns]  # Clean ISBNs
    book_details = book_data[book_data['isbn'].isin(isbns)][['isbn', 'book_title', 'book_author', 'year_of_publication', 'publisher', 'image_url']]
    return book_details

# Display user recommendations
def display_recommendations(user_info, book_data):
    user_id = st.selectbox("Select User ID", user_info['user_id'].unique())

    # Get user recommendations for selected user
    user = user_info[user_info['user_id'] == user_id].iloc[0]
    geo_recommendation = user['geographic_recommendation']
    demographic_recommendation = user['demographic_recommendation']
    collaborative_recommendation = user['collaborative_cluster_recommendation']

    # Convert string to list if necessary and limit to 5 recommendations
    geo_recommendation = convert_to_list(geo_recommendation)[:5]
    demographic_recommendation = convert_to_list(demographic_recommendation)[:5]
    collaborative_recommendation = convert_to_list(collaborative_recommendation)[:5]

    # Fetch book details for each category
    geo_books = get_book_details(geo_recommendation, book_data)
    demo_books = get_book_details(demographic_recommendation, book_data)
    collab_books = get_book_details(collaborative_recommendation, book_data)

    # Display recommendations as book details
    st.subheader(f"Top 5 Books for User {user_id}")

    st.write("### 1. From Your City (Geographic Recommendations):")
    if not geo_books.empty:
        st.write(geo_books)

    st.write("### 2. From Your Age Group (Demographic Recommendations):")
    if not demo_books.empty:
        st.write(demo_books)

    st.write("### 3. Collaborative Filtering (Cluster Recommendations):")
    if not collab_books.empty:
        st.write(collab_books)

# Main function to run the app
def main():
    # Load data
    user_info, book_data = load_data()

    st.title("Book Recommendations")

    display_recommendations(user_info, book_data)

if __name__ == "__main__":
    main()
