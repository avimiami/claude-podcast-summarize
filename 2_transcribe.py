"""
Script 2: Download & Transcribe
Reads CSV from Script 1, downloads/transcribes audio files using Deep Infra API.
Run with: python 2_transcribe.py
"""

import pandas as pd
import requests
from pathlib import Path
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential
from utils import (
    load_env_vars, sanitize_filename, create_transcript_path,
    log_error, write_text_file
)
from datetime import datetime
import json


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
def transcribe_audio_deepinfra(audio_url, api_key, endpoint, model="whisper-large-v3"):
    """
    Transcribe audio using Deep Infra API.
    Can pass audio URL directly without downloading.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "audio": audio_url
    }

    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=300)
        response.raise_for_status()
        result = response.json()

        # Deep Infra Whisper returns text in 'text' field
        return result.get('text', '')

    except requests.exceptions.RequestException as e:
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

        try:
            # Create transcript path
            transcript_path = create_transcript_path(podcast_name, episode_title)

            # Skip if already transcribed
            if transcript_path.exists():
                print(f"  Already exists, skipping")
                success_count += 1
                continue

            # Transcribe using Deep Infra API
            print(f"  Transcribing via Deep Infra API...")
            transcription = transcribe_audio_deepinfra(
                audio_url,
                config['deep_infra_key'],
                config['deep_infra_url'],
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

            print(f"  Saved to: {transcript_path}")
            success_count += 1

        except Exception as e:
            print(f"  Error: {str(e)}")
            log_error("2_transcribe", f"Failed to transcribe {episode_title}: {str(e)}")
            error_count += 1
            continue

    # Summary
    print("\n" + "=" * 50)
    print("Transcription Summary:")
    print(f"  Successfully transcribed: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(df)}")
    print(f"\nTranscripts saved to: {Path('transcripts').absolute()}")


if __name__ == "__main__":
    main()
