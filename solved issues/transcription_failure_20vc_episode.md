# Transcription Failure: 20VC Episode

## Date
2026-01-15

## Episode Details
- **Podcast**: The Twenty Minute VC (20VC): Venture Capital, Startup Funding, The Pitch
- **Episode Title**: 20VC: Anthropic's $10BN Fundraise: Have They Beaten Cursor Already | a16z's $15BN Fundraise: Is the Middle Dead in VC Today? | How OpenAI Could Go to Zero and ElevenLabs at $11BN: Buy or Not?
- **Audio URL**: (available in CSV)

## Error
```
Error: [Errno 2] No such file or directory: "transcripts\\The Twenty Minute VC (20VC)_ Venture Capital _ Startup Funding _ The Pitch\\20VC_ Anthropic's $10BN Fundraise_ Have They Beaten Cursor Already _ a16z's $15BN Fundraise_ Is the Middle Dead in VC Today_ _ How OpenAI Could Go to Zero and ElevenLabs at $11BN_ Buy or Not_.txt"
```

## Root Cause Analysis

### Issue 1: Filename Length
The combined podcast name and episode title creates an extremely long path:
- Podcast folder: `The Twenty Minute VC (20VC)_ Venture Capital _ Startup Funding _ The Pitch`
- Episode file: `20VC_ Anthropic's $10BN Fundraise_ Have They Beaten Cursor Already _ a16z's $15BN Fundraise_ Is the Middle Dead in VC Today_ _ How OpenAI Could Go to Zero and ElevenLabs at $11BN_ Buy or Not_.txt`
- Total path exceeds Windows 260 character limit

### Issue 2: Invalid Characters
The filename contains special characters that may cause issues:
- Colon `:` in episode titles
- Question mark `?` at the end
- Multiple underscores from sanitization

## Potential Solutions

### Option 1: Truncate Filenames More Aggressively
Modify `sanitize_filename()` in `utils.py` to truncate to 100 characters instead of 200:
```python
def sanitize_filename(name):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    name = name.strip('. ')
    return name[:100]  # Reduced from 200
```

### Option 2: Use Hash-based Filenames
Generate unique filenames using hash of the full title:
```python
import hashlib
def sanitize_filename(name):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    if len(name) > 80:
        hash_suffix = hashlib.md5(name.encode()).hexdigest()[:8]
        name = name[:70] + '_' + hash_suffix
    return name.strip('. ')
```

### Option 3: Simplify Podcast Folder Names
Remove long descriptive text from podcast folder names, keeping only the core name.

### Option 4: Enable Long Paths on Windows
Add manifest to enable Windows long path support (requires admin privileges).

## Recommended Fix
Implement **Option 2** (hash-based) as it:
- Preserves filename readability for normal-length titles
- Guarantees unique filenames for truncated titles
- Prevents path length issues on Windows
- Maintains backward compatibility

## Next Steps
1. Modify `sanitize_filename()` in `utils.py`
2. Re-run transcription for the failed episode
3. Test with other long-named episodes
