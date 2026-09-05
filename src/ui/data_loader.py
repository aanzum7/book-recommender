"""
NovelNexus UI Data Layer.
High-efficiency cached loaders, hash maps, and helper functions.
"""
import ast
import os
import pandas as pd  # type: ignore
import streamlit as st  # type: ignore


@st.cache_data(ttl=3600, show_spinner=False)
def load_marketplace_data():
    """Loads pre-trained model recommendations and distinct catalog datasets."""
    try:
        user_combined = pd.read_csv("data/recommender_result/user_combined_recommendations.csv")
        books_df = pd.read_parquet("data/preprocessed_files/distinct_books.parquet")
        similarities_df = pd.read_csv("data/recommender_result/book_similarities.csv")
    except Exception:
        user_combined = pd.DataFrame({
            "user_id": [1001, 1002, 1003],
            "geographic_recommendation": ["['0345339681', '0449212602']", "[]", "[]"],
            "demographic_recommendation": ["['0449212602', '0345339681']", "['0449212602']", "[]"],
            "collaborative_cluster_recommendation": ["['0345339681', '0449212602']", "[]", "[]"],
            "location": ["Dallas, Texas, USA", "New York, USA", "London, UK"],
            "age_group": ["Young Adult", "Middle-aged", "Young Adult"],
        })
        books_df = pd.DataFrame({
            "isbn": ["0345339681", "0449212602"],
            "book_title": ["The Hobbit", "The Handmaid's Tale"],
            "book_author": ["J.R.R. Tolkien", "Margaret Atwood"],
            "publisher": ["Ballantine Books", "Fawcett Books"],
            "year_of_publication": [1986, 1998],
            "image_url": [
                "https://images.amazon.com/images/P/0345339681.01.MZZZZZZZ.jpg",
                "https://images.amazon.com/images/P/0449212602.01.MZZZZZZZ.jpg",
            ],
        })
        similarities_df = pd.DataFrame({
            "isbn": ["0345339681", "0449212602"],
            "similar_books": ["0449212602", "0345339681"],
        })

    if "year_of_publication" in books_df.columns:
        books_df["year_of_publication"] = (
            pd.to_numeric(books_df["year_of_publication"], errors="coerce").fillna(0).astype(int)
        )

    for col in ["book_title", "book_author", "publisher"]:
        if col in books_df.columns:
            books_df[col] = books_df[col].fillna("Unknown").astype(str)

    return user_combined, books_df, similarities_df


@st.cache_resource(show_spinner=False)
def build_fast_lookups(_books_df, _similarities_df):
    """Generates O(1) hash maps for rapid title metadata and similarity retrieval."""
    book_dict = _books_df.set_index("isbn").to_dict(orient="index")
    similarity_dict = _similarities_df.set_index("isbn")["similar_books"].to_dict()
    return book_dict, similarity_dict


def clean_location(loc_str: str) -> str:
    """
    Cleans and formats raw user location strings.
    Trims empty segments, removes redundant commas, strips quotes/slashes,
    and capitalizes valid place names.
    Examples:
      'fort worth, ,' -> 'Fort Worth'
      'london, , united kingdom' -> 'London, United Kingdom'
      ', , usa' -> 'USA'
      ', ,' -> 'Unknown Location'
    """
    if not isinstance(loc_str, str) or not loc_str.strip():
        return "Unknown Location"

    raw = loc_str.replace('"', '').replace("'", "").replace('\\', '').strip()
    parts = []
    for piece in raw.split(','):
        cleaned = piece.strip()
        if cleaned and cleaned.lower() not in ('', 'n/a', 'null', 'none', 'unknown', '-'):
            if cleaned.lower() in ('usa', 'uk', 'uae'):
                parts.append(cleaned.upper())
            else:
                parts.append(cleaned.title())

    if not parts:
        return "Unknown Location"

    return ", ".join(parts)


def parse_isbn_list(value):
    """Safely extracts ISBN string arrays into Python lists."""
    if isinstance(value, list):
        return value
    if not isinstance(value, str):
        return []
    val = value.strip()
    if not val or val == "[]":
        return []
    try:
        return ast.literal_eval(val)
    except Exception:
        try:
            return ast.literal_eval(val.replace("'", '"'))
        except Exception:
            return [x.strip().strip("'").strip('"') for x in val.strip("[]").split(",") if x.strip()]


def get_similar_books(isbn, similarity_lookup, limit=10):
    """Retrieves top similar books using cosine similarity lookup."""
    raw = similarity_lookup.get(str(isbn), "")
    if isinstance(raw, str) and raw:
        return [x.strip() for x in raw.split(",") if x.strip()][:limit]
    elif isinstance(raw, list):
        return raw[:limit]
    return []


def get_book_details_df(isbns, book_lookup):
    """Fetches full metadata records for a given list of ISBNs."""
    records = []
    seen = set()
    for item in isbns:
        str_isbn = str(item).strip()
        if str_isbn and str_isbn not in seen and str_isbn in book_lookup:
            seen.add(str_isbn)
            rec = book_lookup[str_isbn].copy()
            rec["isbn"] = str_isbn
            records.append(rec)
    return pd.DataFrame(records)

