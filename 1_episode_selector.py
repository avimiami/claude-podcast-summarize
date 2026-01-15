"""
Script 1: Episode Selector UI
Parses OPML file, displays podcast episodes, allows selection, exports to CSV.
Run with: streamlit run 1_episode_selector.py
"""

import streamlit as st
import feedparser
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from utils import load_env_vars, sanitize_filename

# Cache configuration
CACHE_DIR = Path("episode_cache")
CACHE_FILE = CACHE_DIR / "episodes_cache.parquet"
CACHE_META = CACHE_DIR / "cache_metadata.json"


def parse_opml(file_path):
    """Parse OPML file and extract podcast feeds."""
    tree = ET.parse(file_path)
    root = tree.getroot()

    feeds = []
    for outline in root.iter():
        if outline.tag.endswith('outline'):
            attrib = outline.attrib
            if 'xmlUrl' in attrib or 'htmlUrl' in attrib:
                feeds.append({
                    'title': attrib.get('text', attrib.get('title', 'Unknown')),
                    'url': attrib.get('xmlUrl', attrib.get('htmlUrl', ''))
                })

    return feeds


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_episodes_cached(feed_url, max_episodes=10):
    """Fetch recent episodes from a podcast RSS feed (cached)."""
    try:
        feed = feedparser.parse(feed_url)
        episodes = []

        for entry in feed.entries[:max_episodes]:
            # Get audio URL (enclosure or media:content)
            audio_url = ''
            if hasattr(entry, 'enclosures') and len(entry.enclosures) > 0:
                audio_url = entry.enclosures[0].get('href', '')
            elif hasattr(entry, 'media_content') and len(entry.media_content) > 0:
                audio_url = entry.media_content[0].get('url', '')
            elif 'links' in entry:
                for link in entry.links:
                    if link.get('type', '').startswith('audio/'):
                        audio_url = link.href
                        break

            # Parse publish date
            pub_date = ''
            if hasattr(entry, 'published_parsed'):
                pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')
            elif hasattr(entry, 'updated_parsed'):
                pub_date = datetime(*entry.updated_parsed[:6]).strftime('%Y-%m-%d')

            episodes.append({
                'title': entry.get('title', 'No title'),
                'pub_date': pub_date,
                'audio_url': audio_url,
                'description': entry.get('description', '')[:500]
            })

        return episodes
    except Exception as e:
        return []


def load_cache():
    """Load cached episodes from parquet file."""
    if CACHE_FILE.exists():
        try:
            return pd.read_parquet(CACHE_FILE)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def save_cache(df):
    """Save episodes to parquet cache."""
    CACHE_DIR.mkdir(exist_ok=True)
    df.to_parquet(CACHE_FILE, index=False)


def main():
    st.set_page_config(
        page_title="Podcast Episode Selector",
        layout="wide",
        page_icon="🎧"
    )

    st.title("🎧 Podcast Episode Selector")
    st.markdown("Select podcast episodes for transcription and summarization.")

    # Initialize session state
    if 'episodes_df' not in st.session_state:
        st.session_state.episodes_df = pd.DataFrame()
    if 'feeds' not in st.session_state:
        st.session_state.feeds = []
    if 'episodes_fetched' not in st.session_state:
        st.session_state.episodes_fetched = False

    # Default OPML file path
    default_opml = Path("antennapod-feeds-2026-01-12.opml")

    # Sidebar for file upload and settings
    with st.sidebar:
        st.header("⚙️ Settings")

        # File uploader with default file
        st.subheader("OPML File")
        use_default = st.checkbox(f"Use default: {default_opml.name}", value=True, key="use_default")

        if use_default and default_opml.exists():
            st.success(f"✅ Using {default_opml.name}")
            opml_source = default_opml
        else:
            uploaded_file = st.file_uploader("Upload OPML", type=['opml', 'xml'], key="opml_uploader")
            if uploaded_file:
                temp_path = Path("temp_opml.opml")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                opml_source = temp_path
            else:
                opml_source = None

        # Max episodes setting
        config = load_env_vars()
        max_episodes = st.number_input(
            "Episodes per podcast",
            min_value=1,
            max_value=50,
            value=config['max_episodes'],
            help="Number of recent episodes to fetch",
            key="max_episodes"
        )

        st.divider()

        # Cache info
        if CACHE_FILE.exists():
            cache_age = datetime.fromtimestamp(CACHE_FILE.stat().st_mtime)
            st.info(f"📦 Cache from {cache_age.strftime('%H:%M')}\n{len(load_cache())} episodes")
            if st.button("🗑️ Clear Cache", key="clear_cache"):
                CACHE_FILE.unlink()
                st.session_state.episodes_fetched = False
                st.rerun()
        else:
            st.info("📦 No cache found")

    # Main area
    if opml_source and opml_source.exists():
        # Parse OPML
        if not st.session_state.feeds:
            with st.spinner("Parsing OPML file..."):
                st.session_state.feeds = parse_opml(opml_source)
                st.success(f"✅ Found {len(st.session_state.feeds)} podcast feeds")

        # Load cached episodes
        cached_df = load_cache()
        if not cached_df.empty:
            st.info(f"📦 Loaded {len(cached_df)} episodes from cache")

        # Fetch button
        col1, col2 = st.columns([1, 3])
        with col1:
            fetch_button = st.button("🔄 Fetch Episodes", type="primary", use_container_width=True, key="fetch_button")

        if fetch_button:
            st.session_state.episodes_fetched = True

        # Only fetch if button clicked OR if we have cached data but haven't fetched yet
        should_fetch = fetch_button or (not st.session_state.episodes_fetched and not cached_df.empty)

        if should_fetch:
            st.write("Fetching episodes...")

            # Progress bar and status
            progress_bar = st.progress(0)
            status_text = st.empty()

            all_episodes = []
            seen_urls = set()  # Track unique episodes

            # Add cached episodes first
            if not cached_df.empty:
                for _, row in cached_df.iterrows():
                    url = row.get('audio_url', '')
                    if url and url not in seen_urls:
                        all_episodes.append(row.to_dict())
                        seen_urls.add(url)

            # Fetch new episodes
            new_count = 0
            for i, feed in enumerate(st.session_state.feeds):
                # Update status (compact)
                status_text.markdown(f"**{i+1}/{len(st.session_state.feeds)}:** {feed['title'][:50]}...")

                episodes = fetch_episodes_cached(feed['url'], max_episodes)

                for ep in episodes:
                    # Skip if we already have this episode
                    if ep['audio_url'] and ep['audio_url'] in seen_urls:
                        continue

                    all_episodes.append({
                        'podcast_name': feed['title'],
                        'episode_title': ep['title'],
                        'publish_date': ep['pub_date'],
                        'audio_url': ep['audio_url'],
                        'description': ep['description']
                    })
                    seen_urls.add(ep['audio_url'])
                    new_count += 1

                progress_bar.progress((i + 1) / len(st.session_state.feeds))

            status_text.empty()

            # Create DataFrame
            if all_episodes:
                df = pd.DataFrame(all_episodes)
                st.session_state.episodes_df = df

                # Save to cache
                save_cache(df)

                st.success(f"✅ Found {len(df)} total episodes ({new_count} new)")
            else:
                st.error("❌ No episodes found")
                st.stop()

        # Display episodes if we have them
        if not st.session_state.episodes_df.empty:
            df = st.session_state.episodes_df

            # Filters
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                search = st.text_input("🔍 Search episodes", placeholder="Type to filter...", key="search_input")
            with col2:
                sort_by = st.selectbox("Sort by", ['publish_date', 'podcast_name'], key="sort_by")
            with col3:
                order = st.selectbox("Order", ['Newest first', 'Oldest first'] if sort_by == 'publish_date' else ['A-Z', 'Z-A'], key="order")

            # Apply filters
            if search:
                df = df[df['episode_title'].str.contains(search, case=False, na=False) |
                       df['podcast_name'].str.contains(search, case=False, na=False)]

            # Sort
            if sort_by == 'publish_date':
                df = df.sort_values('publish_date', ascending=(order == 'Oldest first'))
            else:
                df = df.sort_values('podcast_name', ascending=(order == 'A-Z'))

            st.caption(f"Showing {len(df)} episodes")

            # Initialize selections in session state if not exists (track as set of audio_urls)
            if 'selections' not in st.session_state:
                st.session_state.selections = set()

            # Track the data key to detect when filter/sort changes
            data_key = f"{len(df)}_{search}_{sort_by}_{order}"

            # Check if this is a new data view (filter/sort changed)
            is_new_data_view = ('last_data_key' not in st.session_state or
                                st.session_state.last_data_key != data_key)

            if is_new_data_view:
                # Data changed: rebuild display with saved selections
                st.session_state.last_data_key = data_key
                df_display = df.copy()
                df_display.insert(0, 'selected', df_display['audio_url'].isin(st.session_state.selections).astype(bool))
            else:
                # Same data: add empty selected column, let widget maintain state
                df_display = df.copy()
                df_display.insert(0, 'selected', False)

            # Display table with checkbox selection
            edited_df = st.data_editor(
                df_display,
                column_config={
                    'selected': st.column_config.CheckboxColumn(
                        "Select",
                        width="small"
                    ),
                    'podcast_name': st.column_config.TextColumn(
                        "Podcast",
                        width="medium"
                    ),
                    'episode_title': st.column_config.TextColumn(
                        "Episode",
                        width="large"
                    ),
                    'publish_date': st.column_config.TextColumn(
                        "Date",
                        width="small"
                    ),
                    'description': st.column_config.TextColumn(
                        "Description",
                        width="large",
                        disabled=True
                    ),
                    'audio_url': st.column_config.TextColumn(
                        "Audio URL",
                        width="medium",
                        disabled=True
                    )
                },
                hide_index=True,
                use_container_width=True,
                height=400,
                key="episode_editor"
            )

            # Get selected rows from edited dataframe
            selected_episodes = edited_df[edited_df['selected'] == True]

            # Update session state for persistence across filter/sort operations
            # Only update if the set of selections actually changed (prevents loops)
            new_selections = set(selected_episodes['audio_url'])
            if 'last_known_selections' not in st.session_state:
                st.session_state.last_known_selections = set()

            if new_selections != st.session_state.last_known_selections:
                st.session_state.selections = new_selections
                st.session_state.last_known_selections = new_selections

            # Show selected episodes section
            st.divider()

            if not selected_episodes.empty:
                st.subheader(f"Selected Episodes: {len(selected_episodes)}")

                # Simple text display (no flickering dataframe)
                for _, row in selected_episodes.iterrows():
                    st.text(f"{row['podcast_name']} - {row['episode_title']} ({row['publish_date']})")
            else:
                st.subheader("Selected Episodes: 0")
                st.info("Check the boxes in the table above to select episodes")

            # Export section
            st.divider()
            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                if st.button("💾 Export to CSV", type="primary", use_container_width=True, key="export_button"):
                    if not selected_episodes.empty:
                        export_df = selected_episodes[['podcast_name', 'episode_title',
                                                      'publish_date', 'audio_url', 'description']]

                        csv_path = Path("selected_episodes.csv")
                        export_df.to_csv(csv_path, index=False, encoding='utf-8')

                        st.success(f"✅ Exported {len(selected_episodes)} episodes")
                        st.download_button(
                            label="📥 Download CSV",
                            data=export_df.to_csv(index=False).encode('utf-8'),
                            file_name='selected_episodes.csv',
                            mime='text/csv',
                            use_container_width=True
                        )
                    else:
                        st.warning("⚠️ No episodes selected")

            with col2:
                if not selected_episodes.empty:
                    st.info(f"📊 Ready to process {len(selected_episodes)} episodes")

    else:
        st.warning("⚠️ Please upload an OPML file to get started")


if __name__ == "__main__":
    main()
