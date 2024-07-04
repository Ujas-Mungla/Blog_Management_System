from fastapi import FastAPI, HTTPException, APIRouter, Depends, Security
from sqlalchemy.orm import Session
from typing import List
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import logging
from database.database import SessionLocal
from src.schemas.category_sch import CategoryBase,CategoryPatch
from src.models.category_mod import Category
from src.models.blog_mod import Blog
import uuid
from logs.log_config import logger


pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

Cate=APIRouter()
db=SessionLocal()





# ----------------------------------------------------------- Create_category-----------------------------------------------

@Cate.post("/Create_category/", response_model=CategoryBase)
def create_category(ct: CategoryBase):
    logger.info("Creating a new category")
    new_category = Category(
        category_id=str(uuid.uuid4()),
        category_name=ct.category_name,
        description=ct.description
    )
    db.add(new_category)
    db.commit()
    logger.success(f"Category created successfully: {new_category.category_id}")
    return new_category

# ----------------------------------------------------------- get_category-----------------------------------------------

@Cate.get("/get_category", response_model=CategoryBase)
def get_category(id: str):
    logger.info(f"Fetching category with ID: {id}")
    db_category = db.query(Category).filter(Category.category_id == id, Category.is_active == True, Category.is_deleted == False).first()
    if db_category is None:
        logger.warning(f"Category not found with ID: {id}")
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

# ----------------------------------------------------------- get_all_category-----------------------------------------------

@Cate.get("/get_all_category", response_model=list[CategoryBase])
def get_all_category():
    logger.info("Fetching all active categories")
    db_category = db.query(Category).filter(Category.is_active == True, Category.is_deleted == False).all()
    if not db_category:
        logger.warning("No categories found")
        raise HTTPException(status_code=404, detail="Categories not found")
    return db_category

# ----------------------------------------------------------- update_category_by_patch-----------------------------------------------

@Cate.patch("/update_category_by_patch", response_model=CategoryPatch)
def update_category_patch(categorys: CategoryPatch, id: str):
    logger.info(f"Patching category with ID: {id}")
    db_category = db.query(Category).filter(Category.category_id == id, Category.is_active == True, Category.is_deleted == False).first()
    if db_category is None:
        logger.warning(f"Category not found with ID: {id}")
        raise HTTPException(status_code=404, detail="Category not found")
    for field_name, value in categorys.dict().items():
        if value is not None:
            setattr(db_category, field_name, value)
    db.commit()
    logger.success(f"Category patched successfully: {id}")
    return db_category

# ----------------------------------------------------------- delete_category-----------------------------------------------

@Cate.delete("/delete_category")
def delete_category(id: str):
    logger.info(f"Deleting category with ID: {id}")
    db_category = db.query(Category).filter(Category.category_id == id, Category.is_active == True, Category.is_deleted == False).first()
    if db_category is None:
        logger.warning(f"Category not found with ID: {id}")
        raise HTTPException(status_code=404, detail="Category not found")
    db_category.is_active = False
    db_category.is_deleted = True
    db.commit()
    db.delete(db_category)
    logger.success(f"Category deleted successfully: {id}")
    return {"message": "Category deleted successfully"}


