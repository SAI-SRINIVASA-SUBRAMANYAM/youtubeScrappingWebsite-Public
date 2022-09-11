from cryptography.fernet import Fernet
import configparser
from AppConfig import get_secret_key


class GenerateSecrets:

    def __init__(self):
        GenerateSecrets.generate_shhh()
        config = configparser.ConfigParser()
        section = 'app_settings'
        config.add_section(section)
        config.set(section, 'yt_api_key', GenerateSecrets.get_yt_api())
        config.set(section, 'aws_access_key_id', "<<aws_access_id>>")
        config.set(section, 'secret_access_key', GenerateSecrets.get_aws_secret_access())
        config.set(section, 'mongo_db_secret_key', GenerateSecrets.get_mongo_db_psswd())
        config.set(section, 'sql_db_secret_key', GenerateSecrets.get_sql_db_psswd())
        with open(r'conf.ini', 'w') as fp:
            config.write(fp)

    @staticmethod
    def get_yt_api():
        f = get_secret_key()
        return f.encrypt("<<google_api>>".encode()).decode()

    @staticmethod
    def get_aws_secret_access():
        f = get_secret_key()
        return f.encrypt("<<aws_secret_access>>".encode()).decode()

    @staticmethod
    def get_mongo_db_psswd():
        f = get_secret_key()
        return f.encrypt("<<mongodb_password>>".encode()).decode()

    @staticmethod
    def get_sql_db_psswd():
        f = get_secret_key()
        return f.encrypt('<<sf_password>>'.encode()).decode()

    @staticmethod
    def generate_shhh():
        with open('.shhhh', 'w') as fp:
            key = Fernet.generate_key()
            fp.write(key.decode())


if __name__ == "__main__":
    GenerateSecrets()
