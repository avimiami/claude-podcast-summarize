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
from datetime import datetime
from utils import load_env_vars, sanitize_filename


def parse_opml(file_path):
    """Parse OPML file and extract podcast feeds."""
    tree = ET.parse(file_path)
    root = tree.getroot()

    feeds = []
    # OPML uses namespaces, find them
    namespaces = {
        'opml': 'http://www.opml.org/spec2',
        'default': 'http://www.opml.org/spec2'
    }

    # Try different paths for outline elements
    for outline in root.iter():
        if outline.tag.endswith('outline'):
            attrib = outline.attrib
            if 'xmlUrl' in attrib or 'htmlUrl' in attrib:
                feeds.append({
                    'title': attrib.get('text', attrib.get('title', 'Unknown')),
                    'url': attrib.get('xmlUrl', attrib.get('htmlUrl', ''))
                })

    return feeds


def fetch_episodes(feed_url, max_episodes=10):
    """Fetch recent episodes from a podcast RSS feed."""
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
                'description': entry.get('description', '')[:500]  # Truncate long descriptions
            })

        return episodes
    except Exception as e:
        st.error(f"Error fetching from {feed_url}: {str(e)}")
        return []


def main():
    st.set_page_config(page_title="Podcast Episode Selector", layout="wide")

    st.title("Podcast Episode Selector")
    st.write("Upload an OPML file to select podcast episodes for transcription.")

    # File uploader
    uploaded_file = st.file_uploader("Choose an OPML file", type=['opml', 'xml'])

    if uploaded_file is not None:
        # Save uploaded file temporarily
        temp_path = Path("temp_opml.opml")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Parse OPML
        with st.spinner("Parsing OPML file..."):
            feeds = parse_opml(temp_path)
            st.write(f"Found {len(feeds)} podcast feeds")

        # Clean up temp file
        temp_path.unlink()

        # Load config
        config = load_env_vars()
        max_episodes = config['max_episodes']

        # Fetch episodes
        if st.button("Fetch Episodes", type="primary"):
            progress_bar = st.progress(0)
            all_episodes = []

            for i, feed in enumerate(feeds):
                st.write(f"Fetching from: {feed['title']}")
                episodes = fetch_episodes(feed['url'], max_episodes)

                for ep in episodes:
                    all_episodes.append({
                        'podcast_name': feed['title'],
                        'episode_title': ep['title'],
                        'publish_date': ep['pub_date'],
                        'audio_url': ep['audio_url'],
                        'description': ep['description']
                    })

                progress_bar.progress((i + 1) / len(feeds))

            st.write(f"Found {len(all_episodes)} total episodes")

            # Create DataFrame
            if all_episodes:
                df = pd.DataFrame(all_episodes)

                # Sort options
                sort_by = st.radio("Sort by:", ['publish_date', 'podcast_name'])
                if sort_by == 'publish_date':
                    df = df.sort_values('publish_date', ascending=False)
                else:
                    df = df.sort_values('podcast_name')

                # Display with checkboxes
                st.write("### Select Episodes to Process")
                st.write("Check the box next to each episode you want to transcribe.")

                # Add a select all checkbox
                select_all = st.checkbox("Select All Episodes")

                if select_all:
                    df['selected'] = True
                else:
                    df['selected'] = False

                # Display editable dataframe
                edited_df = st.data_editor(
                    df,
                    column_config={
                        'selected': st.column_config.CheckboxColumn(
                            "Select",
                            help="Check to include this episode"
                        ),
                        'podcast_name': st.column_config.TextColumn("Podcast", width="medium"),
                        'episode_title': st.column_config.TextColumn("Episode", width="large"),
                        'publish_date': st.column_config.TextColumn("Date", width="small"),
                        'description': st.column_config.TextColumn("Description", width="large"),
                        'audio_url': st.column_config.TextColumn("Audio URL", width="large")
                    },
                    hide_index=True,
                    use_container_width=True
                )

                # Export selected episodes
                selected_count = edited_df['selected'].sum()

                col1, col2 = st.columns([1, 1])
                with col1:
                    st.write(f"Selected: {selected_count} episodes")

                with col2:
                    if st.button("Export Selected to CSV", type="primary"):
                        selected_episodes = edited_df[edited_df['selected'] == True]

                        if not selected_episodes.empty:
                            # Remove the selected column for export
                            export_df = selected_episodes[['podcast_name', 'episode_title',
                                                          'publish_date', 'audio_url', 'description']]

                            csv_path = Path("selected_episodes.csv")
                            export_df.to_csv(csv_path, index=False, encoding='utf-8')

                            st.success(f"Exported {len(selected_episodes)} episodes to selected_episodes.csv")
                            st.download_button(
                                label="Download CSV",
                                data=export_df.to_csv(index=False).encode('utf-8'),
                                file_name='selected_episodes.csv',
                                mime='text/csv'
                            )
                        else:
                            st.warning("No episodes selected. Please select at least one episode.")
            else:
                st.error("No episodes found. Please check your OPML file and feed URLs.")


if __name__ == "__main__":
    main()
