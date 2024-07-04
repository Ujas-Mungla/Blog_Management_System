from pydantic import BaseModel,EmailStr,constr,Json,Field
from typing import List,Optional
from datetime import datetime,date

class UserBase(BaseModel):
    username: str
    email: str
    bio: Optional[str] = None

class UserCreate(BaseModel):
    first_name:str
    last_name:str
    password: str



class Users(BaseModel):
   
    first_name :str
    last_name :str
    username :str
    email :str
    mobile_no :str  
    password :str   
    bio :str
    role :str
    address :str

class UserUpdate(BaseModel):
    username:str
    password:str

class UsersPatch(BaseModel):
    first_name :Optional[str]=None
    last_name :Optional[str]=None
    username :Optional[str]=None
    email :Optional[str]=None
    mobile_no :Optional[str]=None
    password :Optional[str]=None
    bio :Optional[str]=None
    role :Optional[str]=None
    address :Optional[str]=None



class OTPRequest(BaseModel):
    email: EmailStr
class OTPVerify(BaseModel):
    email: EmailStr
    otp: str



class FollowerFollowingResponse(BaseModel):
    user_id: str
    usernames: List[str]


class ActionResponse(BaseModel):
    detail: str
    


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
    


class CategoryBase(BaseModel):
    category_name: str
    description: str 



class CategoryPatch(BaseModel):
    category_name: Optional[str] =None
    description: Optional[str] =None 




# class CommentCreate(BaseModel):
#     blog_id: str
#     user_id: str
#     content: str

# class CommentResponse(BaseModel):
#     comment_id: str
#     blog_id: str
#     user_id: str
#     content: str
#     created_at: datetime
#     modified_at: datetime

