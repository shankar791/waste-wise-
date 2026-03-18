from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from datetime import date

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")
    
    waste_logs = relationship("WasteLog", back_populates="account")
    reports = relationship("Report", back_populates="account")

class WasteLog(Base):
    __tablename__ = "waste_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, ForeignKey("accounts.email"), index=True)
    waste_type = Column(String, index=True)
    subcategory = Column(String)
    weight = Column(Float)            # Added: Save the uploaded weight
    image_url = Column(String)        # Added: Save the image path
    carbon = Column(Float)
    points = Column(Integer)
    date = Column(String, index=True) # Text date YYYY-MM-DD
    
    account = relationship("Account", back_populates="waste_logs")

class Reward(Base):
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    points_required = Column(Integer)

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    locality = Column(String)

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, ForeignKey("accounts.email"), index=True)
    message = Column(String)
    target = Column(String)
    
    account = relationship("Account", back_populates="reports")
