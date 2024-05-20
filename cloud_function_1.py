from google.cloud import storage
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.auth.credentials import Credentials
from google.auth.credentials import AnonymousCredentials
from flask import Flask, request, Response

app = Flask(__name__)

# Initialize GCS client
storage_client = storage.Client()

@app.route('/', methods=['POST'])
def process_file_details(request):
    """Cloud Function to receive and process file details."""
    request_data = request.get_json()
    if not request_data:
        return 'Missing data in request body.', 400

    file_id = request_data.get('id')
    file_name = request_data.get('name')

    # Retrieve file from Google Drive using Drive API
    file_content = retrieve_file_from_drive(file_id)

    # Upload file to GCS bucket
    upload_to_gcs(file_name, file_content)

    return 'File details received successfully! File retrieved from Drive and stored in GCS.', 200


def retrieve_file_from_drive(file_id):
    # Load credentials from service account key file
    credentials = service_account.Credentials.from_service_account_file(
        'shared-vikas-56ca917c3058.json',
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )

    # Build Drive API service
    drive_service = build('drive', 'v3', credentials=credentials)

    try:
        # Fetch file content from Drive
        file = drive_service.files().get_media(fileId=file_id).execute()
        return file
    except Exception as e:
        return f'Error retrieving file from Drive: {e}'


def upload_to_gcs(file_name, file_content):
    # Get GCS bucket and blob objects
    bucket_name = 'exp-buck-001'
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    try:
        # Upload file content to GCS
        blob.upload_from_string(file_content)
    except Exception as e:
        return f'Error uploading file to GCS: {e}'

    return 'File uploaded to GCS successfully!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
