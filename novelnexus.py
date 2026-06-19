import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import ast

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="NovelNexus | Premium Bookstore", page_icon="📚", layout="wide")

# Initialize Session States
if "selected_isbn" not in st.session_state:
    st.session_state.selected_isbn = None
if "reading_list" not in st.session_state:
    st.session_state.reading_list = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home Discovery"

# ---------------------------
# Global Design Theme & Styles
# ---------------------------
CONFIG = {
    "background_color": "#0F1115",
    "card_bg": "#1A1D24",
    "card_border": "#2D3139",
    "text_color": "#E1E4EA",
    "accent_color": "#4F46E5",  
    "success_color": "#10B981",
    "font_family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
}

st.markdown(f"""
<style>
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {CONFIG['background_color']};
        font-family: {CONFIG['font_family']};
        color: {CONFIG['text_color']};
    }}
    
    /* Premium Book Store Card Design */
    .book-card {{
        background: {CONFIG['card_bg']};
        border: 1px solid {CONFIG['card_border']};
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        height: 380px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }}
    .book-card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 20px 30px -10px rgba(79, 70, 229, 0.3);
        border-color: {CONFIG['accent_color']};
    }}
    .book-title {{
        font-size: 14px;
        font-weight: 700;
        color: #FFFFFF;
        margin: 10px 0 2px 0;
        line-height: 1.3;
        min-height: 38px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-align: left;
    }}
    .book-meta {{
        font-size: 12px;
        color: #9CA3AF;
        margin: 2px 0;
        text-align: left;
        display: flex;
        align-items: center;
        gap: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .star-rating {{
        color: #F59E0B;
        font-size: 11px;
        margin: 4px 0;
        text-align: left;
        width: 100%;
        font-weight: 600;
    }}
    
    /* Clean Modern Badges */
    .badge-pill {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 30px;
        font-size: 9px;
        font-weight: 600;
        letter-spacing: 0.02em;
    }}
    .badge-vintage {{ background: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.25); }}
    .badge-modern {{ background: rgba(59, 130, 246, 0.15); color: #3B82F6; border: 1px solid rgba(59, 130, 246, 0.25); }}
    
    /* Metadata Cards */
    .info-container {{
        background: #1A1D24;
        border: 1px solid #2D3139;
        border-radius: 10px;
        padding: 16px;
        text-align: left;
        margin-bottom: 14px;
    }}
    .info-label {{
        font-size: 11px;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }}
    .info-value {{
        font-size: 18px;
        font-weight: 600;
        color: #FFFFFF;
        margin-top: 4px;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Data Loading Framework
# ---------------------------
@st.cache_data
def load_data():
    try:
        user_combined_recommendations = pd.read_csv("data/recommender_result/user_combined_recommendations.csv")
        book_data = pd.read_parquet("data/preprocessed_files/distinct_books.parquet")
        book_similarities = pd.read_csv("data/recommender_result/book_similarities.csv")
    except Exception:
        user_combined_recommendations = pd.DataFrame({
            'user_id': [1001, 1002, 1003],
            'geographic_recommendation': ["['0345339681', '0449212602']", "[]", "[]"],
            'demographic_recommendation': ["['0449212602', '0345339681']", "['0449212602']", "[]"],
            'collaborative_cluster_recommendation': ["['0345339681', '0449212602']", "[]", "[]"]
        })
        book_data = pd.DataFrame({
            'isbn': ['0345339681', '0449212602'], 
            'book_title': ['The Hobbit', 'The Handmaid\'s Tale'], 
            'book_author': ['J.R.R. Tolkien', 'Margaret Atwood'],
            'publisher': ['Ballantine Books', 'Fawcett Books'], 
            'year_of_publication': [1986, 1998], 
            'image_url': ['https://images.amazon.com/images/P/0345339681.01.MZZZZZZZ.jpg', 'https://images.amazon.com/images/P/0449212602.01.MZZZZZZZ.jpg']
        })
        book_similarities = pd.DataFrame({'isbn': ['0345339681', '0449212602'], 'similar_books': ['0449212602', '0345339681']})
        
    return user_combined_recommendations, book_data, book_similarities

user_info, book_data, book_similarities = load_data()

# ---------------------------
# Core Helpers
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
# UI Grid Component
# ---------------------------
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
        st.markdown("<div style='padding:30px; background:#1A1D24; border-radius:10px; border:1px dashed #2D3139; text-align:center; color:#9CA3AF;'>No matching volumes found in this library shelf.</div>", unsafe_allow_html=True)
        return

    cols = st.columns(5)
    for index, (_, book) in enumerate(filtered_df.iterrows()):
        col = cols[index % 5]
        with col:
            isbn = book.get('isbn', 'N/A')
            image_url = book.get('image_url', 'https://via.placeholder.com/150')
            book_title = book.get('book_title', 'Untitled')
            book_author = book.get('book_author', 'Unknown Author')
            publisher = book.get('publisher', 'Unknown Publisher')
            year = book.get('year_of_publication', 0)
            
            badge_html = '<span class="badge-pill badge-vintage">⏳ Vintage</span>' if year < 2000 else '<span class="badge-pill badge-modern">✨ Modern</span>'

            st.markdown(f"""
            <div class="book-card">
                <img src="{image_url}" style="width: 105px; height: 145px; object-fit: cover; border-radius: 6px; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.4));">
                <div style="width:100%;">
                    <div class="book-title" title="{book_title}">{book_title}</div>
                    <div class="book-meta" title="{book_author}">✍️ <b>{book_author}</b></div>
                    <div class="star-rating">⭐ 4.6 <span style="color:#6B7280; font-size:10px; font-weight:normal;">(410)</span></div>
                    <div class="book-meta" title="{publisher}">🏢 <small>{publisher}</small></div>
                    <div class="book-meta">📅 <small>Year: {year if year > 0 else 'N/A'}</small></div>
                    <div style="text-align: left; width: 100%; margin-top: 6px;">{badge_html}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Interactive Action Row
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("📖 Details", key=f"det_{isbn}_{index}", use_container_width=True):
                    st.session_state.selected_isbn = isbn
                    st.rerun()
            with btn_col2:
                if st.button("🔖 Save", key=f"save_{isbn}_{index}", use_container_width=True):
                    if isbn not in st.session_state.reading_list:
                        st.session_state.reading_list.append(isbn)
                        st.toast(f"Saved to reading list!", icon="✅")
                    else:
                        st.toast("Already in your list!", icon="ℹ️")

# ---------------------------
# Individual Views
# ---------------------------
def display_book_details_view(isbn, book_data, book_similarities):
    if st.button("← Back to Marketplace Home", use_container_width=True):
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
            st.markdown(f"### By **{book['book_author']}**")
            
            st.markdown(f"""
            <div class="info-container">
                <div class="info-label">Publisher</div>
                <div class="info-value">{book['publisher']}</div>
            </div>
            <div class="info-container">
                <div class="info-label">Publication Year</div>
                <div class="info-value">{book['year_of_publication']}</div>
            </div>
            <div class="info-container" style="border-left: 4px solid {CONFIG['success_color']};">
                <div class="info-label" style="color: {CONFIG['success_color']};">Availability</div>
                <div class="info-value" style="color: #FFF;">In Stock <span style="font-size:13px; color:#9CA3AF;">(Dispatches within 24 hours)</span></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("✨ Readers Who Bought This Also Enjoyed")
        similar_isbns = get_similar_books(isbn, book_similarities)
        if similar_isbns:
            display_book_cards_grid(get_book_details(similar_isbns, book_data))
        else:
            st.caption("No recommendations available for this specific title yet.")

# ---------------------------
# Sidebar Frame
# ---------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#FFF; margin-bottom:0;'>📚 NovelNexus</h2>", unsafe_allow_html=True)
    st.caption("Your Premium AI Bookstore")
    st.markdown("---")
    
    # Fully functional Navigation Router
    st.session_state.current_page = st.radio(
        "Navigation Portal",
        ["🏠 Home Discovery", "🔖 My Reading Lists", "🔥 Global Best Sellers"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    
    st.subheader("👤 Premium Client Profile")
    st.markdown("**Tanvir Anzum**\n*Chief Curator*")
    st.caption(f"Items Saved: {len(st.session_state.reading_list)}")

# ---------------------------
# Main Router Runtime Engine
# ---------------------------
if st.session_state.selected_isbn:
    display_book_details_view(st.session_state.selected_isbn, book_data, book_similarities)
else:
    if st.session_state.current_page == "🏠 Home Discovery":
        # Global Search Engine Header Layout
        st.title("📚 Discovery Marketplace")
        
        h_col1, h_col2 = st.columns([3, 1])
        with h_col1:
            global_search = st.text_input("🔍 Search catalog by title, author name or keywords...", placeholder="Type here to instantly query catalog ecosystem...")
        with h_col2:
            user_id = st.selectbox("🎯 Active Shopping Profile:", user_info['user_id'].unique())
            
        user_row = user_info[user_info['user_id'] == user_id].iloc[0]
        st.markdown("---")
        
        # Segmented Recommender Engine System Tabs
        tab1, tab2, tab3 = st.tabs([
            "🤝 Curated Flavor Profile", 
            "👥 Popular Among Your Peers", 
            "📍 Trending In Your Region"
        ])
        
        with tab1:
            st.markdown("### Handpicked For You")
            st.caption("Algorithmic matrix matches tailored explicitly to your historical engagement data.")
            years_t1 = st.slider("Era Range Limit:", 1950, 2026, (1970, 2026), key="yr_t1")
            collab_ids = convert_to_list(user_row['collaborative_cluster_recommendation'])[:10]
            display_book_cards_grid(get_book_details(collab_ids, book_data), search_term=global_search, year_range=years_t1)
            
        with tab2:
            st.markdown("### Peer Demographic Trends")
            st.caption("High volume sales matches intersecting cleanly within your baseline social circle framework.")
            years_t2 = st.slider("Era Range Limit:", 1950, 2026, (1970, 2026), key="yr_t2")
            demo_ids = convert_to_list(user_row['demographic_recommendation'])[:10]
            display_book_cards_grid(get_book_details(demo_ids, book_data), search_term=global_search, year_range=years_t2)
            
        with tab3:
            st.markdown("### Regional Best Sellers")
            st.caption("Geographically dense transaction spikes surrounding your delivery zones.")
            years_t3 = st.slider("Era Range Limit:", 1950, 2026, (1970, 2026), key="yr_t3")
            geo_ids = convert_to_list(user_row['geographic_recommendation'])[:10]
            display_book_cards_grid(get_book_details(geo_ids, book_data), search_term=global_search, year_range=years_t3)

    elif st.session_state.current_page == "🔖 My Reading Lists":
        st.title("🔖 Your Saved Reading Vault")
        st.markdown("Keep track of your favored choices before checkout processing.")
        
        if st.session_state.reading_list:
            if st.button("🗑️ Clear Entire List"):
                st.session_state.reading_list = []
                st.rerun()
            saved_books = get_book_details(st.session_state.reading_list, book_data)
            display_book_cards_grid(saved_books)
        else:
            st.info("Your list is currently empty. Explore the catalog home screen to build out your curated shelf profile.")

    elif st.session_state.current_page == "🔥 Global Best Sellers":
        st.title("🔥 Global Best Sellers")
        st.markdown("The highest volume titles globally across all platform registers.")
        # Default fallback view showcasing all distinct indexed library books
        display_book_cards_grid(book_data[:10])
