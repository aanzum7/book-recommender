import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import ast

# Paths to the data files
USER_COMBINED_RECOMMENDATIONS_PATH = "data/recommender_result/user_combined_recommendations.csv"
BOOKS_INFO_PATH = "data/preprocessed_files/distinct_books.parquet"
BOOK_SIMILARITIES_PATH = "data/recommender_result/book_similarities.csv"

# Load user recommendations data and book similarities data
@st.cache_data
def load_data():
    user_combined_recommendations = pd.read_csv(USER_COMBINED_RECOMMENDATIONS_PATH)
    book_data = pd.read_parquet(BOOKS_INFO_PATH)
    book_similarities = pd.read_csv(BOOK_SIMILARITIES_PATH)
    return user_combined_recommendations, book_data, book_similarities

# Convert string to list if necessary
def convert_to_list(value):
    """Safely convert string representation of a list to an actual list."""
    if isinstance(value, str):
        value = value.strip()
        if not value:  # Check for empty strings
            return []
        try:
            value = value.replace("'", '"')  # Ensure correct quotation marks
            return ast.literal_eval(value)
        except (ValueError, SyntaxError) as e:
            st.warning(f"Error converting value to list: {value} - {e}")
            return []  # Return empty list if conversion fails
    return value  # If it's already a list, return as is

# Fetch similar books from book_similarities data (with proper ranking)
def get_similar_books(isbn, book_similarities):
    """Fetch top similar books based on ISBN and maintain their order."""
    similar_books = book_similarities[book_similarities['isbn'] == isbn]
    if not similar_books.empty:
        # Parse the similar books, ensuring they are ranked properly
        similar_isbns = similar_books.iloc[0]['similar_books']
        similar_isbns = [isbn.strip() for isbn in similar_isbns.split(",")]  # Maintain original ranking
        return similar_isbns[:5]  # Get top 5 similar books
    return []

# Fetch book details from book_data based on ISBNs
def get_book_details(isbns, book_data):
    """Fetch book details from book_data based on ISBNs and maintain input order."""
    if not isbns:
        return pd.DataFrame()
    # Filter book_data for the given ISBNs
    book_details = book_data[book_data['isbn'].isin(isbns)].copy()  # Explicitly create a copy
    # Ensure the order matches the order of ISBNs provided
    book_details.loc[:, 'isbn'] = book_details['isbn'].astype(str)  # Use .loc to avoid SettingWithCopyWarning
    book_details = book_details.set_index('isbn').reindex(isbns).reset_index()
    return book_details

# Display book cards with a "View Details" option
def display_book_cards_in_columns(book_details, columns):
    """Display books in the specified columns with a clean and consistent card style."""
    if not book_details.empty:
        for index, (_, book) in enumerate(book_details.iterrows()):  # Iterate through book details
            col = columns[index % len(columns)]  # Rotate through the columns
            with col:
                # Safely handle missing values using .get()
                isbn = book.get('isbn', 'N/A')
                image_url = book.get('image_url', 'https://via.placeholder.com/150')
                book_title = book.get('book_title', 'Unknown Title')
                book_author = book.get('book_author', 'Unknown Author')
                publisher = book.get('publisher', 'Unknown Publisher')
                year = book.get('year_of_publication', 'N/A')

                # Truncate the book title to a maximum of two lines
                max_title_length = 20  # Adjust title length limit
                if len(book_title) > max_title_length:
                    book_title = book_title[:max_title_length] + "..."

                # Truncate author, publisher, and year to a maximum of one line
                max_line_length = 15  # Adjust to fit the one-line limit for author/publisher/year
                if len(book_author) > max_line_length:
                    book_author = book_author[:max_line_length] + "..."
                if len(publisher) > max_line_length:
                    publisher = publisher[:max_line_length] + "..."
                if len(str(year)) > max_line_length:
                    year = str(year)[:max_line_length] + "..."

                # Create a styled card for each book
                st.markdown(
                    f"""
                    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin: 10px; 
                                background-color: #f9f9f9; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                        <img src="{image_url}" alt="{book_title}" style="width: 100px; height: 150px; object-fit: cover; margin-bottom: 10px;">
                        <h4 style="font-size: 16px; margin: 10px 0; color: #333; overflow-wrap: break-word; 
                                    white-space: nowrap; text-overflow: ellipsis; display: -webkit-box; 
                                    -webkit-line-clamp: 2; -webkit-box-orient: vertical; word-wrap: break-word;">{book_title}</h4>
                        <p style="font-size: 14px; margin: 5px 0; color: #555; overflow-wrap: break-word; 
                                  white-space: nowrap; text-overflow: ellipsis; display: -webkit-box; 
                                  -webkit-line-clamp: 1; -webkit-box-orient: vertical;">Author: {book_author}</p>
                        <p style="font-size: 14px; margin: 5px 0; color: #555; overflow-wrap: break-word; 
                                  white-space: nowrap; text-overflow: ellipsis; display: -webkit-box; 
                                  -webkit-line-clamp: 1; -webkit-box-orient: vertical;">Publisher: {publisher}</p>
                        <p style="font-size: 14px; margin: 5px 0; color: #555; overflow-wrap: break-word; 
                                  white-space: nowrap; text-overflow: ellipsis; display: -webkit-box; 
                                  -webkit-line-clamp: 1; -webkit-box-orient: vertical;">Year: {year}</p>
                        <a href="/?view_details={isbn}" style="display: inline-block; margin-top: 10px; padding: 5px 10px; 
                            background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px;">
                            View Details
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.write("No books found for the selected recommendations.")


# Display book details
def display_book_details(isbn, book_data, book_similarities):
    """Display detailed information about a book, including similar books (ordered)."""
    book = book_data[book_data['isbn'] == isbn]
    if not book.empty:
        book = book.iloc[0]
        st.image(book['image_url'], width=200)
        st.write(f"**Title:** {book['book_title']}")
        st.write(f"**Author:** {book['book_author']}")
        st.write(f"**Publisher:** {book['publisher']}")
        st.write(f"**Year of Publication:** {book['year_of_publication']}")
        
        # Fetch similar books and maintain order
        similar_isbns = get_similar_books(isbn, book_similarities)
        if similar_isbns:
            st.subheader("People also read:")
            similar_books = get_book_details(similar_isbns, book_data)
            if not similar_books.empty:
                columns = st.columns(3)  # Three columns for web
                display_book_cards_in_columns(similar_books, columns)
            else:
                st.write("No similar books found.")
        else:
            st.write("No similar books found.")
    else:
        st.write("Book details not found.")

# Display user recommendations
def display_recommendations(user_info, book_data, book_similarities):
    user_id = st.selectbox("Personalized for User ID", user_info['user_id'].unique())

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

    st.subheader(f"Personalized recommendations for User {user_id}")

    # Collapsible sections (expanded by default)
    with st.expander("Recommended for You (Collaborative Clustering)", expanded=True):
        columns = st.columns(3)  # Three columns for web
        display_book_cards_in_columns(collab_books, columns)

    with st.expander("People of Your Age also read (Demographic Recommendations)", expanded=True):
        columns = st.columns(3)  # Three columns for web
        display_book_cards_in_columns(demo_books, columns)

    with st.expander("People from Your City also read (Geographic Recommendations)", expanded=True):
        columns = st.columns(3)  # Three columns for web
        display_book_cards_in_columns(geo_books, columns)

# Main function
def main():
    user_info, book_data, book_similarities = load_data()
    st.title("NovelNexus")
    st.subheader("Where stories meet your interests.")

    # Display author information in the sidebar
    st.sidebar.title("About the Author")
    st.sidebar.markdown("**Tanvir Anzum**")

    # Check if "view_details" is in the query params
    query_params = st.query_params
    if "view_details" in query_params:
        isbn = query_params["view_details"]
        display_book_details(isbn, book_data, book_similarities)
    else:
        display_recommendations(user_info, book_data, book_similarities)

if __name__ == "__main__":
    main()
