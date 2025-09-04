import yt_dlp

class VideoInfo:
    def __init__(self, url: str):
        self.url = url
        self.info = None

    def fetch_info(self):
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            self.info = ydl.extract_info(self.url, download=False)
        return self.info

    def get_title(self):
        if self.info:
            return self.info.get('title', '')
        return ''

    def get_duration(self):
        if self.info:
            return self.info.get('duration', 0)  # seconds
        return 0

    def get_thumbnails(self):
        if self.info:
            return self.info.get('thumbnails', [])
        return []

    def get_subtitles(self):
        if self.info:
            return self.info.get('subtitles', {})
        return {}
