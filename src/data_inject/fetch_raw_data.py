import os
import logging
from config.logging_configs import logger  # Assuming the logging configuration is imported

# Configuration
FOLDER_ID = '1fhUg8fnBsAe-ktK0Eq3o7zWtvkmh0J7M'  # Google Drive Folder ID
SERVICE_ACCOUNT_FILE = os.path.join('config', 'service_account', 'json_key_google_drive.json')  # Path to service account JSON file
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
RAW_FILES_DIR = os.path.join('data', 'raw_files')  # Directory to save files
REQUIRED_RAW_FILES = ['Books.csv', 'Ratings.csv', 'Users.csv']

# Ensure the output directory exists
os.makedirs(RAW_FILES_DIR, exist_ok=True)

def local_raw_files_exist() -> bool:
    """Check if all required raw CSV files already exist locally and are not empty."""
    return all(
        os.path.isfile(os.path.join(RAW_FILES_DIR, fname)) and os.path.getsize(os.path.join(RAW_FILES_DIR, fname)) > 0
        for fname in REQUIRED_RAW_FILES
    )

# Initialize Google Drive API
def initialize_drive_service():
    """Initialize and return the Google Drive API client."""
    from googleapiclient.discovery import build  # type: ignore
    from google.oauth2.service_account import Credentials  # type: ignore

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
    from googleapiclient.http import MediaIoBaseDownload  # type: ignore

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
    """Fetch all CSV files from Google Drive if credentials exist; otherwise skip and use existing local data."""
    has_local_data = local_raw_files_exist()
    has_credentials = os.path.isfile(SERVICE_ACCOUNT_FILE)

    if not has_credentials:
        if has_local_data:
            logger.info(
                f"Google Drive credentials not present ('{SERVICE_ACCOUNT_FILE}'), "
                f"but local raw files already exist in '{RAW_FILES_DIR}'. "
                "Skipping remote fetch and loading existing local files."
            )
            return
        else:
            logger.warning(
                f"Google Drive credentials ('{SERVICE_ACCOUNT_FILE}') not present "
                f"and local raw files are missing in '{RAW_FILES_DIR}'."
            )
            return

    logger.info("Service account key found. Checking Google Drive for latest raw datasets...")
    try:
        drive_service = initialize_drive_service()
        files = list_csv_files(drive_service)

        for file in files:
            file_id = file['id']
            file_name = file['name']
            download_file(drive_service, file_id, file_name)

        logger.info("Fetching raw data from Google Drive completed successfully.")

    except Exception as e:
        if has_local_data:
            logger.warning(
                f"Failed to fetch latest data from Google Drive ({e}). "
                "Falling back to existing local raw files."
            )
        else:
            logger.error(f"An error occurred while fetching raw data from Google Drive: {e}")

# Entry point for the script execution
def main():
    fetch_raw_data()

if __name__ == "__main__":
    main()
