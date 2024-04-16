from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# sqlalchemy.url = mariadb+mariadbconnector://root:hoseo2019@database-1.c7ksqskkcyxy.ap-northeast-2.rds.amazonaws.com:3306/ALB
# sqlalchemy.url = mariadb+mariadbconnector://root:root@127.0.0.1:3306/autolook

SQLALCHEMY_DATABASE_URL = "mariadb+mariadbconnector://root:root@127.0.0.1:3306/autolook"
# SQLALCHEMY_DATABASE_URL = "mariadb+mariadbconnector://root:hoseo2019@database-1.c7ksqskkcyxy.ap-northeast-2.rds.amazonaws.com:3306/ALB"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)


Base = declarative_base()
naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
Base.metadata = MetaData(naming_convention = naming_convention)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
