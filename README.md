# .mp3_to_srt_conversion_in_cloud
This project is designed to automate the process of converting uploaded .mp3 files in Google Drive to .wav format, transcribing the audio to text, and generating subtitles in .srt format. The transcribed subtitles are then uploaded back to the same Google Drive folder. The system involves Google Apps Script, Google Cloud Functions, Google Cloud Storage (GCS), and a local Python script for processing.

Table of Contents

Overview
Setup
Google Drive Setup
Google Cloud Setup
Local Machine Setup
Workflow
License
Overview

The project consists of the following components:

Google Apps Script: Detects new .mp3 file uploads to Google Drive and triggers a Google Cloud Function.
Google Cloud Function: Retrieves the .mp3 file from Google Drive and uploads it to a Google Cloud Storage bucket.
Local Python Script: Converts the .mp3 file to .wav format, processes it through a speech-to-text model, generates an .srt subtitle file, and uploads the .srt file back to Google Drive.
Setup

Google Drive Setup
Create a Google Drive Folder: This folder will be used for uploading .mp3 files and receiving the .srt subtitle files.
Google Cloud Setup
Enable APIs:

Google Drive API
Google Cloud Functions
Google Cloud Storage
Google Speech-to-Text API
Create a Cloud Storage Bucket: This bucket will temporarily store the .mp3 files before processing.

Set Up Google Cloud Function:

Create a Google Cloud Function that triggers on HTTP requests.
Ensure the function has the necessary permissions to access Google Drive and Google Cloud Storage.
Deploy the function with the appropriate code to handle the .mp3 file retrieval and upload to the GCS bucket.
Local Machine Setup
Install Python and Required Libraries:

Python 3.8 or higher
Required libraries: google-cloud-storage, google-cloud-speech, pydub, ffmpeg, srt, etc.
Python Script:

Develop a Python script that:
Downloads the .mp3 file from the GCS bucket.
Converts the .mp3 file to .wav format (single channel).
Uses Google Speech-to-Text API to transcribe the audio.
Converts the transcription into .srt format.
Uploads the .srt file back to the original Google Drive folder.
Workflow

Upload: The user uploads an .mp3 file to the designated Google Drive folder.
Detection: The Google Apps Script detects the new file and triggers the Google Cloud Function.
Processing:
The Google Cloud Function retrieves the .mp3 file from Google Drive and uploads it to the GCS bucket.
The local Python script downloads the .mp3 file from the GCS bucket, converts it to .wav format, transcribes the audio, converts the transcription to .srt format, and uploads the .srt file back to Google Drive.
License

This project is licensed under the MIT License. See the LICENSE file for more details.
