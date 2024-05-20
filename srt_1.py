import os
import uuid
import subprocess
import numpy as np
from scipy.io import wavfile
from google.cloud import speech

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/vikash/Downloads/shared-vikas-56ca917c3058.json'


def convert_to_wav(audio_file_path, output_wav_path):
  """
  Converts an audio file (MP3 or WAV) to a single-channel WAV format using ffmpeg (if available).

  Args:
    audio_file_path: The path to the input audio file.
    output_wav_path: The path to save the converted WAV file.
  """

  # Check if ffmpeg is available
  try:
    subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  except FileNotFoundError:
    print("ffmgpeg not found. Pre-process the MP3 file or use a different library for handling ID3 tags.")
    return

  # Check file extension
  if not audio_file_path.lower().endswith(".mp3"):
    return  # Already WAV format, skip conversion

  # Use ffmpeg to pre-process MP3 (assuming ffmpeg is available)
  ffmpeg_command = ['ffmpeg', '-i', audio_file_path, '-vn', '-acodec', 'pcm_s16le', output_wav_path]
  try:
    subprocess.run(ffmpeg_command, check=True)
    print(f"Successfully pre-processed MP3 with ffmpeg to: {output_wav_path}")
  except subprocess.CalledProcessError as e:
    print(f"Error pre-processing MP3 with ffmpeg: {e}")
    return


def transcribe_audio(audio_file_path, project_id, chunk_size_seconds=30):
  """
  Transcribes the audio file in chunks and saves the text to a file.
  Leverages SciPy's wavfile module to read audio data.

  Args:
    audio_file_path: The path to the audio file.
    project_id: Your Google Cloud project ID.
    chunk_size_seconds: The duration (in seconds) of each audio chunk (default: 20).
  """
  encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16

  try:
    # Read audio data and sample rate using wavfile
    sample_rate_hertz, audio_content = wavfile.read(audio_file_path)

    # Check audio format and attempt conversion if necessary
    if audio_content.dtype == np.uint8:
      # Check for 8-bit unsigned integer
      # Try forcing conversion to 16-bit signed integer
      try:
        audio_content = audio_content.astype(np.int16)
        print("Successfully converted audio to 16-bit format.")
      except Exception as e:
        raise ValueError(f"Failed to convert audio format: {e}") from e
    elif audio_content.dtype not in (np.int16, np.float32):
      raise ValueError(f"Unsupported audio format: {audio_content.dtype}")
  except Exception as e:
    print(f"Error reading audio file: {e}")
    return

  # Process audio in chunks
  chunk_size = chunk_size_seconds * sample_rate_hertz  # Set chunk size in samples
  start_frame = 0
  text = ""

  while start_frame < len(audio_content):
    end_frame = min(start_frame + chunk_size, len(audio_content))
    chunk_data = audio_content[start_frame:end_frame].tobytes()  # Convert to bytes

    # Process the chunk
    try:
      chunk_text = transcribe_chunk_long_running(chunk_data, project_id, encoding, sample_rate_hertz)
      text += chunk_text
    except Exception as e:
      print(f"Error transcribing chunk at {start_frame/sample_rate_hertz:.2f} seconds: {e}")

    start_frame = end_frame

  # Save the combined transcription text
  text_filename = audio_file_path + ".txt"
  with open(text_filename, 'w') as text_file:
    text_file.write(text)
  print(f"Transcription saved to: {text_filename}")

def transcribe_chunk_long_running(chunk_data, project_id, encoding, sample_rate_hertz):
  """
  Transcribes a chunk of audio data using long-running recognition.

  Args:
    chunk_data: The audio chunk data as bytes.
    project_id: Your Google Cloud project ID.
  """
  client = speech.SpeechClient()
  config = speech.RecognitionConfig(
      encoding=encoding,
      sample_rate_hertz=sample_rate_hertz,
      language_code="en-US",  # Replace with your desired language code
      model="default"
  )

  # Create a RecognitionAudio object with the chunk data
  audio = speech.RecognitionAudio(content=chunk_data)

  # Use long_running_recognize with the RecognitionAudio object
  operation = client.long_running_recognize(config=config, audio=audio)
  print(f"Chunk recognition job submitted. Waiting for results...")
  response = operation.result()

  # Extract text
  chunk_text = ""
  for result in response.results:
    for alternative in result.alternatives:
      chunk_text += alternative.transcript + "\n"

  return chunk_text

def text_to_srt(text_file_path, srt_file_path):
  """
  Converts a text file containing transcript text to an SRT (SubRip) subtitle file.

  Args:
    text_file_path: The path to the text file containing the transcript.
    srt_file_path: The path to save the SRT subtitle file.
  """

  # Read transcript lines from the text file
  with open(text_file_path, 'r') as text_file:
    transcript_lines = text_file.readlines()

  # Initialize SRT file content and counter for subtitle IDs
  srt_content = ""
  subtitle_id = 1
  start_time = 0.0  # Assuming no explicit timestamps in the text file

  for line_index, line in enumerate(transcript_lines):
    # Skip empty lines
    if not line.strip():
      continue

    # New subtitle starts with a timestamp (estimate 5 seconds between subtitles)
    if line_index > 0:
      start_time += 5.0

    # Create the SRT subtitle block
    srt_block = f"{subtitle_id}\n{start_time:.3f} --> {start_time + 5.0:.3f}\n{line.strip()}\n\n"
    subtitle_id += 1
    srt_content += srt_block

  # Write the SRT content to the output file
  with open(srt_file_path, 'w') as srt_file:
    srt_file.write(srt_content)
  print(f"SRT subtitle file saved to: {srt_file_path}")

# Replace with your GCP project ID
project_id = "shared-vikas"

# Replace with the path to your audio file
audio_file_path = "/Users/vikash/Downloads/Sales_Call_example_1.mp3"

# Pre-process the MP3 with ffmpeg (if available)
output_wav_path = f"{audio_file_path[:-4]}.wav"  # Generate output WAV filename
convert_to_wav(audio_file_path, output_wav_path)

# If ffmpeg pre-processing is successful, transcribe the WAV file
if os.path.exists(output_wav_path):
  transcribe_audio(output_wav_path, project_id)  # Use the converted WAV file
  # Generate the SRT filename based on the audio filename
  text_file_path = f"{output_wav_path[:-4]}.wav.txt"
  srt_file_path = text_file_path[:-4] + ".srt"
  text_to_srt(text_file_path, srt_file_path)
else:
  print("ffmgpeg pre-processing failed. Skipping transcription.")

