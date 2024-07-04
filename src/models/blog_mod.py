from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, JSON,Text,Float
import uuid
from database.database import Base
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship




class Blog(Base):
    __tablename__ = "blogs"
    blog_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    category_id = Column(String(50), ForeignKey('categories.category_id'), nullable=False)
    comments = Column(JSON)
    like = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user = relationship("User")
    category = relationship("Category")
    is_deleted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    ratings_count = Column(Integer, default=0)
    total_rating = Column(Float, default=0.0)
    average_rating = Column(Float, default=0.0)





