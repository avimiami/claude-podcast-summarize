\# Python Podcast Processing System - Implementation Plan



\## Overview

Three standalone Python scripts for podcast management: extract episodes from OPML, transcribe audio, and generate summaries.



\## Script 1: Episode Selector (Flask/Streamlit UI)



\*\*Purpose:\*\* Parse OPML file, display recent episodes, allow selection, export to CSV



\*\*Key Components:\*\*

\- OPML parser (using `xml.etree.ElementTree` or `feedparser`)

\- RSS feed fetcher for each podcast

\- Simple UI (recommend Streamlit for faster development)

\- Episode data structure: podcast\_name, episode\_title, publish\_date, audio\_url, description

\- CSV export with selected episodes



\*\*Dependencies:\*\* `streamlit`, `feedparser`, `pandas`, `requests`



\*\*Output:\*\* `selected\_episodes.csv` with columns: podcast\_name, episode\_title, publish\_date, audio\_url



\*\*Test Criteria:\*\* Successfully parse OPML, fetch 5-10 recent episodes per podcast, display sorted list, export selections to valid CSV



---



\## Script 2: Download \& Transcription



\*\*Purpose:\*\* Read CSV, download/transcribe audio files, organize results



\*\*Key Components:\*\*

\- CSV reader

\- Audio downloader (handle mp3/m4a formats)

\- Deep Infra API integration for speech-to-text

\- File organization: `transcripts/{podcast\_name}/{episode\_title}.txt`

\- Progress tracking/logging

\- Error handling for failed downloads/transcriptions



\*\*Dependencies:\*\* `pandas`, `requests`, `pathlib`



\*\*Input:\*\* `selected\_episodes.csv`



\*\*Output:\*\* Organized folder structure with transcript text files



\*\*Test Criteria:\*\* Download 2-3 episodes, successfully transcribe via Deep Infra API, verify folder structure and file contents



---



\## Script 3: Summarization



\*\*Purpose:\*\* Process transcripts with category-specific prompts, generate summaries



\*\*Key Components:\*\*

\- Transcript file reader

\- Prompt template manager (JSON/dict with categories: global\_macro, AI, crypto, etc.)

\- LLM API integration (OpenAI/Anthropic/Deep Infra)

\- Summary output: `summaries/{category}/{podcast\_name}/{episode\_title}\_summary.txt`

\- Metadata extraction based on prompt requirements



\*\*Dependencies:\*\* `pathlib`, `requests` or LLM client library



\*\*Input:\*\* `transcripts/` folder + category selection



\*\*Output:\*\* Organized summaries with extracted details



\*\*Test Criteria:\*\* Process 2 transcripts with different category prompts, verify structured output matches template requirements



---



\## Recommended Framework Approach



\*\*Use Python with modular functions:\*\*

\- Each script is self-contained but shares common utilities (API calls, file I/O)

\- Create `utils.py` for shared functions (API wrappers, file operations)

\- Use `config.py` or `.env` for API keys and settings

\- Keep scripts simple and linear - no complex state management needed



\*\*Project Structure:\*\*

```

podcast\_processor/

├── config.py (or .env)

├── utils.py

├── 1\_episode\_selector.py

├── 2\_transcribe.py

├── 3\_summarize.py

├── prompt\_templates.json

├── selected\_episodes.csv

├── transcripts/

└── summaries/

```



\*\*Development Order:\*\*

1\. Build Script 1, test with real OPML file

2\. Build Script 2, test with 2-3 episodes from Script 1 output

3\. Build Script 3, test with transcripts from Script 2 output



This plan gives an LLM agent clear boundaries for each component and testable milestones.

