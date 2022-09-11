from abc import ABC, abstractmethod


class DbModel(ABC):
    @abstractmethod
    def db_write_comments(self, records):
        pass

    @abstractmethod
    def db_write_channel_info(self, record):
        pass

    @abstractmethod
    def db_write_video_stats(self, record):
        pass

    @abstractmethod
    def db_write_videos(self, records):
        pass
