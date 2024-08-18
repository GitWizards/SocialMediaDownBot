import re
import yt_dlp

class ShortsDownloader:
    def __init__(self):
        self.ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s'
        }

    def get_url(self, url):
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info['url']
                
                # Download the video content
                with yt_dlp.YoutubeDL({'format': 'best'}) as ydl:
                    result = ydl.urlopen(video_url).read()

                # Get the video title and clean it
                caption = info.get('title', '')
                caption = re.sub(r"\s*\B#\w+(?:\s*#\w+)*\s*$", "", caption)
                caption = re.sub("#", "", caption)

                return result, caption, "url"
        except Exception as e:
            print(f"An error occurred: {e}")
            return None, None, "error"