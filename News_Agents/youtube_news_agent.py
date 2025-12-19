import argparse
import feedparser
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict, Optional

class YoutubeNewsAgent:
    CHANNELS = {
        "BBC News": "UC16niRr50-MSBwiO3YDb3RA",
        "CNN": "UCupvZG-5ko_eiXAupbDfxWw",
        "Al Jazeera English": "UCNye-wNBqNL5ZzHSJj3l8Bg"
    }

    def fetch_latest_video_id(self, channel_id: str) -> Optional[Dict[str, str]]:
        """
        Fetches the latest video ID and title from the channel's RSS feed.
        """
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        feed = feedparser.parse(rss_url)

        if not feed.entries:
            return None

        # Get the first entry (latest video)
        entry = feed.entries[0]
        return {
            "title": entry.title,
            "video_id": entry.yt_videoid,
            "link": entry.link
        }

    def get_transcript(self, video_id: str) -> str:
        """
        Fetches the transcript for a given video ID.
        """
        try:
            # Create an instance
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id)
            
            # The transcript object (FetchedTranscript) is iterable and yields snippets
            full_text = " ".join([snippet.text for snippet in transcript])
                
            return full_text
        except Exception as e:
            return f"[Error fetching transcript: {str(e)}]"

    def run(self):
        print("Fetching latest news transcripts from Top 3 Channels...\n")
        
        for name, channel_id in self.CHANNELS.items():
            print(f"=== {name} ===")
            rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                print("No videos found.\n")
                continue

            # Try to find a video with a transcript in the latest 5 entries
            found_transcript = False
            for entry in feed.entries[:5]:
                video_id = entry.yt_videoid
                title = entry.title
                link = entry.link
                
                print(f"Checking video: {title} ({link})")
                transcript = self.get_transcript(video_id)
                
                if not transcript.startswith("[Error"):
                    print(f"SUCCESS. Found transcript for: {title}")
                    print("\n--- Transcript (First 2000 chars) ---")
                    print(transcript[:2000] + ("..." if len(transcript) > 2000 else ""))
                    found_transcript = True
                    break
                else:
                    print(f"Skipping (No transcript available): {transcript}")
            
            if not found_transcript:
                print("Could not find any transcripts for recent videos.")

            print("\n" + "="*80 + "\n")

    def get_transcripts(self, limit_per_channel: int = 1) -> List[Dict[str, str]]:
        results = []
        print("Fetching latest news transcripts from Top 3 Channels...")
        
        for name, channel_id in self.CHANNELS.items():
            rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                continue

            found_count = 0
            for entry in feed.entries:
                if found_count >= limit_per_channel:
                    break
                    
                video_id = entry.yt_videoid
                title = entry.title
                link = entry.link
                
                transcript = self.get_transcript(video_id)
                
                if not transcript.startswith("[Error"):
                    results.append({
                        "source": f"YouTube - {name}",
                        "title": title,
                        "url": link,
                        "content": transcript
                    })
                    found_count += 1
        
        return results

def main():
    agent = YoutubeNewsAgent()
    agent.run()

if __name__ == "__main__":
    main()
