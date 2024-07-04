from pydantic import BaseModel,EmailStr,constr,Json,Field
from typing import List,Optional
from datetime import datetime,date



class CategoryBase(BaseModel):
    category_name: str
    description: str 



class CategoryPatch(BaseModel):
    category_name: Optional[str] =None
    description: Optional[str] =None 

