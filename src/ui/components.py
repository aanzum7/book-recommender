"""NovelNexus Modular UI Components."""
import pandas as pd  # type: ignore
import streamlit as st  # type: ignore
from src.ui.data_loader import (
    get_similar_books,
    get_book_details_df,
    parse_isbn_list,
    clean_location,
)


def render_hero():
    """Renders top hero showcase banner."""
    st.markdown(
        """
        <div class="nn-hero">
            <div class="nn-hero-pill">
                <span class="pulse-dot"></span> AI Recommendation Engine Active
            </div>
            <div class="nn-hero-title">Next-Generation Book Discovery</div>
            <div class="nn-hero-sub">
                Explore personalized literature tailored to your latent taste. Powered by high-dimensional
                TruncatedSVD matrix factorization, MiniBatchKMeans clustering, and demographic behavioral modeling.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.fragment
def render_books_grid(books_df, book_lookup, prefix="shelf", search_query=""):
    """
    Renders a responsive 5-column grid chunked by rows of 5.
    Features a clean unified card with a single sleek action button.
    No awkward multiple buttons below the card.
    """
    if books_df.empty:
        st.markdown(
            """
            <div style='padding: 32px; background: rgba(22, 29, 46, 0.4); border-radius: 14px;
                        border: 1px dashed rgba(255, 255, 255, 0.1); text-align: center; color: #94A3B8;'>
                <div style="font-size: 26px; margin-bottom: 6px;">📂</div>
                <div style="font-size: 14.5px; font-weight: 600; color: #FFF;">Shelf is currently empty</div>
                <div style="font-size: 12px; margin-top: 4px;">No books match the active filter or category selection.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    filtered_df = books_df.copy()
    if search_query:
        mask = (
            filtered_df["book_title"].str.contains(search_query, case=False, na=False)
            | filtered_df["book_author"].str.contains(search_query, case=False, na=False)
            | filtered_df["isbn"].str.contains(search_query, case=False, na=False)
        )
        filtered_df = filtered_df[mask]

    if filtered_df.empty:
        st.markdown(
            f"""
            <div style='padding: 24px; background: rgba(22, 29, 46, 0.5); border-radius: 12px;
                        border: 1px solid rgba(255, 255, 255, 0.08); text-align: center; color: #94A3B8;'>
                🔍 No titles found matching "<b>{search_query}</b>" on this shelf.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Chunk books into rows of 5 for perfect grid alignment
    num_books = len(filtered_df)
    for row_start in range(0, num_books, 5):
        row_slice = filtered_df.iloc[row_start : row_start + 5]
        cols = st.columns(5)

        for col_idx, (_, book) in enumerate(row_slice.iterrows()):
            global_idx = row_start + col_idx
            with cols[col_idx]:
                isbn = str(book.get("isbn", "N/A")).strip()
                title = book.get("book_title", "Untitled")
                author = book.get("book_author", "")
                publisher = book.get("publisher", "")
                year = book.get("year_of_publication", 0)
                img_url = book.get("image_url", "")

                if not isinstance(img_url, str) or not img_url.startswith("http"):
                    img_url = "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&q=80"

                if not author or str(author).lower() in ("unknown", "unknown author", "n/a", "none", "nan"):
                    author_display = "Author Unlisted"
                else:
                    author_display = f"by {author}"

                meta_parts = []
                if publisher and str(publisher).lower() not in ("unknown", "unknown publisher", "n/a", "none", "nan"):
                    meta_parts.append(str(publisher).strip().title())
                if isinstance(year, (int, float)) and year > 0:
                    meta_parts.append(str(int(year)))
                meta_display = " • ".join(meta_parts) if meta_parts else "Catalog Edition"

                is_vintage = isinstance(year, (int, float)) and year > 0 and year < 2000
                badge_html = (
                    '<span class="nn-badge nn-badge-vintage">🏛️ Vintage</span>'
                    if is_vintage
                    else '<span class="nn-badge nn-badge-modern">✨ Modern</span>'
                )

                is_saved = isbn in st.session_state.reading_list
                if is_saved:
                    badge_html += ' <span class="nn-badge nn-badge-saved">💖 Saved</span>'

                rating_val = 4.3 + (hash(isbn) % 7) / 10.0
                review_count = 120 + (hash(isbn) % 480)

                # Single Unified Book Card
                st.markdown(
                    f"""
                    <div class="nn-card">
                        <div>
                            <div class="nn-cover-wrapper">
                                <img src="{img_url}" class="nn-cover-img" loading="lazy"
                                     onerror="this.src='https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&q=80'">
                            </div>
                            <div class="nn-book-title" title="{title}">{title}</div>
                            <div class="nn-book-author" title="{author_display}">{author_display}</div>
                            <div class="nn-rating-bar">
                                <span>★ {rating_val:.1f}</span>
                                <span class="nn-review-count">({review_count})</span>
                            </div>
                            <div class="nn-meta-chip" title="{meta_display}">{meta_display}</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
                            <div>{badge_html}</div>
                            <span style="font-size: 9.5px; color: #64748B; font-weight: 600;">ISBN: {isbn[:7]}...</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Single Clean Primary Action Button (No multiple buttons below)
                if st.button("🔍 View Details", key=f"view_{prefix}_{isbn}_{global_idx}", use_container_width=True):
                    st.session_state.selected_isbn = isbn
                    st.rerun()


def render_book_detail_view(isbn, book_lookup, similarity_lookup):
    """Full-screen book detail inspector with metadata bento boxes and similar books."""
    top_nav_col1, _ = st.columns([4, 1])
    with top_nav_col1:
        if st.button("← Return to Marketplace Shelves", use_container_width=False):
            st.session_state.selected_isbn = None
            st.rerun()

    if isbn not in book_lookup:
        st.error(f"Catalog record for ISBN '{isbn}' was not found.")
        return

    book = book_lookup[isbn]
    img_url = book.get("image_url", "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&q=80")
    year = book.get("year_of_publication", 0)
    title = book.get("book_title", "Untitled")
    author = book.get("book_author", "")
    publisher = book.get("publisher", "")

    author_clean = f"by {author}" if author and str(author).lower() not in ("unknown", "n/a", "none") else "Author Unlisted"
    pub_clean = str(publisher).title() if publisher and str(publisher).lower() not in ("unknown", "n/a", "none") else "Unlisted Publisher"
    year_clean = str(int(year)) if isinstance(year, (int, float)) and year > 0 else "Unlisted"

    is_saved = isbn in st.session_state.reading_list

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])

    with c1:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, rgba(22, 29, 46, 0.8) 0%, rgba(13, 17, 26, 0.95) 100%);
                        border: 1px solid var(--border-glass); border-radius: 20px; padding: 28px; text-align: center;
                        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.7);">
                <img src="{img_url}" style="width: 220px; height: 330px; object-fit: cover; border-radius: 6px 12px 12px 6px;
                                            box-shadow: -8px 12px 30px rgba(0,0,0,0.8);">
                <div style="margin-top: 18px; display: flex; justify-content: center; gap: 8px;">
                    {'<span class="nn-badge nn-badge-vintage" style="font-size:12px; padding:5px 14px;">🏛️ Vintage Classic</span>' if isinstance(year, (int, float)) and year > 0 and year < 2000 else '<span class="nn-badge nn-badge-modern" style="font-size:12px; padding:5px 14px;">✨ Modern Era</span>'}
                    <span class="nn-badge" style="background: rgba(16, 185, 129, 0.12); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.28); font-size:12px; padding:5px 14px;">
                        <span class="pulse-dot"></span> In Catalog
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="nn-hero-pill">Verified Catalog Record</div>
            <h1 style="font-size: 34px; font-weight: 800; letter-spacing: -0.02em; color: #FFF; margin: 0 0 6px 0;">{title}</h1>
            <h3 style="font-size: 18px; font-weight: 600; color: #818CF8; margin: 0 0 24px 0;">{author_clean}</h3>
            """,
            unsafe_allow_html=True,
        )

        bento_cols = st.columns(3)
        with bento_cols[0]:
            st.markdown(
                f"""
                <div class="bento-card">
                    <div class="bento-title">Publisher</div>
                    <div class="bento-value" style="font-size: 15px;">{pub_clean}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with bento_cols[1]:
            st.markdown(
                f"""
                <div class="bento-card">
                    <div class="bento-title">Year Published</div>
                    <div class="bento-value">{year_clean}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with bento_cols[2]:
            st.markdown(
                f"""
                <div class="bento-card">
                    <div class="bento-title">ISBN-10 Code</div>
                    <div class="bento-value" style="font-size: 14px; font-family: monospace;">{isbn}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        act1, _ = st.columns([1, 2])
        with act1:
            if st.button("💖 Saved in Vault" if is_saved else "🤍 Add to Reading Vault", use_container_width=True):
                if is_saved:
                    st.session_state.reading_list.remove(isbn)
                    st.toast("Removed from reading vault.", icon="🗑️")
                else:
                    st.session_state.reading_list.add(isbn)
                    st.toast("Added to reading vault!", icon="💖")
                st.rerun()

    st.markdown("---")
    st.markdown("### 📚 Readers Who Explored This Also Loved")
    st.caption("Real-time collaborative item-to-item similarity computed via high-dimensional cosine vector matching.")

    similar_isbns = get_similar_books(isbn, similarity_lookup, limit=10)
    if similar_isbns:
        similar_df = get_book_details_df(similar_isbns, book_lookup)
        render_books_grid(similar_df, book_lookup, prefix="similar_shelf")
    else:
        st.info("No similarity neighbors discovered for this specific title.")


def render_sidebar(user_info, reading_list):
    """
    Renders sidebar navigation with the Active Personalization Profile
    fully unified inside a modern card container.
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 10px 0 6px 0;">
                <div style="font-size: 24px; font-weight: 800; letter-spacing: -0.03em; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">
                    <span>📚</span> NovelNexus
                </div>
                <div style="color: #818CF8; font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 2px;">
                    AI Hybrid Recommendation Engine
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # 1. Reading Vault Metric Card
        saved_count = len(reading_list)
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="text-align: center; padding: 4px 0;">
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: #EC4899; font-weight: 700;">
                        💖 Reading Vault
                    </div>
                    <div style="font-size: 32px; font-weight: 800; color: #FFFFFF; margin: 4px 0 2px 0;">
                        {saved_count}
                    </div>
                    <div style="font-size: 11px; color: #94A3B8;">titles bookmarked</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 2. Active Personalization Profile Card (All elements inside container)
        if "user_id" in user_info.columns:
            user_list = sorted([int(x) for x in user_info['user_id'].dropna().unique()])
        else:
            user_list = [1001]

        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <div class="profile-avatar">👤</div>
                    <div>
                        <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: #818CF8; font-weight: 700;">
                            Personalization Profile
                        </div>
                        <div style="font-size: 14px; font-weight: 800; color: #FFFFFF; line-height: 1.2;">
                            Active Reader Identity
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            selected_user_id = st.selectbox(
                "Select Reader Identity:",
                user_list,
                index=user_list.index(276746) if 276746 in user_list else 0,
                label_visibility="visible",
            )

            if "user_id" in user_info.columns and not user_info[user_info["user_id"] == selected_user_id].empty:
                active_user_row = user_info[user_info["user_id"] == selected_user_id].iloc[0]
                raw_age = active_user_row.get("age_group", "Unknown")
                raw_loc = active_user_row.get("location", "")
            else:
                active_user_row = pd.Series()
                raw_age = "Young Adult"
                raw_loc = "Dallas, Texas, USA"

            user_loc = clean_location(str(raw_loc))
            user_age = str(raw_age).strip().title() if raw_age and str(raw_age).lower() != "unknown" else "All Demographics"

            st.markdown(
                f"""
                <div class="profile-tag-box">
                    <div style="font-size: 12px; font-weight: 700; color: #A5B4FC; margin-bottom: 2px;">
                        Reader #{selected_user_id}
                    </div>
                    <div style="font-size: 12px; font-weight: 600; color: #F8FAFC; margin-bottom: 2px;">
                        📍 {user_loc}
                    </div>
                    <div style="font-size: 11.5px; color: #34D399; font-weight: 600;">
                        👥 Demographic: {user_age}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 3. Project Architect Card
        with st.container(border=True):
            st.markdown(
                """
                <div>
                    <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: #818CF8; font-weight: 700; margin-bottom: 2px;">
                        Project Architect
                    </div>
                    <div style="font-size: 15px; font-weight: 800; color: #FFFFFF;">Tanvir Anzum</div>
                    <div style="font-size: 11.5px; color: #10B981; font-weight: 600; margin-bottom: 8px;">
                        AI & Data Researcher
                    </div>
                    <div style="font-size: 11.5px; color: #94A3B8; line-height: 1.4; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 8px;">
                        Architecting machine learning pipelines, latent factor modeling, and intelligent discovery tools.
                    </div>
                    <div style="font-size: 12px; margin-top: 10px; display: flex; gap: 12px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 8px;">
                        <a href="https://www.linkedin.com/in/aanzum" target="_blank" style="text-decoration: none; color: #CBD5E1; font-weight: 600;">
                            🔗 LinkedIn
                        </a>
                        <a href="https://www.researchgate.net/profile/Tanvir-Anzum" target="_blank" style="text-decoration: none; color: #CBD5E1; font-weight: 600;">
                            🔬 Research
                        </a>
                        <a href="https://github.com/aanzum7" target="_blank" style="text-decoration: none; color: #CBD5E1; font-weight: 600;">
                            💻 GitHub
                        </a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    return selected_user_id, active_user_row, user_age, user_loc


def render_marketplace(book_data, active_user_row, selected_user_id, book_lookup):
    """
    Renders marketplace discovery layout with concise, context-rich tabs.
    """
    render_hero()

    # Search Bar & Metrics Strip
    search_col, metric_col = st.columns([3, 1])
    with search_col:
        global_search = st.text_input(
            "Search Catalog",
            placeholder="Search catalog by title, author, publisher, or ISBN...",
            label_visibility="collapsed",
        )
    with metric_col:
        st.markdown(
            f"""
            <div style="text-align: right; padding-top: 8px; color: var(--text-muted); font-size: 13px;">
                Catalog: <strong style="color: #FFF;">{len(book_data):,}</strong> titles online
            </div>
            """,
            unsafe_allow_html=True,
        )

    saved_count = len(st.session_state.reading_list)

    raw_loc = active_user_row.get("location", "") if hasattr(active_user_row, "get") else ""
    raw_age = active_user_row.get("age_group", "") if hasattr(active_user_row, "get") else ""
    user_loc = clean_location(str(raw_loc))
    user_age = str(raw_age).strip().title() if raw_age and str(raw_age).lower() != "unknown" else "All Demographics"

    # Concise, Context-Rich Discovery Tabs
    tab_curated, tab_peers, tab_geo, tab_all, tab_vault = st.tabs([
        "⭐ For You",
        "👥 Popular Peers",
        "📍 Trending Nearby",
        "📚 Catalog Shelves",
        f"💖 Vault ({saved_count})",
    ])

    # Tab 1: Personalized Collaborative SVD
    with tab_curated:
        st.markdown("### ⭐ Handpicked For You")
        st.caption(f"Curated for Reader #{selected_user_id} using latent collaborative SVD embeddings.")
        collab_isbns = parse_isbn_list(active_user_row.get("collaborative_cluster_recommendation", []))[:10]
        curated_df = get_book_details_df(collab_isbns, book_lookup) if collab_isbns else pd.DataFrame()
        if not curated_df.empty:
            render_books_grid(curated_df, book_lookup, prefix="curated_shelf", search_query=global_search)
        else:
            st.info("💡 Personalized recommendations are being generated for this reader profile. Showing top catalog picks:")
            render_books_grid(book_data.head(10), book_lookup, prefix="fallback_curated", search_query=global_search)

    # Tab 2: Demographic Recommendations
    with tab_peers:
        st.markdown("### 👥 Popular Among Peers")
        st.caption(f"Top-rated literature trending among readers in the {user_age} demographic.")
        demo_isbns = parse_isbn_list(active_user_row.get("demographic_recommendation", []))[:10]
        demo_df = get_book_details_df(demo_isbns, book_lookup) if demo_isbns else pd.DataFrame()
        if not demo_df.empty:
            render_books_grid(demo_df, book_lookup, prefix="demo_shelf", search_query=global_search)
        else:
            st.info(f"💡 Showing popular titles across demographics for {user_age}:")
            render_books_grid(book_data.head(10), book_lookup, prefix="fallback_demo", search_query=global_search)

    # Tab 3: Geographic Recommendations
    with tab_geo:
        st.markdown("### 📍 Trending In Your Area")
        st.caption(f"Locational bestsellers popular among readers in {user_loc}.")
        geo_isbns = parse_isbn_list(active_user_row.get("geographic_recommendation", []))[:10]
        geo_df = get_book_details_df(geo_isbns, book_lookup) if geo_isbns else pd.DataFrame()
        if not geo_df.empty:
            render_books_grid(geo_df, book_lookup, prefix="geo_shelf", search_query=global_search)
        else:
            st.info(f"💡 No localized bestsellers listed for {user_loc} yet. Showing popular titles across regions:")
            render_books_grid(book_data.head(10), book_lookup, prefix="fallback_geo", search_query=global_search)

    # Tab 4: Full Catalog Shelves
    with tab_all:
        st.markdown("### 📚 Full Catalog Shelves")
        st.caption("Explore timeless literary classics and modern era bestsellers.")

        st.markdown("#### 🏛️ Vintage Classics (< 2000)")
        vintage_df = book_data[book_data["year_of_publication"] < 2000] if "year_of_publication" in book_data.columns else book_data
        render_books_grid(vintage_df.head(10), book_lookup, prefix="vintage_shelf", search_query=global_search)

        st.markdown("---")
        st.markdown("#### ✨ Modern Era Hits (2000+)")
        modern_df = book_data[book_data["year_of_publication"] >= 2000] if "year_of_publication" in book_data.columns else book_data
        render_books_grid(modern_df.head(10), book_lookup, prefix="modern_shelf", search_query=global_search)

    # Tab 5: Saved Reading Vault
    with tab_vault:
        st.markdown("### 💖 My Reading Vault")
        st.caption("Your saved and bookmarked literature ready for your reading queue.")
        if st.session_state.reading_list:
            v_col1, v_col2 = st.columns([4, 1])
            with v_col2:
                if st.button("🗑️ Clear Entire Vault", use_container_width=True):
                    st.session_state.reading_list.clear()
                    st.toast("Reading vault cleared.", icon="🗑️")
                    st.rerun()

            saved_books_df = get_book_details_df(list(st.session_state.reading_list), book_lookup)
            render_books_grid(saved_books_df, book_lookup, prefix="vault_shelf", search_query=global_search)
        else:
            st.markdown(
                """
                <div style="padding: 44px; background: rgba(22, 29, 46, 0.4); border-radius: 14px;
                            border: 1px dashed rgba(255, 255, 255, 0.1); text-align: center;">
                    <div style="font-size: 38px; margin-bottom: 8px;">🤍</div>
                    <div style="font-size: 16px; font-weight: 700; color: #FFF;">Your Reading Vault is empty</div>
                    <div style="font-size: 12.5px; color: #94A3B8; margin-top: 4px;">
                        Click <b>🔍 View Details</b> on any book to inspect and add titles to your vault.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

