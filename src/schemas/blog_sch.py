from pydantic import BaseModel,EmailStr,constr,Json,Field
from typing import List,Optional
from datetime import datetime,date

 


class BlogBase(BaseModel):
    user_id:str
    title :str
    content :str
    category_id:str

    
   

class Blog_Patch(BaseModel):
    user_id:Optional [str] = None
    title :Optional [str] = None
    content :Optional [str] = None
    category_id:Optional [str] = None
    comments: Optional[List[dict]] = Field(default_factory=list)
    
    
class BlogResponse(BlogBase):
    blog_id: str
    user_id: str
    created_at: datetime
    modified_at: datetime

class BlogInDB(BlogBase):
  title :str
  content :str
    

class BlogWithLikes(BlogBase):
    blog_id: str
    likes: List[str] = Field(default_factory=list)  # List of user_ids who liked the blog
    created_at: datetime
    modified_at: datetime


class Commenttt(BaseModel):
    token:str
    comment:str
    blogs_id:str


class BlogRating(BaseModel):
    ratings_count: int
    total_rating: float
    average_rating: float

class BlogInDB(BlogBase, BlogRating):
    blog_id: str

class Rating(BaseModel):
    rating: float