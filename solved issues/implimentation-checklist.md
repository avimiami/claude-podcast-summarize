\# Implementation Plan



\## Phase 1: Script 1 (Episode Selector)

\- \[ ] Parse OPML file

\- \[ ] Fetch RSS feeds

\- \[ ] Display in Streamlit UI

\- \[ ] Export selected episodes to CSV

\- \*\*Test\*\*: Verify CSV has all required fields



\## Phase 2: Script 2 (Transcription)

\- \[ ] Read CSV input

\- \[ ] Download/pass audio to Deep Infra API

\- \[ ] Save transcripts in organized folders

\- \[ ] Add progress bars and error handling

\- \*\*Test\*\*: Verify 2-3 transcripts complete successfully



\## Phase 3: Script 3 (Summarization)

\- \[ ] Read transcripts

\- \[ ] Load prompt templates

\- \[ ] Call LLM API with category-specific prompts

\- \[ ] Save structured summaries

\- \*\*Test\*\*: Verify summaries match template requirements

