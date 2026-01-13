"""
Shared utilities for the podcast processing system.
Windows-compatible with pathlib for all file operations.
"""

from pathlib import Path
import os
from datetime import datetime
from dotenv import load_dotenv


def load_env_vars():
    """Load API keys from .env file."""
    load_dotenv()
    return {
        'deep_infra_key': os.getenv('DEEP_INFRA_API_KEY'),
        'llm_key': os.getenv('LLM_API_KEY'),
        'llm_provider': os.getenv('LLM_PROVIDER', 'openai'),
        'max_episodes': int(os.getenv('MAX_EPISODES_PER_PODCAST', 10)),
        'transcription_model': os.getenv('TRANSCRIPTION_MODEL', 'whisper-large-v3'),
        'summary_model': os.getenv('SUMMARY_MODEL', 'gpt-4o'),
    }


def sanitize_filename(name):
    """
    Clean strings for valid Windows filenames.
    Removes invalid characters and limits length.
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    # Remove leading/trailing spaces and periods
    name = name.strip('. ')
    # Handle path length limits (Windows has 260 char limit)
    return name[:200]


def create_transcript_path(podcast_name, episode_title):
    """
    Create full path for a transcript file.
    Ensures directory structure exists.
    """
    base_path = Path("transcripts")
    podcast_folder = base_path / sanitize_filename(podcast_name)
    podcast_folder.mkdir(parents=True, exist_ok=True)
    return podcast_folder / f"{sanitize_filename(episode_title)}.txt"


def create_summary_path(category, podcast_name, episode_title):
    """
    Create full path for a summary file.
    Ensures directory structure exists.
    """
    base_path = Path("summaries")
    category_folder = base_path / sanitize_filename(category)
    podcast_folder = category_folder / sanitize_filename(podcast_name)
    podcast_folder.mkdir(parents=True, exist_ok=True)
    return podcast_folder / f"{sanitize_filename(episode_title)}_summary.txt"


def log_error(script_name, error_msg):
    """Consistent error logging with timestamp."""
    log_path = Path("errors.log")
    timestamp = datetime.now().isoformat()
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {script_name}: {error_msg}\n")


def create_folder_structure(base_path, subfolders):
    """Ensure directories exist - Windows compatible."""
    base = Path(base_path)
    for folder in subfolders:
        folder_path = base / folder
        folder_path.mkdir(parents=True, exist_ok=True)
    return base


def read_text_file(file_path):
    """Read text file with UTF-8 encoding."""
    path = Path(file_path)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_text_file(file_path, content):
    """Write text file with UTF-8 encoding."""
    path = Path(file_path)
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def get_audio_filename(url):
    """Extract filename from audio URL."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    filename = Path(parsed.path).name
    return sanitize_filename(filename)
