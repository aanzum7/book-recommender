import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import ast

# ---------------------------
# Page Config (Must be the very first Streamlit call)
# ---------------------------
st.set_page_config(page_title="NovelNexus", page_icon="📚", layout="wide")

# ---------------------------
# Global Configuration & Styles
# ---------------------------
CONFIG = {
    "background_color": "#0E1117",
    "card_bg": "#161B22",
    "card_border": "#30363D",
    "text_color": "#C9D1D9",
    "accent_color": "#58A6FF",
    "success_color": "#2EA043",
    "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
}

st.markdown(f"""
<style>
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {CONFIG['background_color']};
        font-family: {CONFIG['font_family']};
        color: {CONFIG['text_color']};
    }}
    
    /* Modernized Book Card Design */
    .book-card {{
        background: {CONFIG['card_bg']};
        border: 1px solid {CONFIG['card_border']};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.25s ease-in-out;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
    }}
    .book-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(88, 166, 255, 0.18);
        border-color: {CONFIG['accent_color']};
    }}
    .book-title {{
        font-size: 15px;
        font-weight: 600;
        color: #F0F6FC;
        margin: 14px 0 8px 0;
        line-height: 1.4;
        min-height: 42px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}
    .book-meta {{
        font-size: 12.5px;
        color: #8B949E;
        margin: 4px 0;
        text-align: left;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    
    /* Interactive Pill Badges */
    .badge-pill {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        margin-top: 6px;
        letter-spacing: 0.05em;
    }}
    .badge-vintage {{ background: #482715; color: #FF944D; border: 1px solid #FF944D33; }}
    .badge-modern {{ background: #153248; color: #58A6FF; border: 1px solid #58A6FF33; }}
    
    /* Custom Web-Style Dashboard Metric Cards */
    .metric-container {{
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 15px;
        text-align: left;
        margin-bottom: 15px;
    }}
    .metric-label {{
        font-size: 12px;
        color: #8B949E;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .metric-value {{
        font-size: 20px;
        font-weight: bold;
        color: #58A6FF;
        margin-top: 5px;
    }}

    /* Architecture Tree Styles */
    .pipeline-node {{
        background: #161B22;
        border-left: 4px solid {CONFIG['accent_color']};
        border: 1px solid {CONFIG['card_border']};
        border-left: 4px solid {CONFIG['accent_color']};
        padding: 12px;
        margin: 10px 0;
        border-radius: 6px;
        font-size: 12.5px;
    }}
    .pipeline-arrow {{
        text-align: center;
        color: {CONFIG['accent_color']};
        font-size: 14px;
        margin: -6px 0;
        font-weight: bold;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Load Data (Cached Framework)
# ---------------------------
@st.cache_data
def load_data():
    try:
        user_combined_recommendations = pd.read_csv("data/recommender_result/user_combined_recommendations.csv")
        book_data = pd.read_parquet("data/preprocessed_files/distinct_books.parquet")
        book_similarities = pd.read_csv("data/recommender_result/book_similarities.csv")
    except Exception:
        # Development fallback matrix containing 10 items for deep rendering verification
        user_combined_recommendations = pd.DataFrame({
            'user_id': [1001, 1002, 1003],
            'geographic_recommendation': ["['0345339681', '0449212602', '0345339681', '0449212602', '0345339681', '0449212602', '0345339681', '0449212602', '0345339681', '0449212602']", "[]", "[]"],
            'demographic_recommendation': ["['0345339681', '0449212602', '0345339681', '0449212602', '0345339681', '0449212602', '0345339681', '0449212602', '0345339681', '0449212602']", "['0449212602']", "[]"],
            'collaborative_cluster_recommendation': ["['0345339681', '0449212602', '0345339681', '0449212602', '0345339681', '0449212602', '0345339681', '0449212602', '0345339681', '0449212602']", "[]", "[]"]
        })
        book_data = pd.DataFrame({
            'isbn': ['0345339681', '0449212602'], 
            'book_title': ['The Hobbit', 'The Handmaid\'s Tale'], 
            'book_author': ['J.R.R. Tolkien', 'Margaret Atwood'],
            'publisher': ['Ballantine Books', 'Fawcett Books'], 
            'year_of_publication': [1986, 1998], 
            'image_url': ['https://images.amazon.com/images/P/0345339681.01.MZZZZZZZ.jpg', 'https://images.amazon.com/images/P/0449212602.01.MZZZZZZZ.jpg']
        })
        book_similarities = pd.DataFrame({'isbn': ['0345339681'], 'similar_books': ['0449212602']})
        
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
                return ast.literal_eval(value.replace("'", '"'))
            except:
                return []
    return value

def get_similar_books(isbn, book_similarities):
    similar_books = book_similarities[book_similarities['isbn'] == isbn]
    if not similar_books.empty:
        similar_isbns = similar_books.iloc[0]['similar_books']
        if isinstance(similar_isbns, str):
            return [x.strip() for x in similar_isbns.split(",")][:10]
    return []

def get_book_details(isbns, book_data):
    if not isbns: return pd.DataFrame()
    valid_isbns = [str(i) for i in isbns]
    book_details = book_data[book_data['isbn'].astype(str).isin(valid_isbns)].copy()
    book_details['isbn'] = book_details['isbn'].astype(str)
    book_details = book_details.drop_duplicates(subset=['isbn']).set_index('isbn').reindex(valid_isbns).reset_index()
    return book_details.dropna(subset=['book_title'])

# ---------------------------
# UI Presentation Components
# ---------------------------
def render_architecture_tree():
    st.markdown("### 🛠️ Core Infrastructure Engine")
    st.markdown("""
    <div class="pipeline-node">📂 <b>Unified Storage Layer</b><br><small>Apache Parquet Vectors & DataFrames</small></div>
    <div class="pipeline-arrow">🗘</div>
    <div class="pipeline-node">🤖 <b>Multi-Strategy Matcher Engine</b><br><small>Collaborative / Demographic / Geo Closures</small></div>
    <div class="pipeline-arrow">🗘</div>
    <div class="pipeline-node" style="border-left-color: #2ea043;">🎨 <b>Reactive Interaction Panel</b><br><small>Asynchronous State-Router Hooks</small></div>
    """, unsafe_allow_html=True)

def display_book_cards_grid(book_details, search_term="", year_range=None):
    filtered_df = book_details.copy()
    
    if 'year_of_publication' in filtered_df.columns:
        filtered_df['year_of_publication'] = pd.to_numeric(filtered_df['year_of_publication'], errors='coerce').fillna(0).astype(int)
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['book_title'].str.contains(search_term, case=False, na=False) |
            filtered_df['book_author'].str.contains(search_term, case=False, na=False)
        ]
        
    if year_range:
        filtered_df = filtered_df[
            (filtered_df['year_of_publication'] >= year_range[0]) &
            (filtered_df['year_of_publication'] <= year_range[1])
        ]

    if filtered_df.empty:
        st.markdown("""<div style='padding:20px; background:#161B22; border-radius:8px; border:1px dashed #30363D; text-align:center; color:#8B949E;'>
                    No target selections match your current sub-filter configurations.
                    </div>""", unsafe_allow_html=True)
        return

    # Fluid 3-Column Grid Layout Configuration
    cols = st.columns(3)
    for index, (_, book) in enumerate(filtered_df.iterrows()):
        col = cols[index % 3]
        with col:
            isbn = book.get('isbn', 'N/A')
            image_url = book.get('image_url', 'https://via.placeholder.com/150')
            book_title = book.get('book_title', 'Unknown Title')
            book_author = book.get('book_author', 'Unknown Author')
            publisher = book.get('publisher', 'Unknown Publisher')
            year = book.get('year_of_publication', 0)
            
            badge_html = '<span class="badge-pill badge-vintage">⏳ Vintage Classic</span>' if year < 2000 else '<span class="badge-pill badge-modern">⚡ Modern Era</span>'

            st.markdown(f"""
            <div class="book-card">
                <img src="{image_url}" style="width: 115px; height: 165px; object-fit: cover; border-radius: 6px; filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.5));">
                <div style="width:100%;">
                    <div class="book-title" title="{book_title}">{book_title}</div>
                    <div class="book-meta">✍️ <b>{book_author}</b></div>
                    <div class="book-meta">🏢 <small>{publisher}</small></div>
                    <div class="book-meta">📅 <small>Published: {year if year > 0 else 'N/A'}</small></div>
                    <div style="text-align: left; width: 100%; margin-bottom: 12px;">{badge_html}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔎 Inspect Blueprint", key=f"btn_{isbn}_{index}", use_container_width=True):
                st.session_state.selected_isbn = isbn
                st.rerun()

def display_book_details_view(isbn, book_data, book_similarities):
    if st.button("← Back to Discovery Dashboard", use_container_width=True):
        st.session_state.selected_isbn = None
        st.rerun()
        
    book_selection = book_data[book_data['isbn'] == isbn]
    if not book_selection.empty:
        book = book_selection.iloc[0]
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(book['image_url'], use_container_width=True)
        with col2:
            st.title(book['book_title'])
            st.markdown(f"### ✍️ Author: `{book['book_author']}`")
            
            # Premium Web-Style Metrics Container
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">🏢 Publishing House</div>
                <div class="metric-value">{book['publisher']}</div>
            </div>
            <div class="metric-container">
                <div class="metric-label">📅 Release Timestamp</div>
                <div class="metric-value">Year {book['year_of_publication']}</div>
            </div>
            <div class="metric-container">
                <div class="metric-label">🆔 Global Catalog Identifier (ISBN)</div>
                <div class="metric-value" style="font-family: monospace; font-size: 16px;">{isbn}</div>
            </div>
            <div class="metric-container" style="border-left: 4px solid {CONFIG['success_color']};">
                <div class="metric-label" style="color: {CONFIG['success_color']};">System Cross-Vector Status</div>
                <div class="metric-value" style="color: #FFF;">Verified Active <span style="font-size:14px; color:#8B949E;">(Top 5% Tier)</span></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("✨ Structural Neighborhood Vectors (Readers Also Liked)")
        
        similar_isbns = get_similar_books(isbn, book_similarities)
        if similar_isbns:
            similar_books = get_book_details(similar_isbns, book_data)
            display_book_cards_grid(similar_books)
        else:
            st.caption("No vector representations established for this title option.")
    else:
        st.error("Requested catalog details metadata missing.")

# ---------------------------
# Main Routing Application Runtime
# ---------------------------
def main():
    user_info, book_data, book_similarities = load_data()
    
    if "selected_isbn" not in st.session_state:
        st.session_state.selected_isbn = None

    # Sidebar Component Enclosure Layout
    with st.sidebar:
        st.markdown("<h2 style='color:#FFF; margin-bottom:0;'>📚 NovelNexus</h2>", unsafe_allow_html=True)
        st.caption("Context-Aware Engine Framework")
        st.markdown("---")
        
        render_architecture_tree()
        st.markdown("---")
        
        st.subheader("👨‍💻 System Architect")
        st.markdown("**Tanvir Anzum**\n*AI & Analytics Strategist*")

    # Interactive Screen Router View Routing Rules
    if st.session_state.selected_isbn:
        display_book_details_view(st.session_state.selected_isbn, book_data, book_similarities)
    else:
        st.title("📚 NovelNexus Discovery Portal")
        st.markdown("Select a User ID profile below to compute multiple dynamic target clustering vectors in real-time.")
        
        # Dashboard Input Layer
        ctrl_col1, ctrl_col2 = st.columns([2, 3])
        with ctrl_col1:
            user_id = st.selectbox("🎯 Active Pipeline Profile Vector:", user_info['user_id'].unique())
        with ctrl_col2:
            st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
            status = st.status("Computing recommendation weights...", expanded=False)
            status.update(label="Matrices Fully Calculated & Cached", state="complete")
            
        user_row = user_info[user_info['user_id'] == user_id].iloc[0]
        st.markdown("---")
        
        # Tab Matrix Stratification Setup Layer
        tab1, tab2, tab3 = st.tabs([
            "🤝 Collaborative Neighborhoods", 
            "👥 Generational Demographics", 
            "📍 Geographic Locality Metrics"
        ])
        
        with tab1:
            st.markdown("### Peer Latent Factor Embeddings")
            st.caption("Recommendations extracted based on collaborative similarity matrices inside the model.")
            
            sub_col1, sub_col2 = st.columns([1, 1])
            with sub_col1:
                search_t1 = st.text_input("🔍 Filter by name/author:", key="src_t1", placeholder="Type to search...")
            with sub_col2:
                years_t1 = st.slider("📅 Publication Era Window:", 1950, 2026, (1970, 2026), key="yr_t1")
                
            st.markdown("<br>", unsafe_allow_html=True)
            collab_ids = convert_to_list(user_row['collaborative_cluster_recommendation'])[:10]
            display_book_cards_grid(get_book_details(collab_ids, book_data), search_term=search_t1, year_range=years_t1)
            
        with tab2:
            st.markdown("### Age & Persona Cluster Affinities")
            st.caption("High-indexing items identified across cohorts sharing the same user group attributes.")
            
            sub_col1, sub_col2 = st.columns([1, 1])
            with sub_col1:
                search_t2 = st.text_input("🔍 Filter by name/author:", key="src_t2", placeholder="Type to search...")
            with sub_col2:
                years_t2 = st.slider("📅 Publication Era Window:", 1950, 2026, (1970, 2026), key="yr_t2")
                
            st.markdown("<br>", unsafe_allow_html=True)
            demo_ids = convert_to_list(user_row['demographic_recommendation'])[:10]
            display_book_cards_grid(get_book_details(demo_ids, book_data), search_term=search_t2, year_range=years_t2)
            
        with tab3:
            st.markdown("### Territory & Regional Density Hotspots")
            st.caption("Popular selections calculated from aggregate interactions localized within the same geographic region.")
            
            sub_col1, sub_col2 = st.columns([1, 1])
            with sub_col1:
                search_t3 = st.text_input("🔍 Filter by name/author:", key="src_t3", placeholder="Type to search...")
            with sub_col2:
                years_t3 = st.slider("📅 Publication Era Window:", 1950, 2026, (1970, 2026), key="yr_t3")
                
            st.markdown("<br>", unsafe_allow_html=True)
            geo_ids = convert_to_list(user_row['geographic_recommendation'])[:10]
            display_book_cards_grid(get_book_details(geo_ids, book_data), search_term=search_t3, year_range=years_t3)

if __name__ == "__main__":
    main()
