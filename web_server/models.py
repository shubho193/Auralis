from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))

    history = relationship("MixHistory", back_populates="user")

class MixHistory(Base):
    __tablename__ = "mix_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    output_filename = Column(String(255))
    logs = Column(Text)
    settings_summary = Column(String(500)) # e.g. "4 stems, Auto-Gain: On"

    user = relationship("User", back_populates="history")
