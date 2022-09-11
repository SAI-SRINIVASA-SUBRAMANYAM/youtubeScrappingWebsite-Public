from pymongo import MongoClient
from AppConfig import AppConfig
from YTLogger import YTLogger
from DbModel import DbModel
import copy


class MongoDbModel(DbModel):

    def __init__(self):
        self.__conf = AppConfig()
        mdb_conn_str = f"mongodb+srv://vasu:{self.__conf.mongo_db_secret_key}@cluster0.34cpv.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(mdb_conn_str)
        self.__db = client[self.__conf.database_name]
        self.__logger = YTLogger()

    def db_write_videos(self, records: list):
        documents = copy.deepcopy(list(map(lambda x: copy.deepcopy(x), records)))
        self.__logger.log(f"Writing to mongodb collection **{self.__conf.tbl_name_channel_videos}**",
                          self.__logger.log_level_info)
        try:
            collection = self.__db[self.__conf.tbl_name_channel_videos]
            response = collection.insert_many(documents)
            self.__logger.log(f"Successfully inserted at **{self.__conf.tbl_name_channel_videos}**",
                              self.__logger.log_level_info)
            return response.inserted_ids
        except Exception as e:
            self.__logger.log(f"Failed to insert to **{self.__conf.tbl_name_channel_videos}** **{str(e)}**",
                              self.__logger.log_level_error)

    def db_write_video_stats(self, record):
        self.__logger.log(f"Writing to mongodb collection **{self.__conf.tbl_name_video_stats}**",
                          self.__logger.log_level_info)
        document = copy.deepcopy(record)
        try:
            collection = self.__db[self.__conf.tbl_name_video_stats]
            response = collection.insert_one(document)
            self.__logger.log(f"Successfully inserted at **{self.__conf.tbl_name_video_stats}**",
                              self.__logger.log_level_info)
            return response.inserted_id
        except Exception as e:
            self.__logger.log(f"Failed to insert to **{self.__conf.tbl_name_video_stats}** **{str(e)}**",
                              self.__logger.log_level_error)

    def db_write_channel_info(self, record):
        self.__logger.log(f"Writing to mongodb collection **{self.__conf.tbl_name_channel_info}**",
                          self.__logger.log_level_info)
        document = copy.deepcopy(record)
        try:
            collection = self.__db[self.__conf.tbl_name_channel_info]
            response = collection.insert_one(document)
            self.__logger.log(f"Successfully inserted at **{self.__conf.tbl_name_channel_info}**",
                              self.__logger.log_level_info)
            return response.inserted_id
        except Exception as e:
            self.__logger.log(f"Failed to insert to **{self.__conf.tbl_name_channel_info}** **{str(e)}**",
                              self.__logger.log_level_error)

    def db_write_comments(self, records):
        documents = copy.deepcopy(list(map(lambda x: copy.deepcopy(x), records)))
        self.__logger.log(f"Writing to mongodb collection **{self.__conf.tbl_name_video_comments}**",
                          self.__logger.log_level_info)
        try:
            collection = self.__db[self.__conf.tbl_name_video_comments]
            response = collection.insert_many(documents)
            self.__logger.log(f"Successfully inserted at **{self.__conf.tbl_name_video_comments}**",
                              self.__logger.log_level_info)
            return response.inserted_ids
        except Exception as e:
            self.__logger.log(f"Failed to insert to **{self.__conf.tbl_name_video_comments}** **{str(e)}**",
                              self.__logger.log_level_error)
