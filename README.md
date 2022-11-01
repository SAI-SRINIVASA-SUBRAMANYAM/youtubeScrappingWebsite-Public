# youtubeScrappingWebsite-Public
Developed project with intention of understanding of web scrapping, flask-api integration, talking to 3rd google api.

This project provides an overview of how to implement Webscrapping using python.

**Introduction of Webscrapping:** Web scrapping is extracting data from a website and creating our own analysis on it.

<ul>
<li>app.py is the core api layer which accepts request and return a response/download/upload a file</li>
  <li>Operations:
    <ul>
      <li>"/" : Redirects to home screen</li>
      <li>"/channel" : Redirects to the searched channel</li>
      <li>"/channel/videos" : Redirects to the channel videos</li>
      <li>"/channel/video/comments" : Redirects to the channel, video comments</li>
      <li>"/channel/video/download" : Downloads the channel video</li>
      <li>"/channel/video/s3upload" : Uploads to the S3 bucket</li>
    </ul>
  </li>
  <li>AppConfig.py is the application related configuration information</li>
  <li>DbModel.py, MongoDbModel.py, SnowflakeDbModel.py are the database related connection setting and CRUD operations</li>
  <li>YTChannels.py is the core file which handle to extraction process from YouTube, upload to s3, save to database.</li>
  <li>YTExceptions.py, YTLogger.py are exception handling and logging files</li>
  <li>conf.ini application configuration information</li>
  <li>generate_secrets.py is the secrets generation file</li>
  <li>requirements.txt is the application package related information file</li>
</ul>

<h2>Libraries used<h2>
<ul>
<li>requests==2.27.1</li>
<li>beautifulsoup4==4.11.1</li>
<li>requests</li>
<li>mysql-connector-python</li>
<li>flask</li>
<li>requests_html</li>
<li>pytube</li>
<li>pybase64</li>
<li>boto3</li>
<li>cryptography</li>
<li>pymongo</li>
<li>pymongo[srv]</li>
<li>snowflake-connector-python</li>
<li>gunicorn==20.0.4</li>
</ul>
