from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, LargeBinary
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
    full_name = Column(String, nullable=True)
    profile_picture_url = Column(String, nullable=True)
    
    waste_logs = relationship("WasteLog", back_populates="account")
    reports = relationship("Report", back_populates="account")

class WasteLog(Base):
    __tablename__ = "waste_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, ForeignKey("accounts.email"), index=True)
    waste_type = Column(String, index=True)
    subcategory = Column(String, nullable=True)
    item_name = Column(String, nullable=True)
    
    predicted_label = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    classification_source = Column(String, default="fallback") # ai_model or fallback
    
    weight = Column(Float)            
    image_url = Column(String, nullable=True)        
    image_data = Column(LargeBinary, nullable=True)  
    carbon = Column(Float)
    points = Column(Integer)
    date = Column(String, index=True) 
    
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
