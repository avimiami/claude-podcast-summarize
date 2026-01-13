\# Podcast Processing System - Development Guide



\## Project Overview

Build 3 standalone Python scripts to process podcast episodes: extract from OPML, transcribe audio, and generate summaries with category-specific prompts.



\## Developer Context

\- Python coder with average experience (not CS background)

\- Familiar with basic React

\- Prefers clean code without emojis for easier debugging

\- Uses LLM assistance for development

\- \*\*Windows environment with `uv` package manager and `.venv` virtual environment\*\*



\## Critical Windows Setup Information



\*\*IMPORTANT FOR LLM AGENTS:\*\*

This project runs on Windows with a virtual environment. Always use these commands:



\### Activating Virtual Environment

```powershell

\# Windows PowerShell/Command Prompt

.venv\\Scripts\\Activate



\# You should see (.venv) in your prompt after activation

```



\### Installing Packages

```powershell

\# ALWAYS activate venv first, then use uv

.venv\\Scripts\\Activate

uv pip install package-name



\# Or install from requirements.txt

.venv\\Scripts\\Activate

uv pip install -r requirements.txt

```



\### Running Python Scripts

```powershell

\# ALWAYS activate venv first

.venv\\Scripts\\Activate

python script\_name.py



\# For Streamlit

.venv\\Scripts\\Activate

python -m streamlit run 1\_episode\_selector.py

```



\### Common Mistakes to Avoid

\- ❌ DON'T use `source .venv/bin/activate` (that's Linux/Mac)

\- ❌ DON'T use forward slashes: `.venv/Scripts/Activate` (wrong)

\- ✅ DO use backslashes: `.venv\\Scripts\\Activate` (correct)

\- ❌ DON'T run `pip install` without activating venv first

\- ❌ DON'T forget the `\\Scripts\\` part on Windows



\### Path Issues on Windows

```powershell

\# If you get path errors, use pathlib in Python code

from pathlib import Path



\# Good: Works on Windows and Unix

transcripts\_path = Path("transcripts") / podcast\_name / f"{episode\_title}.txt"



\# Bad: Will break on Windows

transcripts\_path = f"transcripts/{podcast\_name}/{episode\_title}.txt"

```



---



\## System Architecture



\### Script 1: Episode Selector UI (`1\_episode\_selector.py`)

\*\*Goal:\*\* Parse OPML → Display episodes → Export selections to CSV



\*\*Requirements:\*\*

\- Use Streamlit (simpler than Flask for this use case)

\- Parse OPML file containing podcast RSS feeds

\- Fetch recent episodes from each feed (last 10 episodes per podcast)

\- Display in sortable table (by date or podcast name)

\- Allow multi-select with checkboxes

\- Export selected episodes to `selected\_episodes.csv`



\*\*CSV Output Format:\*\*

```

podcast\_name,episode\_title,publish\_date,audio\_url,description

```



\*\*Windows-Specific Considerations:\*\*

\- Use `pathlib.Path` for all file operations

\- Handle Windows path length limits (max 260 characters by default)

\- Sanitize filenames to remove Windows-invalid characters: `< > : " / \\ | ? \*`



\*\*Testing Checklist:\*\*

\- \[ ] Successfully parse sample OPML file

\- \[ ] Fetch episodes from at least 3 different podcasts

\- \[ ] UI displays episodes sorted by date (default)

\- \[ ] Can toggle sort by podcast name

\- \[ ] Selection exports valid CSV with all required fields

\- \[ ] Handles missing fields gracefully (some episodes lack descriptions)



\*\*Running Script 1:\*\*

```powershell

.venv\\Scripts\\Activate

python -m streamlit run 1\_episode\_selector.py

```



---



\### Script 2: Download \& Transcribe (`2\_transcribe.py`)

\*\*Goal:\*\* Read CSV → Download/transcribe audio → Save organized transcripts



\*\*Requirements:\*\*

\- Read `selected\_episodes.csv`

\- Download audio files OR pass URLs directly to Deep Infra API

\- Use Deep Infra's speech-to-text API endpoint

\- Save transcripts in organized folder structure:

&nbsp; ```

&nbsp; transcripts\\

&nbsp;   ├── Podcast\_Name\_1\\

&nbsp;   │   ├── episode\_title\_1.txt

&nbsp;   │   └── episode\_title\_2.txt

&nbsp;   └── Podcast\_Name\_2\\

&nbsp;       └── episode\_title\_3.txt

&nbsp; ```

\- Include progress bars (use `tqdm`)

\- Log errors without stopping entire process

\- Create metadata file per transcript with: original\_url, transcription\_date, duration



\*\*Windows File Handling:\*\*

```python

\# Use pathlib for Windows compatibility

from pathlib import Path



def create\_transcript\_path(podcast\_name, episode\_title):

&nbsp;   base\_path = Path("transcripts")

&nbsp;   podcast\_folder = base\_path / sanitize\_filename(podcast\_name)

&nbsp;   podcast\_folder.mkdir(parents=True, exist\_ok=True)

&nbsp;   return podcast\_folder / f"{sanitize\_filename(episode\_title)}.txt"



def sanitize\_filename(name):

&nbsp;   # Remove Windows-invalid characters

&nbsp;   invalid\_chars = '<>:"/\\\\|?\*'

&nbsp;   for char in invalid\_chars:

&nbsp;       name = name.replace(char, '\_')

&nbsp;   # Handle path length limits

&nbsp;   return name\[:200]  # Leave room for full path

```



\*\*API Integration:\*\*

\- Deep Infra endpoint: (check their docs for current endpoint)

\- Handle rate limits with `tenacity` retry logic

\- Store API key in `.env` file



\*\*Testing Checklist:\*\*

\- \[ ] Successfully read CSV from Script 1

\- \[ ] Download 2 test episodes (different podcasts)

\- \[ ] Transcribe via Deep Infra API

\- \[ ] Verify folder structure created correctly on Windows

\- \[ ] Transcript files contain valid text

\- \[ ] Metadata files created with correct info

\- \[ ] Error handling works (test with invalid URL)



\*\*Running Script 2:\*\*

```powershell

.venv\\Scripts\\Activate

python 2\_transcribe.py

```



---



\### Script 3: Summarization (`3\_summarize.py`)

\*\*Goal:\*\* Process transcripts with category prompts → Generate structured summaries



\*\*Requirements:\*\*

\- Read transcripts from `transcripts\\` folder

\- Load prompt templates from `prompt\_templates.json`

\- Allow user to select category (global\_macro, AI, crypto, etc.)

\- Send transcript + prompt to LLM API (Deep Infra, OpenAI, or Anthropic)

\- Extract structured information based on category

\- Save summaries in organized folders:

&nbsp; ```

&nbsp; summaries\\

&nbsp;   ├── global\_macro\\

&nbsp;   │   └── Podcast\_Name\\

&nbsp;   │       └── episode\_title\_summary.txt

&nbsp;   └── AI\\

&nbsp;       └── Podcast\_Name\\

&nbsp;           └── episode\_title\_summary.txt

&nbsp; ```



\*\*Prompt Template Structure (`prompt\_templates.json`):\*\*

```json

{

&nbsp; "global\_macro": {

&nbsp;   "prompt": "Analyze this podcast transcript for global macro insights...",

&nbsp;   "extract\_fields": \["key\_themes", "predictions", "data\_points", "sentiment"]

&nbsp; },

&nbsp; "AI": {

&nbsp;   "prompt": "Summarize AI developments discussed...",

&nbsp;   "extract\_fields": \["technologies", "companies", "breakthroughs", "concerns"]

&nbsp; },

&nbsp; "crypto": {

&nbsp;   "prompt": "Extract crypto market analysis...",

&nbsp;   "extract\_fields": \["assets\_discussed", "price\_predictions", "regulatory\_news", "trends"]

&nbsp; }

}

```



\*\*Testing Checklist:\*\*

\- \[ ] Load prompt templates correctly

\- \[ ] Process 2 different transcripts with different categories

\- \[ ] LLM API integration works

\- \[ ] Summaries contain structured extracted fields

\- \[ ] Folder organization correct on Windows

\- \[ ] Can batch process multiple transcripts in same category



\*\*Running Script 3:\*\*

```powershell

.venv\\Scripts\\Activate

python 3\_summarize.py --category global\_macro

```



---



\## Shared Utilities (`utils.py`)



\*\*Common Functions Needed:\*\*

```python

from pathlib import Path

import os

from dotenv import load\_dotenv



def load\_env\_vars():

&nbsp;   """Load API keys from .env file"""

&nbsp;   load\_dotenv()

&nbsp;   return {

&nbsp;       'deep\_infra\_key': os.getenv('DEEP\_INFRA\_API\_KEY'),

&nbsp;       'llm\_key': os.getenv('LLM\_API\_KEY')

&nbsp;   }



def sanitize\_filename(name):

&nbsp;   """Clean strings for valid Windows filenames"""

&nbsp;   invalid\_chars = '<>:"/\\\\|?\*'

&nbsp;   for char in invalid\_chars:

&nbsp;       name = name.replace(char, '\_')

&nbsp;   # Remove leading/trailing spaces and periods

&nbsp;   name = name.strip('. ')

&nbsp;   # Handle path length limits (Windows has 260 char limit)

&nbsp;   return name\[:200]



def create\_folder\_structure(base\_path, subfolders):

&nbsp;   """Ensure directories exist - Windows compatible"""

&nbsp;   base = Path(base\_path)

&nbsp;   for folder in subfolders:

&nbsp;       folder\_path = base / folder

&nbsp;       folder\_path.mkdir(parents=True, exist\_ok=True)

&nbsp;   return base



def log\_error(script\_name, error\_msg):

&nbsp;   """Consistent error logging"""

&nbsp;   from datetime import datetime

&nbsp;   log\_path = Path("errors.log")

&nbsp;   timestamp = datetime.now().isoformat()

&nbsp;   with open(log\_path, 'a', encoding='utf-8') as f:

&nbsp;       f.write(f"\[{timestamp}] {script\_name}: {error\_msg}\\n")

```



\*\*Configuration (`.env`):\*\*

```

DEEP\_INFRA\_API\_KEY=your\_key\_here

LLM\_API\_KEY=your\_key\_here

MAX\_EPISODES\_PER\_PODCAST=10

TRANSCRIPTION\_MODEL=whisper-large-v3

SUMMARY\_MODEL=mixtral-8x7b

```



---



\## Development Workflow



\### Initial Setup (One Time)

```powershell

\# Create virtual environment (if not already created)

uv venv



\# Activate it

.venv\\Scripts\\Activate



\# Install all dependencies

uv pip install -r requirements.txt



\# Create .env file (add your API keys)

\# Use notepad or any text editor

notepad .env

```



\### Phase 1: Script 1 (Episode Selector)

```powershell

.venv\\Scripts\\Activate

python -m streamlit run 1\_episode\_selector.py

```

1\. Create basic Streamlit app skeleton

2\. Implement OPML parser

3\. Add RSS feed fetcher (test with 1 podcast first)

4\. Build UI with data table

5\. Add selection and export functionality

6\. Test with real OPML file containing 3-5 podcasts



\### Phase 2: Script 2 (Transcription)

```powershell

.venv\\Scripts\\Activate

python 2\_transcribe.py

```

1\. Create CSV reader

2\. Implement audio downloader (test with 1 episode)

3\. Integrate Deep Infra API (test with 1 short episode)

4\. Add folder organization logic with Windows path handling

5\. Implement progress tracking and error handling

6\. Test with 3-5 episodes from different podcasts



\### Phase 3: Script 3 (Summarization)

```powershell

.venv\\Scripts\\Activate

python 3\_summarize.py --category global\_macro

```

1\. Create transcript reader

2\. Build prompt template system

3\. Integrate LLM API (test with 1 category)

4\. Add structured output parsing

5\. Implement folder organization

6\. Test with multiple categories and transcripts



---



\## Error Handling Guidelines



\*\*Common Issues to Handle:\*\*

\- Invalid OPML file format

\- RSS feeds that are unreachable

\- Audio files that fail to download

\- API rate limits exceeded

\- Malformed audio files that can't be transcribed

\- LLM responses that don't match expected format

\- Disk space issues when downloading large files

\- \*\*Windows-specific: Path length exceeds 260 characters\*\*

\- \*\*Windows-specific: Invalid filename characters in episode titles\*\*



\*\*Approach:\*\*

\- Use try-except blocks around each major operation

\- Log errors to `errors.log` with timestamp and context

\- Continue processing remaining items when one fails

\- Provide clear error messages to user

\- Always use `pathlib.Path` for cross-platform compatibility



---



\## Testing Strategy



\*\*Manual Testing:\*\*

```powershell

\# Always activate venv first for testing

.venv\\Scripts\\Activate



\# Test each script

python -m streamlit run 1\_episode\_selector.py

python 2\_transcribe.py

python 3\_summarize.py --category AI

```



\- Test each script independently before moving to next

\- Use small sample sizes initially (2-3 episodes)

\- Verify file outputs manually

\- Check API usage/costs before large batches



\*\*Data Validation:\*\*

\- Ensure CSV has no missing critical fields

\- Verify transcripts aren't empty or truncated

\- Check summaries contain all requested extract\_fields

\- Confirm folder/file naming is consistent and Windows-compatible



---



\## Future Enhancements (Not in Scope Yet)



\- Automatic podcast categorization based on content

\- Web interface for all three scripts

\- Database storage instead of CSV/files

\- Scheduled automatic processing of new episodes

\- Multiple LLM provider support with fallback

\- Audio quality preprocessing before transcription

\- Semantic search across all transcripts



---



\## API Documentation References



\*\*Deep Infra:\*\*

\- Speech-to-Text: \[Check latest docs]

\- LLM Inference: \[Check latest docs]



\*\*Alternative APIs (if needed):\*\*

\- OpenAI Whisper API

\- Anthropic Claude API

\- AssemblyAI



---



\## Notes for LLM Agent



\### Critical Windows Instructions

\- \*\*ALWAYS use `.venv\\Scripts\\Activate` on Windows (backslashes, not forward slashes)\*\*

\- \*\*ALWAYS use `pathlib.Path` for file operations, never string concatenation with `/` or `\\\\`\*\*

\- \*\*ALWAYS sanitize filenames to remove Windows-invalid characters: `< > : " / \\ | ? \*`\*\*

\- \*\*ALWAYS check path lengths don't exceed 250 characters (leave buffer for 260 limit)\*\*

\- When user runs commands, assume they're in PowerShell or Command Prompt on Windows

\- Never suggest Linux/Mac commands like `source activate` or use forward slashes in paths



\### General Guidelines

\- Keep each script under 300 lines if possible

\- Use clear variable names (no abbreviations)

\- Add comments for complex logic

\- Include docstrings for all functions

\- Don't over-engineer - simple and working is better than complex and elegant

\- Test with real data, not mock data

\- Print progress to console (user is running from command line)

\- Handle edge cases (empty feeds, malformed XML, etc.)



---



\## Success Criteria



\*\*Script 1:\*\*

\- Parses OPML and displays episodes in under 30 seconds

\- UI is intuitive enough to use without documentation

\- CSV export is immediately usable by Script 2

\- Works correctly on Windows with proper path handling



\*\*Script 2:\*\*

\- Transcribes 1 hour of audio in under 5 minutes (depends on API)

\- No crashes on malformed audio URLs

\- Organized file structure is browsable and clear on Windows

\- Handles long podcast/episode names without path errors



\*\*Script 3:\*\*

\- Generates summaries that match template requirements

\- Extracts all specified fields consistently

\- Summary quality is good enough to read without reference to original transcript

\- Folder structure works correctly on Windows



---



\## Running the Scripts (Quick Reference)



```powershell

\# ALWAYS start with this

.venv\\Scripts\\Activate



\# Script 1: Episode Selector

python -m streamlit run 1\_episode\_selector.py



\# Script 2: Transcription (after exporting CSV from Script 1)

python 2\_transcribe.py



\# Script 3: Summarization (after Script 2 completes)

python 3\_summarize.py --category global\_macro



\# Or run all categories

python 3\_summarize.py --category AI

python 3\_summarize.py --category crypto

```



---



\## Project File Structure



```

podcast\_processor\\

├── .env                          # API keys (DO NOT COMMIT)

├── .gitignore

├── requirements.txt

├── README.md

├── claude.md                     # This file

├── config.py

├── utils.py

├── prompt\_templates.json

├── 1\_episode\_selector.py

├── 2\_transcribe.py

├── 3\_summarize.py

├── selected\_episodes.csv         # Output from Script 1

├── errors.log                    # Error logging

├── .venv\\                        # Virtual environment (Windows)

│   └── Scripts\\

│       └── Activate              # Activation script

├── transcripts\\                  # Output from Script 2

│   └── \[podcast\_folders]\\

└── summaries\\                    # Output from Script 3

&nbsp;   └── \[category\_folders]\\

```



---



\## Troubleshooting



\### Virtual Environment Issues

```powershell

\# If activation doesn't work, try:

.venv\\Scripts\\Activate.ps1  # For PowerShell

\# Or

.venv\\Scripts\\activate.bat  # For Command Prompt



\# If you get execution policy errors in PowerShell:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

```



\### Path Issues

```python

\# Always use pathlib

from pathlib import Path



\# Good

output\_path = Path("transcripts") / podcast / episode

output\_path.parent.mkdir(parents=True, exist\_ok=True)



\# Bad - will break on Windows

output\_path = f"transcripts/{podcast}/{episode}"

```



\### Encoding Issues

```python

\# Always specify UTF-8 encoding on Windows

with open(file\_path, 'w', encoding='utf-8') as f:

&nbsp;   f.write(content)

```



---



\## Git Commit Strategy



1\. Initial setup (requirements, folder structure, .gitignore)

2\. Script 1 complete and tested

3\. Script 2 complete and tested

4\. Script 3 complete and tested

5\. Bug fixes and refinements



Keep commits focused on one script at a time for easier debugging.



\### .gitignore essentials

```

.env

.venv/

\_\_pycache\_\_/

\*.pyc

transcripts/

summaries/

selected\_episodes.csv

errors.log

```



