import configparser
from cryptography.fernet import Fernet


class AppConfig:
    __MAX_COMMENTS_LIMIT = 100
    __AWS_S3_BUCKET_NAME = "yt-scrap-vids-subbu"
    __AWS_S3_BUCKET_REGION = "us-east-1"
    __DATABASE_NAME = "YT_SCRAPPER_DB"
    __TBL_CHANNEL_INFO = "YT_CHANNEL_INFO"
    __TBL_CHANNEL_VIDEOS = "YT_CHANNEL_VIDEOS"
    __TBL_VIDEO_STATS = "YT_VIDEO_STATS"
    __TBL_VIDEO_COMMENTS = "YT_VIDEO_COMMENTS"

    def __init__(self):
        conf_obj = configparser.ConfigParser()
        conf_obj.read(r'conf.ini')
        self.conf = conf_obj['app_settings']

    @property
    def apiKey(self):
        encry_content = self.conf['yt_api_key']
        f = get_secret_key()
        decrypt = f.decrypt(encry_content.encode())
        return decrypt.decode()

    @property
    def aws_access_key_id(self):
        return self.conf['aws_access_key_id']

    @property
    def aws_secret_access_key(self):
        encry_content = self.conf['secret_access_key']
        f = get_secret_key()
        decrypt = f.decrypt(encry_content.encode())
        return decrypt.decode()

    @property
    def max_comments_limit(self):
        return self.__MAX_COMMENTS_LIMIT

    @property
    def bucket_name(self):
        return self.__AWS_S3_BUCKET_NAME

    @property
    def bucket_region(self):
        return self.__AWS_S3_BUCKET_REGION

    @property
    def mongo_db_secret_key(self):
        encry_content = self.conf['mongo_db_secret_key']
        f = get_secret_key()
        decrypt = f.decrypt(encry_content.encode())
        return decrypt.decode()

    @property
    def database_name(self):
        return self.__DATABASE_NAME

    @property
    def tbl_name_channel_info(self):
        return self.__TBL_CHANNEL_INFO

    @property
    def tbl_name_channel_videos(self):
        return self.__TBL_CHANNEL_VIDEOS

    @property
    def tbl_name_video_stats(self):
        return self.__TBL_VIDEO_STATS

    @property
    def tbl_name_video_comments(self):
        return self.__TBL_VIDEO_COMMENTS

    @property
    def sql_db_creds(self):
        encry_content = self.conf['sql_db_secret_key']
        f = get_secret_key()
        decrypt = f.decrypt(encry_content.encode())
        return {
            "user": 'Subramanyam28',
            "password": decrypt.decode(),
            "account": 'dl58471.ap-southeast-1',
            "role": "ACCOUNTADMIN"
        }


def get_secret_key():
    with open('.shhhh') as fp:
        __key = fp.read().encode()
        f = Fernet(__key)
    return f
