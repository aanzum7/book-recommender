import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import ast

# ---------------------------
# Page Config (MUST be first Streamlit call)
# ---------------------------
st.set_page_config(page_title="NovelNexus",  page_icon="✨",  layout="wide")

# ---------------------------
# Global Configuration
# ---------------------------
CONFIG = {
    "background_color": "#3D2A17",
    "font_family": "Georgia, serif",
    "card": {
        "bg": "#ffffff",
        "border": "#e0e0e0",
        "radius": "12px",
        "padding": "15px",
        "margin": "10px 0",
        "shadow": "2px 2px 8px rgba(0,0,0,0.05)",
        "hover_shadow": "4px 4px 12px rgba(0,0,0,0.1)",
        "hover_transform": "translateY(-4px)"
    },
    "card_title_color": "#2c2c2c",
    "card_meta_color": "#555",
    "button": {
        "bg": "#063F7D",
        "hover_bg": "#061320",
        "color": "white",
        "radius": "6px",
        "padding": "6px 12px",
        "font_size": "13px"
    },
    "sidebar": {
        "title_size": "22px",
        "subtitle_size": "14px",
        "link_color": "#007BFF"
    },
    "recommendation_header": {
        "bg": "#eaf2ff",
        "color": "#1a3d7c",
        "highlight_color": "#007BFF",
        "padding": "12px 20px",
        "radius": "10px",
        "font_size": "20px",
        "font_weight": "600"
    }
}

# ---------------------------
# Apply Global Theme
# ---------------------------
st.markdown(f"""
<style>
body {{
    background-color: {CONFIG['background_color']};
    font-family: {CONFIG['font_family']};
}}
.stApp {{
    background-color: {CONFIG['background_color']};
}}
.book-card {{
    border: 1px solid {CONFIG['card']['border']};
    border-radius: {CONFIG['card']['radius']};
    padding: {CONFIG['card']['padding']};
    margin: {CONFIG['card']['margin']};
    background-color: {CONFIG['card']['bg']};
    text-align: center;
    transition: all 0.2s ease-in-out;
    box-shadow: {CONFIG['card']['shadow']};
}}
.book-card:hover {{
    transform: {CONFIG['card']['hover_transform']};
    box-shadow: {CONFIG['card']['hover_shadow']};
}}
.book-title {{
    font-size: 16px;
    font-weight: 600;
    color: {CONFIG['card_title_color']};
    margin: 10px 0;
}}
.book-meta {{
    font-size: 14px;
    color: {CONFIG['card_meta_color']};
    margin: 2px 0;
}}
.view-btn {{
    display: inline-block;
    margin-top: 10px;
    padding: {CONFIG['button']['padding']};
    background-color: {CONFIG['button']['bg']};
    color: {CONFIG['button']['color']};
    text-decoration: none;
    border-radius: {CONFIG['button']['radius']};
    font-size: {CONFIG['button']['font_size']};
    transition: background 0.2s;
}}
.view-btn:hover {{
    background-color: {CONFIG['button']['hover_bg']};
}}
.sidebar-title {{ font-size: {CONFIG['sidebar']['title_size']}; font-weight: 600; margin-bottom: 0.2rem; }}
.sidebar-subtitle {{ font-size: {CONFIG['sidebar']['subtitle_size']}; font-weight: normal; line-height: 1.5; }}
.link-block a {{ text-decoration: none; color: {CONFIG['sidebar']['link_color']}; font-weight: 600; }}
.recommendation-header {{
    background-color: {CONFIG['recommendation_header']['bg']};
    color: {CONFIG['recommendation_header']['color']};
    padding: {CONFIG['recommendation_header']['padding']};
    border-radius: {CONFIG['recommendation_header']['radius']};
    font-size: {CONFIG['recommendation_header']['font_size']};
    font-weight: {CONFIG['recommendation_header']['font_weight']};
    display: inline-block;
    margin-bottom: 15px;
}}
.recommendation-header span {{
    color: {CONFIG['recommendation_header']['highlight_color']};
}}
</style>
""", unsafe_allow_html=True)

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

                max_title_length = 22
                if len(book_title) > max_title_length:
                    book_title = book_title[:max_title_length] + "..."

                st.markdown(
                    f"""
                    <div class="book-card">
                        <img src="{image_url}" alt="{book_title}" style="width: 100px; height: 150px; object-fit: cover; margin-bottom: 10px;">
                        <div class="book-title">{book_title}</div>
                        <div class="book-meta">✍️ {book_author}</div>
                        <div class="book-meta">🏢 {publisher}</div>
                        <div class="book-meta">📅 {year}</div>
                        <a href="/?view_details={isbn}" class="view-btn">View Details</a>
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
        st.write(f"**📖 Title:** {book['book_title']}")
        st.write(f"**✍️ Author:** {book['book_author']}")
        st.write(f"**🏢 Publisher:** {book['publisher']}")
        st.write(f"**📅 Year:** {book['year_of_publication']}")

        similar_isbns = get_similar_books(isbn, book_similarities)
        if similar_isbns:
            st.subheader("✨ People also read:")
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

    # Stylish recommendations header
    st.markdown(
        f"""
        <div class="recommendation-header">
            📖 Recommendations for User <span>{user_id}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    user = user_info[user_info['user_id'] == user_id].iloc[0]
    geo_recommendation = convert_to_list(user['geographic_recommendation'])[:5]
    demographic_recommendation = convert_to_list(user['demographic_recommendation'])[:5]
    collaborative_recommendation = convert_to_list(user['collaborative_cluster_recommendation'])[:5]

    geo_books = get_book_details(geo_recommendation, book_data)
    demo_books = get_book_details(demographic_recommendation, book_data)
    collab_books = get_book_details(collaborative_recommendation, book_data)

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
    user_info, book_data, book_similarities = load_data()

    # Sidebar
    with st.sidebar:
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
            <div class='link-block'>
                <a href="https://www.linkedin.com/in/aanzum" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn" width="16">
                    <strong>LinkedIn</strong>
                </a>
                &nbsp;&nbsp;
                <a href="https://www.researchgate.net/profile/Tanvir-Anzum" target="_blank">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/5/5e/ResearchGate_icon_SVG.svg" alt="ResearchGate" width="16">
                    <strong>Research</strong>
                </a>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

    # Main content
    st.title("📚 NovelNexus")
    st.subheader("✨ Where stories meet your interests.")

    query_params = st.query_params
    if "view_details" in query_params:
        isbn = query_params["view_details"]
        display_book_details(isbn, book_data, book_similarities)
    else:
        display_recommendations(user_info, book_data, book_similarities)

if __name__ == "__main__":
    main()
