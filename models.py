import os
from sqlalchemy import create_engine, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, relationship, mapped_column, Mapped
import datetime
from atexit import register


POSTGRES_USER = os.getenv('POSTGRES_USER', '')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
POSTGRES_DB = os.getenv('POSTGRES_DB', '')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5435')

PG_DSN = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Advertisment(Base):
    __tablename__ = 'advertisments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    date_created: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='advertisments')

    @property
    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date_created': self.date_created.isoformat(),
            'user': self.user.name,
        }


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(70), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(70), nullable=False)
    advertisments = relationship('Advertisment', back_populates='user', cascade='all, delete-orphan')

    @property
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
        }


Base.metadata.create_all(bind=engine)

register(engine.dispose)
