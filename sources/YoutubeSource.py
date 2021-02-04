
"""
Need to look into how to embed youtube dl too
https://github.com/ytdl-org/youtube-dl/blob/master/README.md#embedding-youtube-dl
"""
import youtube_dl

from enums.download_status import DownloadStatus
from sources.source import Source
from track import Track

"""
also how to control volume. Via vlc or by system?

"""

class YoutubeSource(Source):
    def fetch_meta(self, source_id: str) -> Track:
        return Track(
            source_id="default_source_id",
            title="Default Title",
            artist="Default Artist",
            thumbnail="Thumbnail url",
            length=100,
            download_status=DownloadStatus.QUEUED
        )


    def fetch_file(self, source_id: str) -> bool:
        """
        Attempts to download the file coresponding to the provided track
        :returns false if not successful

                future additions
                    - downloads only audio
                    - have a mp3 cache (limit cache size though)
                    - normalise the mp3
        """
        print(f"downloaded {source_id}")
        return True
