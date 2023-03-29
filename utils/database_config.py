from config.config import get_config

parser = get_config()
database_section = parser.get("Default", "database")
database = {
    "username": parser.get(database_section, "user"),
    "host": parser.get(database_section, "host"),
    "password": parser.get(database_section, "pass"),
    "database": parser.get(database_section, "database"),
    "port": parser.getint(database_section, "port", fallback=3306),
}
database_url = "mysql+aiomysql://{username}:{password}@{host}:{port}/{database}".format(
    **database
)
