from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from store.database import Base


class Error(Base):
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True)
    message = Column(String)

    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    file = relationship("File", back_populates="errors")
