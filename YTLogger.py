import logging


class YTLogger:
    log_level_debug = logging.DEBUG
    log_level_info = logging.INFO
    log_level_warning = logging.WARNING
    log_level_error = logging.ERROR

    def __init__(self, log_level=logging.INFO):
        pass
        # format = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        # logging.basicConfig(filename="app_log.log", level=log_level, format=format)

    def log(self, log: str, handler="unknown", level=log_level_debug):
        pass
        # if log is None or log.strip() == "":
        #     log = "EMPTY_MESSAGE"
        # log_dictionary = dict({"handler": handler, "log": log})
        # if level == self.log_level_error:
        #     logging.error(str(log_dictionary))
        # elif level == self.log_level_warning:
        #     logging.warning(str(log_dictionary))
        # else:
        #     logging.info(str(log_dictionary))
