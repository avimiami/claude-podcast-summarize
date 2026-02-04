# Podcast Processing System - Complete Workflow

## Quick Start Workflow

### Step 1: Select Episodes (Generate CSV)
**Script:** `1_episode_selector.py`

**What it does:** Parses OPML file → Displays podcast episodes → Exports your selections to CSV

**How to run:**
```powershell
.venv\Scripts\Activate
python -m streamlit run 1_episode_selector.py
```

**What you do:**
1. Open the Streamlit UI in your browser
2. Browse episodes from your podcasts
3. Check the boxes for episodes you want to process
4. Click "Export Selected Episodes"

**Output:** `selected_episodes.csv` file containing:
- podcast_name
- episode_title
- publish_date
- audio_url
- description

---

### Step 2: Download & Transcribe (Generate Text)
**Script:** `2_transcribe.py`

**What it does:** Downloads audio files → Transcribes using Whisper API → Saves organized transcripts

**How to run:**
```powershell
# With default CSV (selected_episodes.csv in current directory)
.venv\Scripts\python.exe 2_transcribe.py

# OR with custom CSV path
.venv\Scripts\python.exe 2_transcribe.py --csv "C:\path\to\your.csv"
```

**What it does automatically:**
1. Reads the CSV file
2. Downloads MP3 files to `temp_audio/`
3. Sends audio to Deep Infra Whisper API
4. Saves transcripts to `transcripts/YYYY-MM-DD/podcast_name/episode.txt`
5. Creates metadata files with transcription details

**Output:**
- **Transcripts:** `transcripts/2025-01-15/` (organized by date)
- **Audio files:** `temp_audio/` (can be deleted after transcription)
- **Progress:** Shows real-time progress in terminal

**Processing time:** ~45-60 seconds per episode

---

### Step 3: Summarize (Generate Insights)
**Script:** `3_summarize.py`

**What it does:** Reads transcripts → Applies AI prompt template → Extracts structured insights

**How to run:**
```powershell
# With AI category (for AI/tech podcasts) - processes ALL transcripts
.venv\Scripts\python.exe 3_summarize.py --category AI

# Filter by specific date (RECOMMENDED - only processes today's transcripts)
.venv\Scripts\python.exe 3_summarize.py --category AI --date 2025-01-15

# With other categories
.venv\Scripts\python.exe 3_summarize.py --category global_macro --date 2025-01-15
.venv\Scripts\python.exe 3_summarize.py --category crypto --date 2025-01-15
.venv\Scripts\python.exe 3_summarize.py --category tech --date 2025-01-15
.venv\Scripts\python.exe 3_summarize.py --category general --date 2025-01-15
```

**What it does automatically:**
1. Scans `transcripts/` folder (optionally filtered by date)
2. Loads the category-specific prompt from `prompt_templates.yaml`
3. Sends each transcript to LLM API
4. Extracts structured information based on category
5. Saves summaries to `summaries/category/YYYY-MM-DD/podcast_name/episode_summary.txt`

**Output:**
- **Summaries:** `summaries/AI/2025-01-15/` (organized by category and date)
- **Each summary contains:**
  - Metadata (date, model, category)
  - Structured extraction based on category

**Processing time:** ~15-25 seconds per episode

---

## Complete Example Workflow

### Scenario: You want to process 10 new podcast episodes

```powershell
# STEP 1: Select episodes
.venv\Scripts\Activate
python -m streamlit run 1_episode_selector.py
# [Check 10 episodes in browser → Click Export]

# STEP 2: Transcribe all 10 episodes
.venv\Scripts\python.exe 2_transcribe.py --csv "C:\Users\avico\Downloads\my_episodes.csv"
# [Wait ~8-10 minutes, watch progress bar]
# [Transcripts saved to: transcripts/2025-01-15/]

# STEP 3: Generate AI summaries (ONLY for today's transcripts)
.venv\Scripts\python.exe 3_summarize.py --category AI --date 2025-01-15
# [Wait ~3-4 minutes, watch progress bar]
# [Summaries saved to: summaries/AI/2025-01-15/]

# DONE! Read your summaries
notepad summaries\AI\2025-01-15\Podcast_Name\episode_summary.txt
```

---

## File Structure After Processing

```
claude-code-podcast-generator/
├── selected_episodes.csv          # Output from Step 1
├── transcripts/                    # Output from Step 2
│   ├── 2025-01-14/                # Old transcripts (if any)
│   │   └── podcast_name/
│   │       └── episode.txt
│   └── 2025-01-15/                # Today's transcripts
│       ├── ChinaTalk/
│       │   ├── episode.txt
│       │   └── episode_metadata.json
│       ├── The a16z Show/
│       │   └── episode.txt
│       └── ... (one per podcast)
├── summaries/                      # Output from Step 3
│   └── AI/
│       └── 2025-01-15/            # Today's summaries
│           ├── ChinaTalk/
│           │   └── episode_summary.txt
│           ├── The a16z Show/
│           │   └── episode_summary.txt
│           └── ... (one per podcast)
└── temp_audio/                     # Temporary MP3 downloads (can delete)
    ├── podcast1_episode1.mp3
    └── ... (one per episode)
```

---

## Category Selection Guide

Choose your category based on podcast content:

| Category | Best For | Extracts |
|----------|----------|----------|
| `AI` | AI, machine learning, tech podcasts | Technologies, companies, breakthroughs, concerns |
| `global_macro` | Economics, finance, markets | Predictions, data points, sentiment, insights |
| `crypto` | Cryptocurrency, DeFi, Web3 | Assets, price predictions, regulations, trends |
| `tech` | General tech, startups, business | Trends, companies, disruptions, investment themes |
| `general` | Mixed content, any podcast | Main topics, insights, facts, quotes |

---

## Pro Tips

### Re-running Scripts
- **Step 1:** Can export new CSVs anytime (overwrites `selected_episodes.csv`)
- **Step 2:** Skips already transcribed episodes (checks if file exists)
- **Step 3:** Skips already summarized episodes (checks if file exists)

### Processing in Batches
```powershell
# Day 1: Process 5 episodes
.venv\Scripts\python.exe 2_transcribe.py
.venv\Scripts\python.exe 3_summarize.py --category AI

# Day 2: Process 5 more episodes
.venv\Scripts\python.exe 2_transcribe.py
# Automatically goes to transcripts/2025-01-16/

.venv\Scripts\python.exe 3_summarize.py --category AI
# Automatically goes to summaries/AI/2025-01-16/
```

### Multiple Categories for Same Transcripts
```powershell
# Generate AI summaries
.venv\Scripts\python.exe 3_summarize.py --category AI

# Also generate macro summaries (for the same transcripts!)
.venv\Scripts\python.exe 3_summarize.py --category global_macro

# Results in:
# summaries/AI/2025-01-15/
# summaries/global_macro/2025-01-15/
```

### Cleanup
```powershell
# Delete downloaded audio files (saves space)
Remove-Item temp_audio\* -Force

# Or keep them if you want to re-transcribe with different model
```

---

## Troubleshooting

### "No such file or directory" errors
→ Make sure you activated venv: `.venv\Scripts\Activate`

### "DEEP_INFRA_API_KEY not found"
→ Add API key to `.env` file (copy from `.env.template`)

### Script hangs or errors out
→ Check `errors.log` file for detailed error messages

### Transcripts folder structure looks wrong
→ Old transcripts stay in old structure, new ones use date folders. Both work!

---

## Summary

1. **Step 1:** Use Streamlit UI → Export CSV (one-time selection)
2. **Step 2:** Run with `--csv` argument → Get transcripts (45s/episode)
3. **Step 3:** Run with `--category` + `--date` → Get summaries (20s/episode)

**Total time for 10 episodes:** ~15-20 minutes (mostly automated)

---

## Date Filtering - Recommended Workflow

**Why use date filtering?**
- Faster: Only process today's transcripts instead of all of them
- Cheaper: Don't re-summarize old episodes with API credits
- Safer: Avoid accidentally re-processing hundreds of old transcripts

**Best practice:**
```powershell
# Step 1: Transcribe (saves to today's date folder)
.venv\Scripts\python.exe 2_transcribe.py --csv "my_episodes.csv"
# Output: transcripts/2025-01-15/

# Step 2: Summarize ONLY today's transcripts
.venv\Scripts\python.exe 3_summarize.py --category AI --date 2025-01-15
# Output: summaries/AI/2025-01-15/
```

**How to find available dates:**
```powershell
# List all date folders in transcripts
dir transcripts

# Example output:
# 2025-01-14/
# 2025-01-15/
# 2025-01-16/
```

**Processing old transcripts:**
```powershell
# If you want to summarize transcripts from a previous date
.venv\Scripts\python.exe 3_summarize.py --category AI --date 2025-01-14
```

**Processing everything (use with caution):**
```powershell
# This will process ALL transcripts from ALL dates
.venv\Scripts\python.exe 3_summarize.py --category AI
# Warning: Can be expensive and time-consuming if you have many transcripts!
```
