from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mariadb+mariadbconnector://root:root@127.0.0.1:3306/autolook"


# db랑 연결
# 회원을 저장하는 용도의 데이터 베이스를 만듬
# 회원이 만들어지면 회뭔의 고유키를 만들들어서 그것을 이름으로하는 데이터베이스를 만든다
# 만들어진 데이터 베이스의 아이디와 닉네임을 이용하여 로그인하고
# 데이터 저장 삭제 조회
# 코드 다시 짜야하네


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
