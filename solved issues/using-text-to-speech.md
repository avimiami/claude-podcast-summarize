Whisper Large V3 API User Guide
Overview
Whisper Large V3 is a general-purpose speech recognition model trained on a large dataset of diverse audio. It can perform multilingual speech recognition, speech translation, and language identification. This guide covers how to use the Whisper Large V3 model through the DeepInfra API.
API Endpoint
https://api.deepinfra.com/v1/openai
Prerequisites

A DeepInfra API key
Python 3.7+
OpenAI Python SDK: pip install openai
An audio file in a supported format

Supported Audio Formats
The API supports the following audio formats:

FLAC (.flac)
MP3 (.mp3)
MP4 (.mp4)
MPEG (.mpeg)
MPGA (.mpga)
M4A (.m4a)
OGG (.ogg)
WAV (.wav)
WebM (.webm)

Request Parameters
Create Transcription
ParameterTypeRequiredDescriptionfileFileYesThe audio file to transcribemodelStringYesModel ID: openai/whisper-large-v3languageStringNoISO-639-1 language code (e.g., en, es, fr)promptStringNoText prompt to guide the model's styleresponse_formatStringNoOutput format: json (default), text, srt, verbose_json, vtttemperatureNumberNoSampling temperature (0-1). Default: 0. Higher values produce more random resultstimestamp_granularitiesArrayNoTimestamp granularity: word or segment. Requires response_format to be verbose_json
Python Examples
Installation
bashpip install openai
Basic Transcription
pythonfrom openai import OpenAI

# Initialize the client
client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://api.deepinfra.com/v1/openai"
)

# Open your audio file
with open("speech.mp3", "rb") as audio_file:
    # Create transcription
    transcript = client.audio.transcriptions.create(
        model="openai/whisper-large-v3",
        file=audio_file
    )

# Print the transcribed text
print(transcript.text)
Transcription with Language Specification
pythonfrom openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://api.deepinfra.com/v1/openai"
)

with open("speech.mp3", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="en"  # Specify English
    )

print(transcript.text)
Transcription with Detailed Output
pythonfrom openai import OpenAI
import json

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://api.deepinfra.com/v1/openai"
)

with open("speech.mp3", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="verbose_json",
        timestamp_granularities=["word"]
    )

# Access detailed information
print(f"Text: {transcript.text}")
print(f"Duration: {transcript.duration} seconds")
print(f"Language: {transcript.language}")

# Print word-level timestamps
if hasattr(transcript, 'words'):
    for word in transcript.words:
        print(f"{word.word}: {word.start}s - {word.end}s")
Translation to English
pythonfrom openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://api.deepinfra.com/v1/openai"
)

with open("speech.mp3", "rb") as audio_file:
    # Translate audio to English
    translation = client.audio.translations.create(
        model="whisper-1",
        file=audio_file
    )

print(translation.text)
Response Formats
JSON (Default)
json{
  "text": "Hello, my name is Wolfgang and I come from Germany. Where are you heading today?"
}
Verbose JSON
json{
  "text": "Hello, my name is Wolfgang and I come from Germany. Where are you heading today?",
  "task": "transcribe",
  "language": "en",
  "duration": 10.5,
  "words": [
    {"word": "Hello", "start": 0.0, "end": 0.5},
    {"word": "my", "start": 0.6, "end": 0.8}
  ],
  "segments": [...]
}
Text Format
Returns plain text without JSON wrapping.
SRT/VTT
Returns subtitles in SRT or VTT format with timestamps.
Error Handling
pythonfrom openai import OpenAI
from openai import APIError

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://api.deepinfra.com/v1/openai"
)

try:
    with open("speech.mp3", "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    print(transcript.text)
except APIError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
except FileNotFoundError:
    print("Audio file not found")
except Exception as e:
    print(f"Error: {e}")
Pricing
The API costs $0.00045 per minute of audio processing.
Best Practices

Language Specification: Provide the language parameter if known - it improves accuracy and latency
Prompt Guidance: Use the prompt parameter to guide the model's style (e.g., technical terminology)
Response Format: Choose verbose_json for detailed timing information, text for simple output
Temperature: Use lower values (0-0.3) for accurate transcriptions, higher values (0.7-1) for creative guidance
File Size: Ensure audio files are in supported formats for best results

Additional Resources

Project Repository: https://github.com/openai/whisper
Research Paper: https://arxiv.org/abs/2212.04356
License: Apache 2.0

Support
For issues or questions:

Visit the DeepInfra documentation: https://deepinfra.com/docs
Contact support through the DeepInfra dashboard