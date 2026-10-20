from sqlalchemy import Column, Integer, String
from database import Base


class ImageModel(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    size = Column(String)

    width = Column(Integer)

    height = Column(Integer)

    type = Column(String)

    created_at = Column(String)

    path = Column(String)