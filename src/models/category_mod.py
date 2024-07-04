from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, JSON,Text
import uuid
from database.database import Base
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship



class Category(Base):

    __tablename__ = "categories"
    category_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_deleted=Column(Boolean,default=False)
    is_active=Column(Boolean,default=True)
    created_at=Column(DateTime,default=datetime.now) 
    modified_at = Column(DateTime,default=datetime.now,onupdate=datetime.now) 

