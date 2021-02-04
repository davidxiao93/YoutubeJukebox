from track import Track

class Source:


    def fetch_meta(self, source_id: str) -> Track:
        raise NotImplementedError


    def fetch_file(self, source_id: str) -> bool:
        """
        Attempts to download the file coresponding to the provided track
        :returns false if not successful
        """
        raise NotImplementedError
