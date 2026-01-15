# Streamlit data_editor infinite refresh loop

## Bug Description
The episode selector UI (`1_episode_selector.py`) has an infinite refresh loop when displaying the episodes table with checkbox selections.

## Current Behavior
- The table continuously refreshes/re-renders itself
- Happens when using `st.data_editor` with checkbox column
- Makes the app unusable
- Table is "going bananas" with constant refreshing

## Attempted Fixes (Commit: a333cf8)
The following changes were attempted but did not resolve the issue:
- Added `episodes_fetched` session state flag to track whether episodes have been fetched
- Modified fetch logic to prevent auto-re-fetching on every interaction
- Implemented selection state management via `st.session_state.selections` dictionary
- Added unique keys to all widgets (text inputs, buttons, selectboxes)
- Separated display dataframe from session state dataframe

## Files Affected
- `1_episode_selector.py` (lines 258-327: data_editor section)

## Root Cause Analysis
The infinite refresh occurs because:
1. When user checks/unchecks a box in `data_editor`, Streamlit reruns the entire script
2. The script re-creates the dataframe with the 'selected' column on every rerun
3. This creates a new state that triggers another rerun, creating an infinite loop
4. The condition checking `st.session_state.episodes_df.empty` was also contributing to the problem

## Environment
- **OS**: Windows
- **Python**: Running in `.venv` virtual environment
- **Package Manager**: `uv`
- **Framework**: Streamlit

## Priority
**High** - Makes the episode selector UI completely unusable

## Next Steps
- Need to properly separate dataframe state from widget interactions
- Consider using `st.session_state` to track selections without recreating the entire dataframe
- May need to refactor the data_editor implementation or use alternative approach

## Related Commit
- Commit: `a333cf8` - "Attempt to fix Streamlit infinite refresh loop - KNOWN BUG"
