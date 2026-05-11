class Config:

    SECRET_KEY = "clave_super_secreta"

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/emergency_db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False