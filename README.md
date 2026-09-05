# NovelNexus - AI Book Recommendation System

An end-to-end Machine Learning book recommendation engine and interactive marketplace built with Python, Scikit-learn, and Streamlit.

Live Demo: [NovelNexus on Streamlit](https://recommend-novelnexus.streamlit.app/)

---

## Architecture Overview

NovelNexus employs a **4-tier hybrid recommendation engine**:

1. **Personalized Collaborative Filtering**:
   - High-dimensional user-item interaction matrix decomposed via **TruncatedSVD** (100 components).
   - User behavioral grouping using **MiniBatchKMeans** (30 clusters) to overcome cold-start sparsity.
2. **Item-to-Item Similarity ("People Also Read")**:
   - Cosine similarity across cluster co-occurrences to recommend similar titles when inspecting any book.
3. **Demographic Recommender**:
   - Age-bracket segmentation (*Teenager*, *Young Adult*, *Middle-aged*, *Senior*) weighted by rating score and review volume.
4. **Geographic Recommender**:
   - Regional trending books based on user location clusters.

---

## Project Structure

```text
book-recommender/
├── config/
│   ├── pipeline_config.py       # Centralized hyperparameters, weights, and file paths
│   └── logging_configs.py       # Application and pipeline logging configuration
├── data/
│   ├── raw_files/               # Books.csv, Ratings.csv, Users.csv
│   ├── preprocessed_files/      # Parquet files (raw_data, distinct_books, users)
│   └── recommender_result/      # Computed clusters, similarity matrices, recommendations
├── src/
│   ├── data_inject/             # Remote data ingestion (Google Drive with local fallback)
│   ├── data_preprocessing/      # Vectorized cleaning, user & book catalog extraction
│   └── recommender/
│       ├── collaborative_filtering_recommender/  # SVD, KMeans, and Cosine similarity
│       ├── demographic_recommender/              # Age-bracket weighted scoring
│       ├── geographic_recommender/               # Regional trending recommender
│       └── user_combined_recommendation/         # Multi-model aggregator
├── main.py                      # Modular pipeline CLI orchestrator
├── novelnexus.py                # Production Streamlit UI application
├── Procfile                     # Cloud deployment instruction
└── requirements.txt             # Python production dependencies
```

---

## Quickstart & Installation

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/aanzum7/book-recommender.git
cd book-recommender

# Using Conda
conda create --name book-recommender python=3.11 -y
conda activate book-recommender
pip install -r requirements.txt
```

### 2. Running the Data & ML Pipeline

The pipeline is fully modularized with step timing and targeted stage execution via [`main.py`](main.py):

```bash
# Run complete end-to-end pipeline (Ingestion -> Preprocessing -> Training -> Aggregation)
python main.py

# Or execute specific pipeline stages:
python main.py --stage ingest       # Fetch raw data (Google Drive or local fallback)
python main.py --stage preprocess   # Vectorized cleaning & Parquet extraction
python main.py --stage recommend    # Compute Demographic, Geo, SVD, & Item Similarities
python main.py --stage aggregate    # Aggregate multi-model outputs for all users
```

### 3. Launching the Web Application

Launch the dark-themed discovery marketplace:

```bash
streamlit run novelnexus.py
```

---

## Deployment

The application is configured for deployment on Heroku, Render, and Streamlit Community Cloud using [`Procfile`](Procfile):

```text
web: streamlit run novelnexus.py --server.port=$PORT
```

---

## Author

**Tanvir Anzum**  
AI & Data Researcher  
- LinkedIn: [linkedin.com/in/aanzum](https://www.linkedin.com/in/aanzum)  
- ResearchGate: [Tanvir-Anzum](https://www.researchgate.net/profile/Tanvir-Anzum)
