import re
import json
import sys
from urllib.request import urlopen

BASE_URL = "https://www.youtube.com/results?search_query={channel_name}&sp=EgIQAg"
channel_name = "telusko"

_search_channel_url = BASE_URL.format(channel_name=channel_name)

channel_search_list_page = urlopen(_search_channel_url)
channels_list_page = channel_search_list_page.read().decode()
channel_search_list_page.close()

re1 = re.compile(r'\"url\":"\/c\/\S+",\"webPageType\":\"WEB_PAGE_TYPE_CHANNEL\"')
channel_info = {
    "url": None,
    "id": None
}
# print(channels_list_page)
for srch_res in re1.findall(channels_list_page):
    start_pos = srch_res.find("/c/")
    end_pos = srch_res.find("\",")
    if start_pos != -1 and end_pos != -1:
        channel_url = srch_res[start_pos:end_pos]
        search_template = "\"browseEndpoint\"(.*?)\"canonicalBaseUrl\":\"{cUrl}\""
        search_template = search_template.format(cUrl=channel_url)
        channel_search_text = re.compile(search_template)
        temp = re.search(channel_search_text, channels_list_page).group(1)[1:-2]
        channel_id = json.loads(temp+"\"}").get("browseId")
        channel_info.update({"url": channel_url, "id": channel_id})
        break

if channel_info.get("url") is None:
    sys.exit("Invalid url")

yt_channel_url = "https://www.youtube.com/{channel_url}/videos?view=57&sort=dd&flow=grid"
yt_channel_url = yt_channel_url.format(channel_url=channel_info.get("url"))
# print(yt_channel_url)

yt_selected_channel_page = urlopen(yt_channel_url).read().decode()

re2 = re.compile("\"videoId\":\"(\S+)\",\"thumbnail\"")
selected_channel_videos_list = []
for c in re2.findall(yt_selected_channel_page):
    search_text = "videoId\":\"{c}\"(.*?)watchEndpoint\":(.*?)\"videoId\":\"{c}\""
    # print(search_text.format(c=c))
    search_text = search_text.format(c=c)

    youtube_video_info = {
        "thumbnail_url": None,
        "views_count": None,
        "youtube_title": None,
        "video_url": None
    }

    f = re.search(search_text, yt_selected_channel_page)
    if f:
        json_text2 = "{" + f.group(1)[1:-2] + "}}"
        json_dict = json.loads(json_text2)
        thumbnail_url = json_dict.get("thumbnail").get("thumbnails")[0]["url"]
        youtube_title = json_dict.get("title").get("runs")[0]["text"]
        views_count = json_dict.get("viewCountText").get("simpleText")
        views_count = re.sub("\D", "", views_count)
        video_url = json_dict.get("navigationEndpoint").get("commandMetadata").get("webCommandMetadata").get('url')
        selected_channel_videos_list.append({
            "thumbnail_url": thumbnail_url,
            "youtube_title": youtube_title,
            "views_count": views_count,
            "video_url": video_url
        })
# print(selected_channel_videos_list, len(selected_channel_videos_list), sep="\n")