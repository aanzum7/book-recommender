# Book Recommender System

This project is focused on building a **Recommendation System for Books** that provides personalized book recommendations based on user preferences, ratings, and other factors. It leverages data processing, machine learning models, and collaborative filtering to suggest books to users.

## Project Structure

### Core Files
- **`app.py`**: Main application to run the recommender system.
- **`main.py`**: Script to initiate and run the book recommendation engine.
- **`novelnexus.py`**: Module for novel-related data processing, including parsing and handling book-specific data.
- **`playground.py`**: Experimental and testing scripts to explore different approaches for recommendations.

### Configuration and Dependencies
- **`conda_requirements.txt`**: Environment dependencies for Conda, ensuring the proper libraries are installed to run the system.
- **`config/`**: Configuration files for setting up various parameters and API credentials, including Google Cloud service account credentials and other environment setups.

### Data and Logs
- **`data/`**: Datasets used in the system, such as books, ratings, and user data. This folder contains the data used for training the recommendation models.
  - **`raw_files/`**: Raw files containing book information.
  - **`processed_data/`**: Cleaned and preprocessed data for further analysis.
- **`logs/`**: Logs related to the application, such as model training, errors, or other relevant output.
- **`data_inject/`**: Scripts or modules used for injecting new data into the system.
- **`data_preprocessing/`**: Scripts for preprocessing the data before feeding it to the recommendation models.

### Source Code
- **`src/`**: The source code for the recommendation system, including algorithms, models, data handling, and recommendation logic.

## Project Flow

1. **Raw Data Collection**:
   - Source: Raw files are collected from Kaggle or similar platforms.
   - Real Scenario: Data will be fetched from databases or other live sources.

2. **Preprocessing**:
   - Clean and preprocess the raw files to remove noise and ensure data quality.
   - Based on specific parameters, the dataset is reduced to create a smaller, manageable version for MVP or demo purposes.

3. **Recommendation Types**:
   - **Demographic Recommendations**:
     - Based on age group.
     - Suggests books that are most reviewed by users in the same age group.
   - **Geographic Recommendations**:
     - Based on city group.
     - Suggests books that are most reviewed by users in the same city group.
   - **Collaborative Clustering**:
     - Groups users into clusters based on similar reading patterns.
     - Recommends books that are popular within the same cluster group.
   - **Book-Centric Collaborative Recommendations (Future Plan)**:
     - For each book, suggest other books collaboratively read by similar user groups.

4. **Deployment**:
   - The system is deployed on Streamlit for a user-friendly interface.
   - Demo Link: [NovelNexus](https://aanzum7-book-recommender-novelnexus-uphs6x.streamlit.app/)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/aanzum7/book-recommender.git
    cd book-recommender
    ```

2. Set up the environment:
    - Using Conda:
      ```bash
      conda create --name book-recommender python=3.8
      conda activate book-recommender
      conda install --file conda_requirements.txt
      ```

3. Install any additional dependencies if required.

## Running the Application

To start the book recommender system, you can run the main script:

```bash
python app.py
```

This will start the system and provide personalized book recommendations based on the available data.

## Contributing

Feel free to fork the repository and submit issues or pull requests for any changes or improvements you'd like to make.

