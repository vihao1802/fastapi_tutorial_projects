from sqlmodel import SQLModel, Session, create_engine

sqlite_file_name = "blog.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_agrs = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_agrs)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
