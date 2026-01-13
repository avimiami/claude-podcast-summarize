"""
Script 2: Download & Transcribe
Reads CSV from Script 1, downloads audio files, and transcribes using Deep Infra Whisper API.
Run with: python 2_transcribe.py
"""

import pandas as pd
import requests
from pathlib import Path
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI
from utils import (
    load_env_vars, sanitize_filename, create_transcript_path,
    log_error, write_text_file
)
from datetime import datetime
import json
import os


def download_audio_file(audio_url, download_path):
    """
    Download audio file from URL to local path.
    Returns the path to downloaded file.
    """
    try:
        response = requests.get(audio_url, stream=True, timeout=60)
        response.raise_for_status()

        # Ensure parent directory exists
        download_path.parent.mkdir(parents=True, exist_ok=True)

        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return download_path

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download audio: {str(e)}")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
def transcribe_audio_deepinfra(audio_file_path, api_key, model="openai/whisper-large-v3"):
    """
    Transcribe audio file using Deep Infra Whisper API via OpenAI SDK.
    Requires the audio file to be downloaded first.
    """
    # Initialize OpenAI client with Deep Infra base URL
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepinfra.com/v1/openai"
    )

    try:
        # Open the audio file and transcribe
        with open(audio_file_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model=model,
                file=audio_file
            )

        return transcript.text

    except Exception as e:
        raise Exception(f"Transcription API error: {str(e)}")


def create_metadata_file(transcript_path, metadata):
    """Create a metadata file alongside the transcript."""
    metadata_path = transcript_path.parent / f"{transcript_path.stem}_metadata.json"
    write_text_file(metadata_path, json.dumps(metadata, indent=2))


def main():
    print("Podcast Transcription Script")
    print("=" * 50)

    # Load configuration
    config = load_env_vars()

    if not config['deep_infra_key']:
        print("Error: DEEP_INFRA_API_KEY not found in .env file")
        print("Please copy .env.template to .env and add your API key")
        return

    # Check for CSV file
    csv_path = Path("selected_episodes.csv")
    if not csv_path.exists():
        print(f"Error: {csv_path} not found")
        print("Please run Script 1 (1_episode_selector.py) first to generate the CSV file")
        return

    # Create temporary download directory
    temp_dir = Path("temp_audio")
    temp_dir.mkdir(exist_ok=True)

    # Load episodes from CSV
    df = pd.read_csv(csv_path)
    print(f"\nFound {len(df)} episodes in CSV")

    # Process each episode
    success_count = 0
    error_count = 0

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Transcribing"):
        podcast_name = row['podcast_name']
        episode_title = row['episode_title']
        audio_url = row['audio_url']

        print(f"\n[{idx + 1}/{len(df)}] Processing: {episode_title}")

        # Skip if no audio URL
        if not audio_url or pd.isna(audio_url):
            print(f"  Skipping: No audio URL found")
            log_error("2_transcribe", f"No audio URL for {episode_title}")
            error_count += 1
            continue

        # Create paths
        transcript_path = create_transcript_path(podcast_name, episode_title)
        audio_filename = sanitize_filename(f"{podcast_name}_{episode_title}.mp3")
        audio_download_path = temp_dir / audio_filename

        # Skip if already transcribed
        if transcript_path.exists():
            print(f"  Already exists, skipping")
            success_count += 1
            continue

        try:
            # Download audio file
            print(f"  Downloading audio...")
            download_audio_file(audio_url, audio_download_path)
            print(f"  Downloaded to: {audio_download_path}")

            # Transcribe using Deep Infra API
            print(f"  Transcribing via Deep Infra Whisper API...")
            transcription = transcribe_audio_deepinfra(
                audio_download_path,
                config['deep_infra_key'],
                config['transcription_model']
            )

            if not transcription:
                print(f"  Warning: Empty transcription received")
                log_error("2_transcribe", f"Empty transcription for {episode_title}")
                error_count += 1
                continue

            # Save transcript
            write_text_file(transcript_path, transcription)

            # Create metadata file
            metadata = {
                "podcast_name": podcast_name,
                "episode_title": episode_title,
                "audio_url": audio_url,
                "transcription_date": datetime.now().isoformat(),
                "model_used": config['transcription_model']
            }
            create_metadata_file(transcript_path, metadata)

            print(f"  Saved transcript to: {transcript_path}")
            success_count += 1

        except Exception as e:
            print(f"  Error: {str(e)}")
            log_error("2_transcribe", f"Failed to transcribe {episode_title}: {str(e)}")
            error_count += 1
            continue

        finally:
            # Clean up downloaded audio file
            if audio_download_path.exists():
                try:
                    audio_download_path.unlink()
                    print(f"  Cleaned up audio file")
                except Exception as e:
                    print(f"  Warning: Could not delete audio file: {str(e)}")

    # Clean up temp directory if empty
    try:
        if temp_dir.exists() and not list(temp_dir.iterdir()):
            temp_dir.rmdir()
    except:
        pass

    # Summary
    print("\n" + "=" * 50)
    print("Transcription Summary:")
    print(f"  Successfully transcribed: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(df)}")
    print(f"\nTranscripts saved to: {Path('transcripts').absolute()}")


if __name__ == "__main__":
    main()
