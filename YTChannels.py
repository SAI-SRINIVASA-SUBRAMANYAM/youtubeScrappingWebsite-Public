import re
import json
from urllib.request import urlopen
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs
from AppConfig import AppConfig
import pytube
from io import BytesIO
import boto3
from YTLogger import YTLogger
from YTExceptions import YTExceptions
from MongoDbModel import MongoDbModel
from SnowflakeDbModel import SnowflakeDbModel


class YTChannels:
    __base_url = "https://www.youtube.com"

    def __init__(self):
        self.conf = AppConfig()
        self.YTChannelDetails = {
            "channel_info": dict(),
            "videos": [],
            "stats": {}
        }
        self.logger = YTLogger()
        self.m_db_model = MongoDbModel()
        self.sf_db_model = SnowflakeDbModel()

    def get_channel_info(self, search_string):
        __BASE_URL = self.__base_url + "/results?search_query={channel_name}&sp=EgIQAg"
        __BASE_URL = __BASE_URL.format(channel_name=search_string)
        self.logger.log(f"Searching for **{__BASE_URL}**", self.get_channel_info.__name__)
        channel_info = {
            "channel_id": None,
            "channel_title": None,
            "channel_url": None,
            "channel_thumbnail": None,
            "channel_subs": None,
            "channel_videos_count": None
        }
        try:
            channels_list_page = YTChannels.__get_queryable_page(__BASE_URL)
            search_template = "\{\"channelRenderer\":\{\"(.*?)\}\}\}\]\}\}\}"
            if channels_list_page is None or len(re.findall(search_template, channels_list_page)) == 0:
                return channel_info
            top_search_result = re.findall(search_template, channels_list_page)[0]
            channel_data = json.loads("{\"channelRenderer\":{\"" + top_search_result + "}}}]}}}")
            channel_info.update({
                "channel_id": channel_data["channelRenderer"]["channelId"],
                "channel_title": channel_data["channelRenderer"]["title"]["simpleText"],
                "channel_url":
                    channel_data["channelRenderer"]["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"][
                        "url"],
                "channel_thumbnail": channel_data["channelRenderer"]["thumbnail"]["thumbnails"][0]["url"],
                "channel_subs": channel_data["channelRenderer"]["subscriberCountText"]["simpleText"],
                "channel_videos_count": channel_data["channelRenderer"]["videoCountText"]["runs"][0]["text"]
            })
            self.logger.log(f"Channel found **{channel_info.get('channel_title')}**", self.__class__.__name__)
            self.YTChannelDetails.update({
                "channel_info": channel_info
            })
            self.sf_db_model.db_write_channel_info(channel_info)
            self.m_db_model.db_write_channel_info(channel_info)
        except Exception as e:
            YTExceptions(message=str(e), src=self.get_channel_info.__name__)

    def get_videos_by_channel(self, channel_url):
        yt_channel_videos_url = YTChannels.get_yt_channel_url(self.__base_url, channel_url)
        print("get_videos_by_channel")
        print(yt_channel_videos_url)
        self.logger.log(f"Searching for **{yt_channel_videos_url}**", self.get_videos_by_channel.__name__)
        if yt_channel_videos_url is None:
            YTExceptions(message="Unable to generate channel video", src=self.get_videos_by_channel.__name__)

        try:
            yt_channel_videos_page = YTChannels.__get_queryable_page(yt_channel_videos_url)
            search_template = "\{\"gridVideoRenderer\":\{\"(.*?)\}\]\}\}\}\]\}\}"
            videos = []
            for item in re.findall(search_template, yt_channel_videos_page):
                data = json.loads("{\"gridVideoRenderer\":{\"" + item + "}]}}}]}}")
                views_count = ""
                if data["gridVideoRenderer"]["viewCountText"].get("simpleText"):
                    views_count = data["gridVideoRenderer"]["viewCountText"]["simpleText"]
                else:
                    for view in data["gridVideoRenderer"]["viewCountText"].get("runs"):
                        views_count = view.get("text")
                        break

                published_time = ""
                if data["gridVideoRenderer"].get("publishedTimeText"):
                    published_time = data["gridVideoRenderer"]["publishedTimeText"]["simpleText"]
                else:
                    published_time = "LIVE"
                videos.append({
                    "channel_id": self.YTChannelDetails.get('channel_info').get('channel_id'),
                    "thumbnail_url": data["gridVideoRenderer"]["thumbnail"]["thumbnails"][0]["url"],
                    "video_title": data["gridVideoRenderer"]["title"]["runs"][0]["text"],
                    "views_count": views_count,
                    "video_id": data["gridVideoRenderer"]["videoId"],
                    "published_time": published_time
                })
            self.YTChannelDetails.update({
                "videos": videos
            })
            self.logger.log(f"Found latest videos of total **{len(videos)}**", self.get_videos_by_channel.__name__)
            self.m_db_model.db_write_videos(videos)
            self.sf_db_model.db_write_videos(videos)
        except Exception as e:
            YTExceptions(message=str(e), src=self.get_videos_by_channel.__name__)

    def download_video(self, video_id):
        try:
            url = self.__get_video_url(self.__base_url, video_id)
            self.logger.log(f"Downloading video **{url}**", self.download_video.__name__)
            buffer, filename, filesize = YTChannels.get_download_stream(url)
            self.logger.log(f"Completed downloading name & size is **{filename}** **{filesize}**",
                            self.download_video.__name__)
            return buffer, filename
        except Exception as e:
            YTExceptions(message=f"Exception while downloading file **{str(e)}**",
                         src=self.download_video.__name__)

    def get_video_stats(self, video_id):
        video_info = {
            "likes_count": 0,
            "comments_count": 0,
            "comments_turned_off": False,
            "video_id": video_id,
            "channel_id": self.YTChannelDetails.get('channel_id'),
            "video_title": "No title"
        }
        url = YTChannels.__get_video_url(self.__base_url, video_id)
        self.YTChannelDetails.update({
            "stats": video_info
        })
        try:
            self.logger.log(f"Gathering stats for **{url}**", self.get_video_stats.__name__)
            session = HTMLSession()
            response = session.get(url)

            if response.status_code != 200:
                self.logger.log(f"Response unavailable for **{url}**", self.get_video_stats.__name__,
                                self.logger.log_level_warning)
                return None

            soup_bs = bs(response.html.html, "html.parser")
            soup = str(soup_bs)
            if re.search("ytInitialData = \{(.*?)\};", soup) is None:
                self.logger.log(f"Unable to find initial data object from **{url}**", self.get_video_stats.__name__,
                                self.logger.log_level_warning)
                return None
            video_title_text = soup_bs.find("title").text
            video_info.update({"video_title": video_title_text})
            yt_initial_data = "{" + re.search("ytInitialData = \{(.*?)\};", soup).group(1) + "}"
            likes_label = comments_count = None
            if re.search("\"accessibility\":\{\"accessibilityData\":\{\"label\":\"(.*?) likes\"\}\},",
                         yt_initial_data):
                likes_object = json.loads(
                    "{" + re.search("\"accessibility\":\{\"accessibilityData\":\{\"label\":\"(.*?) likes\"\}\},",
                                    yt_initial_data).group()[0:-1] + "}")
                likes_label = likes_object["accessibility"]["accessibilityData"]["label"]
            if likes_label is not None:
                video_info["likes_count"] = likes_label[0:likes_label.index(" like")] if likes_label.find(
                    "like") != -1 else likes_label

            if soup.find("Comments are turned off.") != -1:
                self.logger.log(f"Comments are turned off on video **{url}**", self.get_video_stats.__name__,
                                self.logger.log_level_info)
                comments_count = 0
                video_info["comments_turned_off"] = True
            else:
                if re.search("\"commentCount\"\:\{\"simpleText\"\:\"(\S+)\"\},", yt_initial_data):
                    comments_text = json.loads(
                        "{" + re.search("\"commentCount\"\:\{\"simpleText\"\:\"(\S+)\"\},", yt_initial_data).group()[
                              0:-1] + "}")
                    comments_count = comments_text.get("commentCount").get("simpleText")

            if comments_count is not None:
                video_info["comments_count"] = comments_count

            self.YTChannelDetails.update({
                "stats": video_info
            })
            self.m_db_model.db_write_video_stats(video_info)
            self.sf_db_model.db_write_video_stats(video_info)
        except Exception as e:
            YTExceptions(message=f"Exception on **{url}**, **{str(e)}**", src=self.get_video_stats.__name__)

    def get_video_comments(self, video_id):
        api_key = self.conf.apiKey
        comments_max_limit = self.conf.max_comments_limit
        comments = []
        url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=id,snippet&maxResults={comments_max_limit}&videoId={video_id}&key={api_key}"
        try:
            self.logger.log(f"Fetching comments from google api.", self.get_video_comments.__name__,
                            self.logger.log_level_warning)
            response = requests.get(url)
            if response is None or response.status_code != 200 or response.content is None:
                self.logger.log(f"Unable to fetch comments from google api.", self.get_video_comments.__name__,
                                self.logger.log_level_error)
                return {
                    "status": "ERROR",
                    "Message": "Failed to load youtube video comments. Invalid response code",
                    "comments": comments
                }
            data = json.loads(response.content)
            for item in data.get('items'):
                comments.append({
                    "video_id": item['snippet']['videoId'],
                    "comment_text": item['snippet']['topLevelComment']['snippet']['textDisplay'],
                    "author_name": item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    "author_thumbnail": item['snippet']['topLevelComment']['snippet']['authorProfileImageUrl'],
                    "published_at": item['snippet']['topLevelComment']['snippet']['publishedAt'],
                    "updated_at": item['snippet']['topLevelComment']['snippet']['updatedAt']
                })
            self.logger.log(f"Fetching comments completed for video & count is **{len(comments)}**",
                            self.download_video.__name__)
            self.m_db_model.db_write_comments(comments)
            self.sf_db_model.db_write_comments(comments)
            return {
                "status": "SUCCESS",
                "Message": "OK",
                "comments": comments
            }
        except Exception as e:
            self.logger.log(f"Exception while fetching comments **{str(e)}**", self.get_video_comments.__name__,
                            self.logger.log_level_error)
            return {
                "status": "ERROR",
                "Message": "Failed to load youtube video comments",
                "comments": comments
            }

    def upload_to_s3(self, video_id):
        try:
            session = boto3.Session(
                aws_access_key_id=self.conf.aws_access_key_id,
                aws_secret_access_key=self.conf.aws_secret_access_key
            )
            yt_vid_url = YTChannels.__get_video_url(self.__base_url, video_id)
            self.logger.log(f"Uploading video to s3 **{yt_vid_url}**.", self.upload_to_s3.__name__,
                            self.logger.log_level_info)
            buffer, filename, _ = YTChannels.get_download_stream(yt_vid_url)
            s3client = session.client('s3')
            s3client.upload_fileobj(buffer, self.conf.bucket_name, filename)
            self.logger.log(f"Uploaded video to s3 **{yt_vid_url}**.", self.upload_to_s3.__name__,
                            self.logger.log_level_info)
            return True
        except Exception as e:

            self.logger.log(f"Exception while uploading video to s3 **{str(e)}**.", self.upload_to_s3.__name__,
                            self.logger.log_level_error)
            return False

    @staticmethod
    def get_download_stream(url):
        buffer = BytesIO()
        yt = pytube.YouTube(url)
        stream = yt.streams.get_by_itag(18)
        filesize = (stream.filesize / 1024)
        filename = re.sub(" ", "_", stream.default_filename)
        stream.stream_to_buffer(buffer)
        buffer.seek(0)
        return buffer, filename, filesize

    @staticmethod
    def __get_video_url(base_url, video_id):
        url = f"{base_url}/watch?v={video_id}"
        return url

    @staticmethod
    def __get_queryable_page(__url):
        channel_search_list_page = urlopen(__url)
        channels_list_page = channel_search_list_page.read().decode()
        channel_search_list_page.close()
        return channels_list_page

    @staticmethod
    def get_yt_channel_url(base_url, url, id=None):
        videos_viewby = "/videos?view=57&sort=dd&flow=grid"
        if url:
            return f"{base_url}{url}{videos_viewby}"
        elif id:
            return f'{base_url}/channel/{id}{videos_viewby}'
        else:
            return None
