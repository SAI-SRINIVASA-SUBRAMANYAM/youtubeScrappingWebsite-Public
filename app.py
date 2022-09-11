import re
from flask import Flask, send_file, request, render_template, make_response
from YTChannels import YTChannels

app = Flask(__name__)
yt_channel = YTChannels()


@app.route("/", methods=["GET"])
def home():
    return render_template(
        'search_channel.html',
        title="Home - YT Scrapping",
        breadcrum="/"
    )


@app.route("/channel", methods=["POST"])
def get_channel_info():
    search_string = request.form.get('searchString')
    search_string = re.sub(" ", "+", search_string)
    yt_channel.get_channel_info(search_string)
    channel_info = yt_channel.YTChannelDetails.get('channel_info')
    return render_template(
        'channel_info.html',
        title=f"Channel - {channel_info.get('channel_title')}",
        channel_info=channel_info,
        breadcrum=f"/{channel_info.get('channel_title')}"
    )


@app.route("/channel/videos", methods=["GET"])
def get_channel_videos():
    yt_channel_details = yt_channel.YTChannelDetails
    channel_info = yt_channel_details.get('channel_info')
    yt_channel.get_videos_by_channel(channel_info.get('channel_url'))
    return render_template(
        'channel_videos.html',
        title=f"Videos - {channel_info.get('channel_title')}",
        channel_videos=yt_channel_details.get('videos'),
        breadcrum=f"/{channel_info.get('channel_title')}/videos"
    )


@app.route("/channel/video/comments", methods=["GET"])
def get_video_comments():
    video_id = request.args.get('video_id')
    yt_channel.get_video_stats(video_id)
    yt_channel_details = yt_channel.YTChannelDetails
    if yt_channel_details.get('stats').get('comments_turned_off') == False:
        comments = yt_channel.get_video_comments(video_id).get('comments')
    else:
        comments = []

    return render_template(
        'video_comments.html',
        title=f"Comments - {yt_channel_details.get('channel_info').get('channel_title')}",
        comments=comments,
        video_title=yt_channel_details.get('stats').get('video_title'),
        video_id=video_id,
        stats=yt_channel_details.get('stats'),
        breadcrum=f"/{yt_channel_details.get('channel_info').get('channel_title')}/video/comments"
    )


@app.route("/channel/video/download", methods=["GET"])
def get_video_file():
    video_id = request.args.get('video_id')
    buffer, filename = yt_channel.download_video(video_id)
    return send_file(
        buffer,
        as_attachment=True,
        mimetype="video/mp4",
        download_name=filename,
        etag=filename
    )


@app.route("/channel/video/s3upload", methods=["POST"])
def upload_to_s3():
    video_id = request.json.get('video_id')
    response = yt_channel.upload_to_s3(video_id)
    return make_response({"isUploaded": response})


@app.errorhandler(404)
def error_page(e):
    return render_template(
        'error.html',
        exception_type="Page not found",
        exception_title=str(e),
        exception_message="Sorry, an error has occurred, Requested page not found!",
        breadcrum=f"/Error"
    )


@app.errorhandler(500)
def error_page(e):
    return render_template(
        'error.html',
        exception_type="Internal server error",
        exception_title=str(e),
        exception_message="Sorry, an internal error has occurred, try again!",
        breadcrum=f"/Error"
    )


@app.errorhandler(405)
def error_page(e):
    return render_template(
        'error.html',
        exception_type="Method not found",
        exception_title=str(e),
        exception_message="Sorry, an invalid request method, contact support team for additional assistance",
        breadcrum=f"/Error"
    )


if __name__ == "__main__":
    app.run()
