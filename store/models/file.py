from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from store.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    path = Column(String)

    errors = relationship("Error", back_populates="file")
