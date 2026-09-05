"""
NovelNexus | AI Book Discovery Marketplace Runner.
Streamlined entry point managing state, data initialization, and view routing.
"""
import streamlit as st  # type: ignore
from src.ui.styles import inject_custom_css
from src.ui.data_loader import load_marketplace_data, build_fast_lookups
from src.ui.components import (
    render_sidebar,
    render_book_detail_view,
    render_marketplace,
)


def init_app():
    """Initializes Streamlit page configuration and session state."""
    st.set_page_config(
        page_title="NovelNexus | AI Book Discovery",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    if "selected_isbn" not in st.session_state:
        st.session_state.selected_isbn = None

    if "reading_list" not in st.session_state or not isinstance(st.session_state.reading_list, set):
        if "reading_list" in st.session_state and isinstance(st.session_state.reading_list, list):
            st.session_state.reading_list = set(st.session_state.reading_list)
        else:
            st.session_state.reading_list = set()


def main():
    """Main application lifecycle controller."""
    init_app()
    inject_custom_css()

    # Load pre-trained models and catalog hash maps
    user_info, book_data, book_similarities = load_marketplace_data()
    book_lookup, similarity_lookup = build_fast_lookups(book_data, book_similarities)

    # Render sidebar controls & profile switcher
    selected_user_id, active_user_row, _, _ = render_sidebar(
        user_info, st.session_state.reading_list
    )

    # View Routing: Detail Inspector or Marketplace Shelves
    if st.session_state.selected_isbn:
        render_book_detail_view(st.session_state.selected_isbn, book_lookup, similarity_lookup)
    else:
        render_marketplace(book_data, active_user_row, selected_user_id, book_lookup)


if __name__ == "__main__":
    main()
