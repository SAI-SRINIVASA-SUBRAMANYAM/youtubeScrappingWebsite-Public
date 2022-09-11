from pyyoutube import Api
from YTExceptions import YTExceptions
import requests
import json
import re
from AppConfig import AppConfig

SEARCH_CHANNEL_TITLE = "telusko"
VIDEOS_LIMIT = 50

conf = AppConfig()
api = Api(api_key=conf.apiKey)
res = api.search_by_keywords(q="telusko", search_type=["channel"], count=5, limit=5)

channel_details = {
    "id": None,
    "title": None,
    "description": None
}

for item in res.items:
    channel_info = item.to_dict()
    MATCH_FOUND = False

    if channel_info.get("snippet") and channel_info.get("snippet").get("title"):
        if re.match(SEARCH_CHANNEL_TITLE, channel_info.get("snippet").get("title"), re.IGNORECASE):
            MATCH_FOUND = True

    if MATCH_FOUND:
        if channel_info.get("snippet").get("title"):
            channel_details.update({"title": channel_info.get("snippet").get("title")})
        if channel_info.get("snippet").get("description"):
            channel_details.update({"description": channel_info.get("snippet").get("description")})
        if channel_info.get("id") and channel_info.get("id").get("channelId"):
            channel_details.update({"id": channel_info.get("id").get("channelId")})
        break

# print(channel_details)
if not channel_details.get('id'):
    YTExceptions(message="Channel not found", src="GET_CHANNEL")

channel_videos = "https://www.googleapis.com/youtube/v3/search?key={apiKey}&channelId={channelId}&part=snippet,id&order=date&maxResults={videosLimit}"
channel_videos = channel_videos.format(apiKey=conf.apiKey, channelId=channel_details.get('id'),
                                       videosLimit=VIDEOS_LIMIT)
print(channel_videos)
result = requests.get(channel_videos)
# print(result.content, "\n", result.status_code)
if result.status_code is None or result.status_code != 200 or result.content is None:
    YTExceptions(message="Invalid response", src="VALIDATE_RESPONSE")
data = json.loads(result.content)
print(data)
if data.get("items") is None:
    YTExceptions(message=f"No video on this channel {channel_details.get('title')}",
                 src="VALIDATE_VIDEOS")

video_details = []

for index, item in enumerate(data.get("items")):
    width = item.get("snippet").get("thumbnails").get("high").get("width")
    height = item.get("snippet").get("thumbnails").get("high").get("height")
    video_info = {
        "id": item.get("id").get("videoId"),
        "title": item.get("snippet").get("title"),
        "description": item.get("snippet").get("description"),
        "thumbnail": item.get("snippet").get("thumbnails").get("high").get("url"),
        "publishedAt": item.get("snippet").get("publishedAt"),
        "w_h": f"{width}_{height}"
    }
    video_details.append(video_info)

print("total:", len(video_details))
print(video_details)
for video in video_details:
    if video.get("id") == "4auwnxsEDeI":
        print(video)
# print(filter(video_details, lambda x: True if x.get("id") == "4auwnxsEDeI" else False))
SpecificVideoUrl = 'https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics&id=' + "4auwnxsEDeI" + '&key=' + conf.apiKey
print(SpecificVideoUrl)
video_content_details = requests.get(SpecificVideoUrl)

print(video_content_details.content)
