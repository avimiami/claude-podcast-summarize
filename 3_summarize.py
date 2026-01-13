"""
Script 3: Summarization
Process transcripts with category-specific prompts and generate summaries.
Run with: python 3_summarize.py --category global_macro
"""

import argparse
import json
from pathlib import Path
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI
from anthropic import Anthropic
from utils import (
    load_env_vars, read_text_file, create_summary_path,
    log_error, write_text_file, sanitize_filename
)
from datetime import datetime


def load_prompt_templates():
    """Load prompt templates from JSON file."""
    template_path = Path("prompt_templates.json")
    if not template_path.exists():
        raise FileNotFoundError(f"prompt_templates.json not found at {template_path}")

    with open(template_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_transcripts():
    """Get all transcript files from transcripts folder."""
    transcripts_path = Path("transcripts")
    if not transcripts_path.exists():
        return []

    transcripts = []
    for podcast_folder in transcripts_path.iterdir():
        if podcast_folder.is_dir():
            for transcript_file in podcast_folder.iterdir():
                if transcript_file.is_file() and transcript_file.suffix == '.txt':
                    # Skip metadata files
                    if not transcript_file.stem.endswith('_metadata'):
                        transcripts.append({
                            'podcast_name': podcast_folder.name,
                            'episode_title': transcript_file.stem,
                            'path': transcript_file
                        })

    return transcripts


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
def summarize_with_openai(transcript, prompt, api_key, model="gpt-4o"):
    """Generate summary using OpenAI API."""
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes podcast transcripts."
            },
            {
                "role": "user",
                "content": f"{prompt}\n\nTranscript:\n{transcript}"
            }
        ],
        max_tokens=4000,
        temperature=0.3
    )

    return response.choices[0].message.content


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
def summarize_with_anthropic(transcript, prompt, api_key, model="claude-3-5-sonnet-20241022"):
    """Generate summary using Anthropic API."""
    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model=model,
        max_tokens=4000,
        temperature=0.3,
        messages=[
            {
                "role": "user",
                "content": f"{prompt}\n\nTranscript:\n{transcript}"
            }
        ]
    )

    return response.content[0].text


def summarize_with_deepinfra(transcript, prompt, api_key, model="mixtral-8x7b"):
    """Generate summary using Deep Infra API (OpenAI-compatible)."""
    client = OpenAI(
        base_url="https://api.deepinfra.com/v1/openai",
        api_key=api_key
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes podcast transcripts."
            },
            {
                "role": "user",
                "content": f"{prompt}\n\nTranscript:\n{transcript}"
            }
        ],
        max_tokens=4000,
        temperature=0.3
    )

    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="Summarize podcast transcripts")
    parser.add_argument(
        "--category",
        type=str,
        required=True,
        help="Category to use for summarization (global_macro, AI, crypto, tech, general)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override the model specified in .env"
    )
    args = parser.parse_args()

    print(f"Podcast Summarization Script - Category: {args.category}")
    print("=" * 50)

    # Load configuration
    config = load_env_vars()

    if not config['llm_key']:
        print("Error: LLM_API_KEY not found in .env file")
        print("Please copy .env.template to .env and add your API key")
        return

    # Load prompt templates
    try:
        templates = load_prompt_templates()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Get category
    category = args.category
    if category not in templates:
        available = ', '.join(templates.keys())
        print(f"Error: Category '{category}' not found")
        print(f"Available categories: {available}")
        return

    template = templates[category]
    prompt = template['prompt']

    # Get model to use
    model = args.model or config['summary_model']
    provider = config['llm_provider']

    print(f"Using provider: {provider}")
    print(f"Using model: {model}")

    # Get all transcripts
    transcripts = get_transcripts()
    if not transcripts:
        print("Error: No transcripts found in transcripts/ folder")
        print("Please run Script 2 (2_transcribe.py) first")
        return

    print(f"\nFound {len(transcripts)} transcripts to process")

    # Process each transcript
    success_count = 0
    error_count = 0

    for transcript_info in tqdm(transcripts, desc="Summarizing"):
        podcast_name = transcript_info['podcast_name']
        episode_title = transcript_info['episode_title']
        transcript_path = transcript_info['path']

        print(f"\nProcessing: {podcast_name} - {episode_title}")

        try:
            # Create summary path
            summary_path = create_summary_path(category, podcast_name, episode_title)

            # Skip if already summarized
            if summary_path.exists():
                print(f"  Already exists, skipping")
                success_count += 1
                continue

            # Read transcript
            transcript = read_text_file(transcript_path)

            # Check if transcript is too long (truncate if needed)
            max_chars = 100000  # Approx 100k chars
            if len(transcript) > max_chars:
                print(f"  Warning: Transcript too long ({len(transcript)} chars), truncating")
                transcript = transcript[:max_chars]

            # Generate summary based on provider
            print(f"  Generating summary...")
            if provider == "openai":
                summary = summarize_with_openai(transcript, prompt, config['llm_key'], model)
            elif provider == "anthropic":
                summary = summarize_with_anthropic(transcript, prompt, config['llm_key'], model)
            elif provider == "deepinfra":
                summary = summarize_with_deepinfra(transcript, prompt, config['llm_key'], model)
            else:
                print(f"  Error: Unknown provider '{provider}'")
                log_error("3_summarize", f"Unknown provider: {provider}")
                error_count += 1
                continue

            # Add metadata to summary
            metadata_header = f"""# Summary Metadata
Category: {category}
Podcast: {podcast_name}
Episode: {episode_title}
Generated: {datetime.now().isoformat()}
Model: {provider}/{model}

---

"""
            full_summary = metadata_header + summary

            # Save summary
            write_text_file(summary_path, full_summary)

            print(f"  Saved to: {summary_path}")
            success_count += 1

        except Exception as e:
            print(f"  Error: {str(e)}")
            log_error("3_summarize", f"Failed to summarize {episode_title}: {str(e)}")
            error_count += 1
            continue

    # Summary
    print("\n" + "=" * 50)
    print("Summarization Summary:")
    print(f"  Successfully summarized: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(transcripts)}")
    print(f"\nSummaries saved to: {Path('summaries').absolute() / category}")


if __name__ == "__main__":
    main()
