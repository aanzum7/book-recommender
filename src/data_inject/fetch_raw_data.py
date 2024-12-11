import os
import logging
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.http import MediaIoBaseDownload  # type: ignore
from google.oauth2.service_account import Credentials  # type: ignore
from config.logging_configs import logger  # Assuming the logging configuration is imported

# Configuration
FOLDER_ID = '1fhUg8fnBsAe-ktK0Eq3o7zWtvkmh0J7M'  # Google Drive Folder ID
SERVICE_ACCOUNT_FILE = 'config\service_account\json_key_google_drive.json'  # Path to your service account JSON file
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
RAW_FILES_DIR = 'data/raw_files'  # Directory to save files

# Ensure the output directory exists
os.makedirs(RAW_FILES_DIR, exist_ok=True)

# Initialize Google Drive API
def initialize_drive_service():
    """Initialize and return the Google Drive API client."""
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    logger.info("Google Drive API client initialized successfully.")
    return drive_service

# List CSV files in the folder
def list_csv_files(drive_service):
    """List all CSV files in the specified folder."""
    query = f"'{FOLDER_ID}' in parents and mimeType = 'text/csv'"  # Query to filter CSV files
    try:
        results = drive_service.files().list(q=query).execute()
        files = results.get('files', [])
        
        if not files:
            logger.info('No CSV files found in the folder.')
        else:
            logger.info(f"Found {len(files)} CSV file(s) in the folder:")
            for file in files:
                logger.info(f"File Name: {file['name']}, MIME Type: {file['mimeType']}, File ID: {file['id']}")
        
        return files
    except Exception as e:
        logger.error(f"Error while listing CSV files: {e}")
        return []

# Download a file from Google Drive
def download_file(drive_service, file_id, file_name):
    """Download the CSV file from Google Drive."""
    try:
        request = drive_service.files().get_media(fileId=file_id)
        output_path = os.path.join(RAW_FILES_DIR, file_name)
        with open(output_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logger.info(f"Download progress for file {file_name}: {int(status.progress() * 100)}%")
        logger.info(f"File {file_name} downloaded successfully to {output_path}.")
    except Exception as e:
        logger.error(f"Error downloading {file_name}: {e}")

# Main function to fetch CSV files from Google Drive
def fetch_raw_data():
    """Fetch all CSV files from the Google Drive folder."""
    logger.info("Starting to fetch raw data from Google Drive...")

    try:
        # Initialize the Google Drive API service
        drive_service = initialize_drive_service()

        # List all CSV files in the folder
        files = list_csv_files(drive_service)

        # Download each CSV file
        for file in files:
            file_id = file['id']
            file_name = file['name']
            download_file(drive_service, file_id, file_name)

        logger.info("Fetching raw data completed.")

    except Exception as e:
        logger.error(f"An error occurred while fetching raw data: {e}")

# Entry point for the script execution
def main():
    fetch_raw_data()

if __name__ == "__main__":
    main()
