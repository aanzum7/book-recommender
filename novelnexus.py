import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import ast

# ---------------------------
# Paths to the data files
# ---------------------------
USER_COMBINED_RECOMMENDATIONS_PATH = "data/recommender_result/user_combined_recommendations.csv"
BOOKS_INFO_PATH = "data/preprocessed_files/distinct_books.parquet"
BOOK_SIMILARITIES_PATH = "data/recommender_result/book_similarities.csv"


# ---------------------------
# Load Data
# ---------------------------
@st.cache_data
def load_data():
    user_combined_recommendations = pd.read_csv(USER_COMBINED_RECOMMENDATIONS_PATH)
    book_data = pd.read_parquet(BOOKS_INFO_PATH)
    book_similarities = pd.read_csv(BOOK_SIMILARITIES_PATH)
    return user_combined_recommendations, book_data, book_similarities


# ---------------------------
# Helpers
# ---------------------------
def convert_to_list(value):
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        try:
            value = value.replace("'", '"')
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return []
    return value


def get_similar_books(isbn, book_similarities):
    similar_books = book_similarities[book_similarities['isbn'] == isbn]
    if not similar_books.empty:
        similar_isbns = similar_books.iloc[0]['similar_books']
        similar_isbns = [isbn.strip() for isbn in similar_isbns.split(",")]
        return similar_isbns[:5]
    return []


def get_book_details(isbns, book_data):
    if not isbns:
        return pd.DataFrame()
    book_details = book_data[book_data['isbn'].isin(isbns)].copy()
    book_details.loc[:, 'isbn'] = book_details['isbn'].astype(str)
    book_details = book_details.set_index('isbn').reindex(isbns).reset_index()
    return book_details


def display_book_cards_in_columns(book_details, columns):
    if not book_details.empty:
        for index, (_, book) in enumerate(book_details.iterrows()):
            col = columns[index % len(columns)]
            with col:
                isbn = book.get('isbn', 'N/A')
                image_url = book.get('image_url', 'https://via.placeholder.com/150')
                book_title = book.get('book_title', 'Unknown Title')
                book_author = book.get('book_author', 'Unknown Author')
                publisher = book.get('publisher', 'Unknown Publisher')
                year = book.get('year_of_publication', 'N/A')

                max_title_length = 20
                if len(book_title) > max_title_length:
                    book_title = book_title[:max_title_length] + "..."

                max_line_length = 15
                if len(book_author) > max_line_length:
                    book_author = book_author[:max_line_length] + "..."
                if len(publisher) > max_line_length:
                    publisher = publisher[:max_line_length] + "..."
                if len(str(year)) > max_line_length:
                    year = str(year)[:max_line_length] + "..."

                st.markdown(
                    f"""
                    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin: 10px;
                                background-color: #f9f9f9; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                        <img src="{image_url}" alt="{book_title}" style="width: 100px; height: 150px; object-fit: cover; margin-bottom: 10px;">
                        <h4 style="font-size: 16px; margin: 10px 0; color: #333;">{book_title}</h4>
                        <p style="font-size: 14px; color: #555;">Author: {book_author}</p>
                        <p style="font-size: 14px; color: #555;">Publisher: {publisher}</p>
                        <p style="font-size: 14px; color: #555;">Year: {year}</p>
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


def display_book_details(isbn, book_data, book_similarities):
    book = book_data[book_data['isbn'] == isbn]
    if not book.empty:
        book = book.iloc[0]
        st.image(book['image_url'], width=200)
        st.write(f"**Title:** {book['book_title']}")
        st.write(f"**Author:** {book['book_author']}")
        st.write(f"**Publisher:** {book['publisher']}")
        st.write(f"**Year of Publication:** {book['year_of_publication']}")

        similar_isbns = get_similar_books(isbn, book_similarities)
        if similar_isbns:
            st.subheader("People also read:")
            similar_books = get_book_details(similar_isbns, book_data)
            if not similar_books.empty:
                columns = st.columns(3)
                display_book_cards_in_columns(similar_books, columns)
            else:
                st.write("No similar books found.")
        else:
            st.write("No similar books found.")
    else:
        st.write("Book details not found.")


def display_recommendations(user_info, book_data, book_similarities):
    user_id = st.selectbox("📌 Personalized for User ID", user_info['user_id'].unique())

    user = user_info[user_info['user_id'] == user_id].iloc[0]
    geo_recommendation = convert_to_list(user['geographic_recommendation'])[:5]
    demographic_recommendation = convert_to_list(user['demographic_recommendation'])[:5]
    collaborative_recommendation = convert_to_list(user['collaborative_cluster_recommendation'])[:5]

    geo_books = get_book_details(geo_recommendation, book_data)
    demo_books = get_book_details(demographic_recommendation, book_data)
    collab_books = get_book_details(collaborative_recommendation, book_data)

    st.subheader(f"📖 Recommendations for User `{user_id}`")

    with st.expander("🤝 Based on Collaborative Clustering", expanded=True):
        display_book_cards_in_columns(collab_books, st.columns(3))

    with st.expander("👥 Based on Similar Age Group", expanded=True):
        display_book_cards_in_columns(demo_books, st.columns(3))

    with st.expander("📍 Based on Same Location", expanded=True):
        display_book_cards_in_columns(geo_books, st.columns(3))


# ---------------------------
# Main
# ---------------------------
def main():
    st.set_page_config(page_title="NovelNexus", layout="wide")
    user_info, book_data, book_similarities = load_data()

    # Sidebar
    with st.sidebar:
        st.markdown(
            """
            <style>
            .sidebar-title { font-size: 22px; font-weight: 600; margin-bottom: 0.2rem; }
            .sidebar-subtitle { font-size: 14px; font-weight: normal; line-height: 1.5; }
            .link-block { margin-top: 10px; font-size: 14px; }
            .link-block a { text-decoration: none; color: #007BFF; font-weight: 600; }
            .link-block img { vertical-align: middle; margin-right: 6px; }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div class='sidebar-title'>📚 NovelNexus</div>", unsafe_allow_html=True)
        st.caption(
            "<div class='sidebar-subtitle'>Your personalized <strong>book discovery engine</strong>. Powered by user behavior, demographic, and geographic insights.</div>",
            unsafe_allow_html=True
        )

        st.markdown("---")

        st.title("👨‍💻 About the Author")
        st.caption("Tanvir Anzum – AI & Data Researcher")

        st.markdown("""
            <div style='font-size: 14px; font-weight: normal;'>
            Passionate about turning <strong>data into insights</strong> and building <strong>AI-powered tools</strong> for real-world impact.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
            <div style='font-size: 14px; font-weight: normal;'>
            <br>
            <a href="https://www.linkedin.com/in/aanzum" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn" width="16" style="vertical-align:middle; margin-right:6px;">
                <strong>LinkedIn</strong>
            </a>
            &nbsp;&nbsp;
            <a href="https://www.researchgate.net/profile/Tanvir-Anzum" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/5e/ResearchGate_icon_SVG.svg" alt="ResearchGate" width="16" style="vertical-align:middle; margin-right:6px;">
                <strong>Research</strong>
            </a>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")


    # Main content
    st.title("📚 NovelNexus")
    st.subheader("Where stories meet your interests.")

    query_params = st.query_params
    if "view_details" in query_params:
        isbn = query_params["view_details"]
        display_book_details(isbn, book_data, book_similarities)
    else:
        display_recommendations(user_info, book_data, book_similarities)


if __name__ == "__main__":
    main()
