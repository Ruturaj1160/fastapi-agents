from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///rangmanch.db"

engine = create_engine(DATABASE_URL, echo=True)


def create_tables():
    """create tables defined by SQLModel class"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency injection"""
    with Session(engine) as session:
        yield session
