from snowflake import connector
from AppConfig import AppConfig
from DbModel import DbModel
from YTLogger import YTLogger
import re


def get_table_creation_scripts():
    conf = AppConfig()
    yield f"""CREATE TABLE IF NOT EXISTS {conf.tbl_name_channel_info} ( channel_id varchar(255) PRIMARY KEY,
            channel_title varchar(255),
            channel_url varchar(255),
            channel_thumbnail varchar(255),
            channel_videos_count varchar(20),
            channel_subs varchar(20))"""
    yield f"""CREATE TABLE IF NOT EXISTS {conf.tbl_name_channel_videos} ( video_id varchar(255) PRIMARY KEY,
            video_title varchar(255),
            thumbnail_url varchar(255),
            views_count varchar(20),
            published_time varchar(50),
            channel_id varchar(255))"""
    yield f"""CREATE TABLE IF NOT EXISTS {conf.tbl_name_video_stats} ( video_id varchar(255) PRIMARY KEY,
            video_title varchar(255),
            comments_count varchar(20),
            likes_count varchar(20),
            channel_id varchar(255),
            comments_turned_off varchar(10))"""
    yield f"""CREATE TABLE IF NOT EXISTS {conf.tbl_name_video_comments} ( video_id varchar(255),
            comment_text text,
            author_name varchar(255),
            author_thumbnail varchar(255),
            published_at varchar(50),
            updated_at varchar(50))"""


class SnowflakeDbModel(DbModel):
    def __init__(self):
        self.logger = YTLogger()
        self.conf = AppConfig()
        try:
            with connector.connect(**self.conf.sql_db_creds) as conn:
                cur = conn.cursor()
                cur.execute(f"CREATE DATABASE IF NOT EXISTS {self.conf.database_name}")
                cur.execute(f"USE {self.conf.database_name}")
                for create_table in get_table_creation_scripts():
                    cur.execute(create_table)
                conn.close()
        except Exception as e:
            print(e)

    def test_snowflake_connectivity(self):
        is_connection_valid = False
        with connector.connect(**self.conf.sql_db_creds) as con:
            res = con.cursor().execute("SELECT CURRENT_VERSION()")
            v, = res.fetchone()
            con.close()
            if v is not None:
                is_connection_valid = True
        return is_connection_valid

    def db_write_comments(self, records):
        columns = ""
        values = ""
        video_id = ""
        for record in records:
            video_id = record.get('video_id')
            columns, value = SnowflakeDbModel.extract_column_values(record)
            value = re.sub("\"", "'", f"{value}")
            if values == "":
                values = value
            else:
                values = values + ", " + value

        insert_statement = f"INSERT INTO {self.conf.tbl_name_video_comments} ({columns}) values {values};"
        with connector.connect(**self.conf.sql_db_creds) as conn:
            try:
                cur = conn.cursor()
                cur.execute(f"USE {self.conf.database_name}")
                if video_id != "":
                    cur.execute(f"DELETE FROM {self.conf.tbl_name_video_comments} WHERE video_id='{video_id}';")
                cur.execute(insert_statement)
                if cur.rowcount > 0:
                    self.logger.log(
                        f"Successfully inserted, {cur.rowcount} records to {self.conf.tbl_name_video_comments}")
                else:
                    self.logger.log(f"Failed to insert at {self.conf.tbl_name_video_comments}",
                                    self.logger.log_level_error)
                cur.close()
            except Exception as e:
                self.logger.log(f"SF_Exception while writing to **{self.db_write_comments.__name__}** **{str(e)}**",
                                self.logger.log_level_error)
            finally:
                if cur is not None:
                    cur.close()

    def db_write_channel_info(self, record):
        columns, values = SnowflakeDbModel.extract_column_values(record)
        insert_statement = f"INSERT INTO {self.conf.tbl_name_channel_info} ({columns}) values {values};"
        try:
            with connector.connect(**self.conf.sql_db_creds) as conn:
                try:
                    cur = conn.cursor()
                    cur.execute(f"USE {self.conf.database_name}")
                    cur.execute(
                        f"DELETE FROM {self.conf.tbl_name_channel_info} WHERE CHANNEL_ID='{record.get('channel_id')}'")
                    cur.execute(insert_statement)
                    if cur.rowcount > 0:
                        self.logger.log(
                            f"Successfully inserted, {cur.rowcount} records to {self.conf.tbl_name_channel_info}")
                    else:
                        self.logger.log(f"Failed to insert at {self.conf.tbl_name_channel_info}",
                                        self.logger.log_level_error)
                    cur.close()
                except Exception as e:
                    self.logger.log(f"SF_Exception while writing to **{self.db_write_channel_info.__name__}** **{str(e)}**",
                                    self.logger.log_level_error)
                finally:
                    if cur is not None:
                        cur.close()
        except Exception as e:
            print(e)

    def db_write_video_stats(self, record):
        columns, values = SnowflakeDbModel.extract_column_values(record)
        insert_statement = f"INSERT INTO {self.conf.tbl_name_video_stats} ({columns}) values {values};"
        try:
            with connector.connect(**self.conf.sql_db_creds) as conn:
                try:
                    cur = conn.cursor()
                    cur.execute(f"USE {self.conf.database_name}")
                    cur.execute(
                        f"DELETE FROM {self.conf.tbl_name_video_stats} WHERE VIDEO_ID='{record.get('video_id')}'")
                    cur.execute(insert_statement)
                    if cur.rowcount > 0:
                        self.logger.log(
                            f"Successfully inserted, {cur.rowcount} records to {self.conf.tbl_name_video_stats}")
                    else:
                        self.logger.log(f"Failed to insert at {self.conf.tbl_name_video_stats}",
                                        self.logger.log_level_error)
                    cur.close()
                except Exception as e:
                    self.logger.log(
                        f"SF_Exception while writing to **{self.db_write_video_stats.__name__}** **{str(e)}**",
                        self.logger.log_level_error)
                finally:
                    if cur is not None:
                        cur.close()
        except Exception as e:
            print(e)

    def db_write_videos(self, records):
        columns = ""
        values = ""
        channel_id = ""
        for record in records:
            channel_id = record.get('channel_id')
            columns, value = SnowflakeDbModel.extract_column_values(record)
            value = re.sub("\"", "'", f"{value}")
            if values == "":
                values = value
            else:
                values = values + ", " + value

        insert_statement = f"INSERT INTO {self.conf.tbl_name_channel_videos} ({columns}) values {values};"
        try:
            with connector.connect(**self.conf.sql_db_creds) as conn:
                try:
                    cur = conn.cursor()
                    cur.execute(f"USE {self.conf.database_name}")
                    if channel_id != "":
                        cur.execute(f"DELETE FROM {self.conf.tbl_name_channel_videos} where channel_id = '{channel_id}'")
                    cur.execute(insert_statement)
                    if cur.rowcount > 0:
                        self.logger.log(
                            f"Successfully inserted, {cur.rowcount} records to {self.conf.tbl_name_channel_videos}")
                    else:
                        self.logger.log(f"Failed to insert at {self.conf.tbl_name_video_stats}",
                                        self.logger.log_level_error)
                    cur.close()
                except Exception as e:
                    self.logger.log(f"SF_Exception while writing to **{self.db_write_videos.__name__}** **{str(e)}**",
                                    self.logger.log_level_error)
        except Exception as e:
            print(e)

    @staticmethod
    def extract_column_values(record: dict):
        columns, values = "", []
        for key, value in record.items():
            if columns == "":
                columns = key
            else:
                columns = columns + ", " + key.capitalize()
            if type(value) == str:
                values.append(re.sub('\'', '', value))
            else:
                values.append(str(value))
        return columns, tuple(values)
