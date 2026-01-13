# Podcast Processing System

A Python toolkit to extract podcast episodes from OPML, transcribe audio, and generate AI-powered summaries with category-specific prompts.

## Features

- **Episode Selection UI**: Parse OPML files and select episodes via Streamlit interface
- **Audio Transcription**: Transcribe podcasts using Deep Infra's Whisper API
- **AI Summarization**: Generate summaries using OpenAI, Anthropic, or Deep Infra APIs
- **Category-Specific Prompts**: Tailored summaries for global macro, AI, crypto, tech, and general topics
- **Windows Compatible**: Full Windows support with proper path handling

## Installation

### Prerequisites

- Python 3.8+
- `uv` package manager (recommended) or pip
- API keys for Deep Infra (transcription) and an LLM provider (summarization)

### Setup

```powershell
# Clone the repository
git clone https://github.com/avimiami/claude-podcast-summarize.git
cd claude-podcast-summarize

# Create virtual environment (if using uv)
uv venv

# Activate virtual environment (Windows)
.venv\Scripts\Activate

# Install dependencies
uv pip install -r requirements.txt

# Copy environment template and add your API keys
copy .env.template .env
notepad .env
```

## Configuration

Edit `.env` with your API keys:

```bash
# Deep Infra API Key (for transcription)
# Sign up at: https://deepinfra.com/
DEEP_INFRA_API_KEY=your_key_here

# LLM API Key (OpenAI, Anthropic, or Deep Infra)
LLM_API_KEY=your_key_here

# LLM Provider: openai, anthropic, or deepinfra
LLM_PROVIDER=openai

# Optional: Override default models
SUMMARY_MODEL=gpt-4o
TRANSCRIPTION_MODEL=whisper-large-v3
```

## Usage

### Step 1: Select Episodes

Launch the Streamlit UI to select podcast episodes:

```powershell
.venv\Scripts\Activate
python -m streamlit run 1_episode_selector.py
```

1. Upload your OPML file (export from your podcast app)
2. Click "Fetch Episodes" to load recent episodes
3. Select episodes using the checkboxes
4. Export to CSV (`selected_episodes.csv`)

### Step 2: Transcribe Audio

Transcribe the selected episodes:

```powershell
.venv\Scripts\Activate
python 2_transcribe.py
```

Transcripts are saved to `transcripts/{podcast_name}/{episode_title}.txt`

### Step 3: Generate Summaries

Generate summaries with category-specific prompts:

```powershell
.venv\Scripts\Activate
python 3_summarize.py --category global_macro
```

Available categories: `global_macro`, `AI`, `crypto`, `tech`, `general`

Summaries are saved to `summaries/{category}/{podcast_name}/{episode_title}_summary.txt`

## Project Structure

```
claude-podcast-summarize/
├── 1_episode_selector.py     # Streamlit UI for episode selection
├── 2_transcribe.py            # Audio transcription script
├── 3_summarize.py             # Summarization script
├── utils.py                   # Shared utilities
├── prompt_templates.yaml      # Category-specific prompts
├── .env.template              # Environment variables template
├── requirements.txt           # Python dependencies
├── transcripts/               # Generated transcripts (gitignored)
└── summaries/                 # Generated summaries (gitignored)
```

## Customizing Prompts

Edit `prompt_templates.yaml` to customize summary prompts for each category:

```yaml
global_macro:
  prompt: "Your custom prompt here..."
  extract_fields:
    - key_themes
    - predictions
```

## API Providers

### Transcription (Deep Infra)
- Model: `whisper-large-v3`
- Pricing: See https://deepinfra.com/pricing
- Sign up: https://deepinfra.com/

### Summarization
Choose from:
- **OpenAI**: GPT-4o, GPT-4-turbo
- **Anthropic**: Claude 3.5 Sonnet
- **Deep Infra**: Mixtral 8x7b, Llama 3 70b

## Windows-Specific Notes

- Always use backslashes for paths in PowerShell: `.venv\Scripts\Activate`
- Filenames are sanitized to remove invalid Windows characters
- Path length is limited to 200 characters to avoid the 260 character limit

## Troubleshooting

### Virtual Environment Won't Activate

```powershell
# For PowerShell
.venv\Scripts\Activate.ps1

# For Command Prompt
.venv\Scripts\activate.bat

# If you get execution policy errors (PowerShell):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Import Errors

Ensure you activated the virtual environment before installing packages:

```powershell
.venv\Scripts\Activate
uv pip install -r requirements.txt
```

### API Errors

- Check that your `.env` file contains valid API keys
- Verify your LLM provider is set correctly (`LLM_PROVIDER=openai|anthropic|deepinfra`)
- Check API rate limits and quotas

## License

MIT

## Contributing

Contributions welcome! Feel free to open issues or pull requests.
