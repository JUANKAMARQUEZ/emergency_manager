import os


class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "Kj82nX!pQw93Lm#Tz71AaBcD"
    )

    database_url = os.environ.get(
        "DATABASE_URL"
    )

    if database_url:

        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    SQLALCHEMY_DATABASE_URI = (
        database_url
        or "mysql+pymysql://root:@localhost/emergency_db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False