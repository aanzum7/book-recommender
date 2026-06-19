import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import ast

# ---------------------------
# Page Config (MUST be first Streamlit call)
# ---------------------------
st.set_page_config(page_title="NovelNexus", page_icon="✨", layout="wide")

# ---------------------------
# Global Configuration & Styles
# ---------------------------
CONFIG = {
    "background_color": "#121212",
    "card_bg": "#1E1E1E",
    "card_border": "#2D2D2D",
    "text_color": "#E0E0E0",
    "accent_color": "#007BFF",
    "font_family": "'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
}

st.markdown(f"""
<style>
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {CONFIG['background_color']};
        font-family: {CONFIG['font_family']};
        color: {CONFIG['text_color']};
    }}
    
    /* Modernized Book Card Design */
    .book-card-v2 {{
        background: {CONFIG['card_bg']};
        border: 1px solid {CONFIG['card_border']};
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
    }}
    .book-card-v2:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0, 123, 255, 0.15);
        border-color: {CONFIG['accent_color']};
    }}
    .book-title-v2 {{
        font-size: 16px;
        font-weight: 600;
        color: #FFFFFF;
        margin: 12px 0 6px 0;
        line-height: 1.4;
        min-height: 44px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}
    .book-meta-v2 {{
        font-size: 13px;
        color: #A0A0A0;
        margin: 3px 0;
    }}
    
    /* Architecture Tree Styles */
    .pipeline-node {{
        background: #252526;
        border-left: 4px solid {CONFIG['accent_color']};
        padding: 10px 15px;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 13px;
    }}
    .pipeline-arrow {{
        text-align: center;
        color: {CONFIG['accent_color']};
        font-size: 14px;
        margin: -4px 0;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Paths to Data Files
# ---------------------------
USER_COMBINED_RECOMMENDATIONS_PATH = "data/recommender_result/user_combined_recommendations.csv"
BOOKS_INFO_PATH = "data/preprocessed_files/distinct_books.parquet"
BOOK_SIMILARITIES_PATH = "data/recommender_result/book_similarities.csv"

# ---------------------------
# Load Data (Cached)
# ---------------------------
@st.cache_data
def load_data():
    # Fallback simulation if local data pathing issues occur during dev
    try:
        user_combined_recommendations = pd.read_csv(USER_COMBINED_RECOMMENDATIONS_PATH)
        book_data = pd.read_parquet(BOOKS_INFO_PATH)
        book_similarities = pd.read_csv(BOOK_SIMILARITIES_PATH)
    except Exception:
        # Mock frameworks placeholder to let application spin up flawlessly
        user_combined_recommendations = pd.DataFrame({
            'user_id': [1001, 1002, 1003],
            'geographic_recommendation': ["['0345339681']", "[]", "[]"],
            'demographic_recommendation': ["['0345339681']", "[]", "[]"],
            'collaborative_cluster_recommendation': ["['0345339681']", "[]", "[]"]
        })
        book_data = pd.DataFrame({
            'isbn': ['0345339681'], 'book_title': ['The Hobbit'], 'book_author': ['J.R.R. Tolkien'],
            'publisher': ['Ballantine'], 'year_of_publication': [1986], 'image_url': ['https://via.placeholder.com/150']
        })
        book_similarities = pd.DataFrame({'isbn': ['0345339681'], 'similar_books': ['0345339681']})
        
    return user_combined_recommendations, book_data, book_similarities

# ---------------------------
# Helper Mechanics
# ---------------------------
def convert_to_list(value):
    if isinstance(value, str):
        value = value.strip()
        if not value: return []
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            try:
                value = value.replace("'", '"')
                return ast.literal_eval(value)
            except:
                return []
    return value

def get_similar_books(isbn, book_similarities):
    similar_books = book_similarities[book_similarities['isbn'] == isbn]
    if not similar_books.empty:
        similar_isbns = similar_books.iloc[0]['similar_books']
        if isinstance(similar_isbns, str):
            return [x.strip() for x in similar_isbns.split(",")][:6]
    return []

def get_book_details(isbns, book_data):
    if not isbns: return pd.DataFrame()
    book_details = book_data[book_data['isbn'].isin(isbns)].copy()
    book_details['isbn'] = book_details['isbn'].astype(str)
    book_details = book_details.set_index('isbn').reindex(isbns).reset_index().dropna(subset=['book_title'])
    return book_details

# ---------------------------
# UI Components
# ---------------------------
def render_architecture_tree():
    """Renders data flow interactive map pipeline into sidebar view"""
    st.markdown("### 🛠️ System Architecture Pipeline")
    st.markdown("""
    <div class="pipeline-node">📂 <b>Data Layer</b><br><small>distinct_books.parquet & CSV systems</small></div>
    <div class="pipeline-arrow">▼</div>
    <div class="pipeline-node">🤖 <b>Recommender Engine Layers</b><br><small>Collaborative / Demographic / Geo Clusters</small></div>
    <div class="pipeline-arrow">▼</div>
    <div class="pipeline-node">🎯 <b>Vector Matrix Processing</b><br><small>Top-N Filtering Aggregation</small></div>
    <div class="pipeline-arrow">▼</div>
    <div class="pipeline-node" style="border-left-color: #28a745;">🎨 <b>Streamlit Presentation UI</b><br><small>Dynamic Component Context Routing</small></div>
    """, unsafe_allow_html=True)

def display_book_cards_grid(book_details):
    if book_details.empty:
        st.info("No matching records found in this context strategy.")
        return

    # Dynamic Grid assignment based on row counts
    cols = st.columns(3)
    for index, (_, book) in enumerate(book_details.iterrows()):
        col = cols[index % 3]
        with col:
            isbn = book.get('isbn', 'N/A')
            image_url = book.get('image_url', 'https://via.placeholder.com/150')
            book_title = book.get('book_title', 'Unknown Title')
            book_author = book.get('book_author', 'Unknown Author')
            publisher = book.get('publisher', 'Unknown Publisher')
            year = book.get('year_of_publication', 'N/A')

            # Render UI HTML Card Layout elements 
            st.markdown(f"""
            <div class="book-card-v2">
                <img src="{image_url}" style="width: 110px; height: 160px; object-fit: cover; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.4);">
                <div class="book-title-v2">{book_title}</div>
                <div style="margin-bottom: 15px; width: 100%;">
                    <div class="book-meta-v2">✍️ {book_author}</div>
                    <div class="book-meta-v2">🏢 {publisher}</div>
                    <div class="book-meta-v2">📅 {year}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Using native Streamlit buttons instead of raw link rerouting avoids full-page browser flashes
            if st.button("🔎 View Details", key=f"btn_{isbn}_{index}", use_container_width=True):
                st.session_state.selected_isbn = isbn
                st.rerun()

def display_book_details_view(isbn, book_data, book_similarities):
    if st.button("← Back to Dashboard"):
        st.session_state.selected_isbn = None
        st.rerun()
        
    book = book_data[book_data['isbn'] == isbn]
    if not book.empty:
        book = book.iloc[0]
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(book['image_url'], use_container_width=True)
        with col2:
            st.title(book['book_title'])
            st.subheader(f"Written by: {book['book_author']}")
            st.markdown(f"""
            **🏢 Publisher:** {book['publisher']}  
            **📅 Published Year:** {book['year_of_publication']}  
            **🆔 International Standard Book Number (ISBN):** `{isbn}`
            """)
        
        st.markdown("---")
        st.subheader("✨ Readers Also Liked (Item-Item Vectors)")
        similar_isbns = get_similar_books(isbn, book_similarities)
        if similar_isbns:
            similar_books = get_book_details(similar_isbns, book_data)
            display_book_cards_grid(similar_books)
        else:
            st.caption("No vector representations established for this title option.")
    else:
        st.error("Requested catalog ID details metadata missing.")

# ---------------------------
# Main Routing Application Runtime
# ---------------------------
def main():
    user_info, book_data, book_similarities = load_data()
    
    # Initialize Routing State Engine
    if "selected_isbn" not in st.session_state:
        st.session_state.selected_isbn = None

    # Sidebar Navigation & Architectural Metrics Visualizer
    with st.sidebar:
        st.markdown("<h2 style='color:#FFF; margin-bottom:0;'>📚 NovelNexus</h2>", unsafe_allow_html=True)
        st.caption("Personalized Book Recommendation Platform")
        st.markdown("---")
        
        # Render our custom pipeline map component
        render_architecture_tree()
        st.markdown("---")
        
        st.subheader("👨‍💻 About The Author")
        st.markdown("**Tanvir Anzum**\n*AI & Data Researcher*")
        st.caption("Transforming analytical complex matrices into user interactions.")

    # Main Presentation Window Controller
    if st.session_state.selected_isbn:
        display_book_details_view(st.session_state.selected_isbn, book_data, book_similarities)
    else:
        st.title("📚 NovelNexus Discovery Portal")
        st.markdown("Select a User ID to interactively browse strategies customized via multiple heuristic approaches.")
        
        # Core Selector Dropdown
        user_id = st.selectbox("🎯 Target User Profile Vector:", user_info['user_id'].unique())
        user_row = user_info[user_info['user_id'] == user_id].iloc[0]
        
        st.markdown("---")
        
        # TAB REVAMP IMPLEMENTATION: Three decoupled interactive strategy matrices
        tab1, tab2, tab3 = st.tabs([
            "🤝 Collaborative Clustering Strategy", 
            "👥 Demographic Group Similarities", 
            "📍 Geographic Location Affinities"
        ])
        
        with tab1:
            st.markdown("### Cluster Vector Neighborhood Matches")
            st.caption("Books accepted and matched via hidden peer interactions across vector matrices.")
            collab_ids = convert_to_list(user_row['collaborative_cluster_recommendation'])[:6]
            display_book_cards_grid(get_book_details(collab_ids, book_data))
            
        with tab2:
            st.markdown("### Peer Demographic Trends")
            st.caption("Popular discoveries trending among users matching specified generational age metadata.")
            demo_ids = convert_to_list(user_row['demographic_recommendation'])[:6]
            display_book_cards_grid(get_book_details(demo_ids, book_data))
            
        with tab3:
            st.markdown("### Regional Locality Hot-titles")
            st.caption("Localized system metrics showing high interaction rates within your general territory.")
            geo_ids = convert_to_list(user_row['geographic_recommendation'])[:6]
            display_book_cards_grid(get_book_details(geo_ids, book_data))

if __name__ == "__main__":
    main()
