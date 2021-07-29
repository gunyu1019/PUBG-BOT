import configparser

parser = configparser.ConfigParser()
parser.read("config/config.ini", encoding="utf-8")
