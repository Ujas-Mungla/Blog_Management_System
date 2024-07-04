from fastapi import FastAPI,HTTPException,APIRouter,Depends,Header
from database.database import SessionLocal
from src.models.blog_mod import Blog
from src.models.user_mod import User
from src.models.category_mod import Category
from src.schemas.blog_sch import BlogResponse,Blog_Patch,BlogBase,BlogInDB,BlogBase,BlogWithLikes,Commenttt,BlogRating,BlogInDB,Rating
import uuid
from passlib.context import CryptContext
from typing import List
from src.utils.token import decode_token_user_id
import logging
from logs.log_config     import logger



pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

blogger=APIRouter()
db=SessionLocal()

# -----------------------------------------------------Create_blog------------------------------------------------------------------------

@blogger.post("/Create_blog/", response_model=BlogBase)
def Create_Blog(blg: BlogBase):
    logger.info("Creating a new blog")
    new_blog = Blog(
        user_id=blg.user_id,
        title=blg.title,
        content=blg.content,
        category_id=blg.category_id,
        comments={},
        likes=[]
    )

    db.add(new_blog)
    db.commit()
    logger.success("Blog created successfully")
    return new_blog

# ------------------------------------------------------------get_blog_by_id----------------------------------------------------------------

@blogger.get("/get_blog_by_id/{blog_id}", response_model=BlogBase)
def get_blog_by_id(blog_id: str):
    logger.info(f"Fetching blog with ID: {blog_id}")
    db_blog = db.query(Blog).filter(Blog.blog_id == blog_id, Blog.is_active == True).first()
    if not db_blog:
        logger.warning(f"Blog not found with ID: {blog_id}")
        raise HTTPException(status_code=404, detail="Blog Not Found")
    return db_blog

# -------------------------------------------------------get_all_blog----------------------------------------------------------------

@blogger.get("/get_all_blog", response_model=List[BlogBase])
def get_all_blog():
    logger.info("Fetching all active blogs")
    db_blog = db.query(Blog).filter(Blog.is_active == True).all()
    if db_blog is None:
        logger.warning("No blogs found")
        raise HTTPException(status_code=404, detail="Blogs Not Found")
    return db_blog

# --------------------------------------------------Update_blog_-----------------------------------------------------------------

@blogger.put("/Update_blog_{blog_id}")
def update_blog(blg: BlogBase, blog_id: str):
    logger.info(f"Updating blog with ID: {blog_id}")
    db_blog = db.query(Blog).filter(Blog.blog_id == blog_id, Blog.is_active == True).first()
    if db_blog is None:
        logger.warning(f"Blog not found with ID: {blog_id}")
        raise HTTPException(status_code=404, detail="Blog Not Found")

    db_user = db.query(User).filter(User.id == blg.user_id).first()
    if db_user is None:
        logger.warning(f"User not found with ID: {blg.user_id}")
        raise HTTPException(status_code=404, detail="User Not Found")

    db_category = db.query(Category).filter(Category.category_id == blg.category_id).first()
    if db_category is None:
        logger.warning(f"Category not found with ID: {blg.category_id}")
        raise HTTPException(status_code=404, detail="Category Not Found")

    db_blog.user_id = blg.user_id
    db_blog.title = blg.title
    db_blog.content = blg.content
    db_blog.category_id = blg.category_id
    db.commit()
    db.refresh(db_blog)
    logger.success(f"Blog updated successfully with ID: {blog_id}")
    return "Your detail changed successfully"

# ------------------------------------------------blog_reregister--------------------------------------------------------------------------

@blogger.put("/blog/{blog_id}/reregister")
def reregister_blog(blog_id: str):
    logger.info(f"Reregistering blog with ID: {blog_id}")
    db_blog = db.query(Blog).filter(Blog.blog_id == blog_id).first()
    
    if db_blog is None:
        logger.warning(f"Blog not found with ID: {blog_id}")
        raise HTTPException(status_code=404, detail="Blog not found")
    
    if db_blog.is_deleted is True and db_blog.is_active is False:
        db_blog.is_deleted = False
        db_blog.is_active = True
        db.commit()
        db.refresh(db_blog)
        logger.info(f"Blog reregistered successfully with ID: {blog_id}")
        return {"message": "Blog re-registered successfully"}
    
    logger.warning(f"Blog with ID: {blog_id} cannot be re-registered")
    raise HTTPException(status_code=401, detail="Blog cannot be re-registered")

# -------------------------------------------------update_employee_patch----------------------------------------------------------

@blogger.patch("/update_employee_patch/{blog_id}")
def update_employee_patch(blog_id: str, blg: Blog_Patch):
    logger.info(f"Patching blog with ID: {blog_id}")
    find_blog = db.query(Blog).filter(Blog.blog_id == blog_id, Blog.is_active == True).first()
    if find_blog is None:
        logger.warning(f"Blog not found with ID: {blog_id}")
        raise HTTPException(status_code=404, detail="Blog Not Found")
    
    update_data = blg.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(find_blog, key, value)
    db.commit()
    db.refresh(find_blog)
    logger.success(f"Blog patched successfully with ID: {blog_id}")
    return {"message": "Details changed successfully", "Blog": find_blog}

# ---------------------------------------------delete_blog---------------------------------------------------------------

@blogger.delete("/delete_blog/")
def delete_blog(blog_id: str):
    logger.info(f"Deleting blog with ID: {blog_id}")
    db_blog = db.query(Blog).filter(Blog.blog_id == blog_id, Blog.is_active == True).first()
    if db_blog is None:
        logger.warning(f"Blog not found with ID: {blog_id}")
        raise HTTPException(status_code=404, detail="Blog Not Found")
    db_blog.is_active = False
    db_blog.is_deleted = True
    db.delete(db_blog)
    db.commit()
    logger.success(f"Blog deleted successfully with ID: {blog_id}")
    return "Blog Deleted Successfully"

# ------------------------------------------------------------get_blogs_by_category----------------------------------------------------

@blogger.get("/get_blogs_by_category/{category_id}", response_model=list[BlogInDB])
def get_blog_by_category(category_id: str):
    logger.info(f"Fetching blogs for category ID: {category_id}")
    blogs = db.query(Blog).filter(Blog.category_id == category_id).all()
    if not blogs:
        logger.warning(f"No blogs found for category ID: {category_id}")
        raise HTTPException(status_code=404, detail="No blogs found for this category")
    return blogs




# ------------------------------------------------------------like_blog----------------------------------------------------


@blogger.post("/like_blog")
def like_post(blog_id: str, token: str = Header(...)):
    logger.info(f"Liking blog with ID: {blog_id}")
    db_user_id = decode_token_user_id(token)
    db_user = db.query(User).filter(User.id == db_user_id, User.is_active == True, User.is_deleted == False, User.is_verified == True).first()
    if db_user is None:
        logger.warning(f"User not found with ID from token")
        raise HTTPException(status_code=404, detail="User not found")

    db_blog = db.query(Blog).filter(Blog.blog_id == blog_id, Blog.is_active == True, Blog.is_deleted == False).first()
    if db_blog is None:
        logger.warning(f"Blog not found with ID: {blog_id}")
        raise HTTPException(status_code=404, detail="Blog not found")

    if db_user_id in db_blog.like:
        logger.warning(f"User {db_user_id} has already liked blog with ID: {blog_id}")
        raise HTTPException(status_code=400, detail="You have already liked this blog")

    db_blog.like.append(db_user_id)
    db.commit()
    db.refresh(db_blog)
    logger.success(f"Blog liked successfully with ID: {blog_id}")
    return {"detail": "Successfully liked the blog"}

# ------------------------------------------------------likes_by_count ----------------------------------------------------

@blogger.get("/likes_by_count")
def likes_by_count(blog_id: str):
    logger.info(f"Fetching like count for blog ID: {blog_id}")
    db_blog = db.query(Blog).filter(Blog.blog_id == blog_id, Blog.is_active == True, Blog.is_deleted == False).first()
    if db_blog is None:
        logger.warning(f"Blog not found with ID: {blog_id}")
        raise HTTPException(status_code=404, detail="Blog not found")
    
    likes_count = len(db_blog.like)
    logger.success(f"Like count for blog ID {blog_id}: {likes_count}")
    return {"blog_id": blog_id, "likes_count": likes_count}


# ================================================================================================================================
# --------------------------------------------------ADD_COMMENT--------------------------------------------------------------
# ==================================================================================================================================

@blogger.post("/add_comment")
def add_comment(comment_data: Commenttt):
    logger.info(f"Adding comment to blog ID: {comment_data.blogs_id}")
    db_user_id = decode_token_user_id(comment_data.token)
    db_user = db.query(User).filter(User.id == db_user_id, User.is_active == True, User.is_deleted == False, User.is_verified == True).first()

    if not db_user:
        logger.warning(f"User not found with ID from token")
        raise HTTPException(status_code=404, detail="User not found")

    db_blog = db.query(Blog).filter(Blog.blog_id == comment_data.blogs_id).first()

    if not db_blog:
        logger.warning(f"Blog not found with ID: {comment_data.blogs_id}")
        raise HTTPException(status_code=404, detail="Blog not found")

    new_comment = {"user_id": db_user_id, "comment": comment_data.comment}
    
    if db_blog.comments:
        db_blog.comments.append(new_comment)
    else:
        db_blog.comments = [new_comment]

    db.add(db_blog)
    db.commit()
    logger.success(f"Comment added successfully to blog ID: {comment_data.blogs_id}")
    return {"message": "Comment added successfully"}


# ================================================================================================================================
# --------------------------------------------------RATTING_SYSTEM--------------------------------------------------------------
# ==================================================================================================================================


# --------------------------------------------------calculate_average_rating--------------------------------------------------------------

def calculate_average_rating(total_rating: float, ratings_count: int) -> float:
    if ratings_count == 0:
        logger.warning("Attempted to calculate average rating with zero ratings count")
        return 0.0  # Return 0 if there are no ratings

    average_rating = total_rating / ratings_count
    logger.info(f"Calculated average rating: {average_rating} from total rating: {total_rating} and ratings count: {ratings_count}")
    return round(average_rating, 2)  # Round to 2 decimal places

@blogger.post("/add_blog_rating/{blog_id}", response_model=BlogInDB)
def add_blog_rating(blog_id: str, rating: str):
    logger.info(f"Received request to add rating for blog_id: {blog_id} with rating: {rating}")
    
    db_blog = db.query(Blog).filter(Blog.blog_id == blog_id, Blog.is_active == True, Blog.is_deleted == False).first()
    if not db_blog:
        logger.error(f"Blog with id {blog_id} not found or inactive/deleted")
        raise HTTPException(status_code=404, detail="Blog not found")
    
    if db_blog.total_rating is None:
        db_blog.total_rating = 0
        logger.info(f"Initialized total_rating to 0 for blog_id: {blog_id}")
    
    if db_blog.ratings_count is None:
        db_blog.ratings_count = 0
        logger.info(f"Initialized ratings_count to 0 for blog_id: {blog_id}")
    
    db_blog.ratings_count += 1
    db_blog.total_rating += float(rating)  # Convert rating to float before adding
    logger.info(f"Updated blog_id: {blog_id} - new total_rating: {db_blog.total_rating}, new ratings_count: {db_blog.ratings_count}")
    
    # Calculate and update average rating
    db_blog.average_rating = calculate_average_rating(db_blog.total_rating, db_blog.ratings_count)
    logger.info(f"Updated average rating for blog_id: {blog_id} to {db_blog.average_rating}")
    
    db.commit()
    db.refresh(db_blog)
    logger.success(f"Successfully added rating and updated blog entry for blog_id: {blog_id}")
    
    return db_blog





# # --------------------------------------------------update_blog_rating--------------------------------------------------------------

# @blogger.put("/update_blog_rating/{blog_id}", response_model=BlogInDB)
# def update_blog_rating(blog_id: str, rating: float):
#     db_blog = db.query(Blog).filter(
#             Blog.blog_id == blog_id,
#             Blog.is_active == True,
#             Blog.is_deleted == False
#         ).first()

#     if not db_blog:
#             raise HTTPException(status_code=404, detail="Blog not found")

#     if db_blog.ratings_count == 0:
#             raise HTTPException(status_code=400, detail="No previous ratings for this blog")

#     db_blog.total_rating = db_blog.total_rating - db_blog.average_rating + rating
#     db_blog.average_rating = calculate_average_rating(db_blog.total_rating, db_blog.ratings_count)

#     db.commit()
#     db.refresh(db_blog)

#     return db_blog






# --------------------------------------------------get_blog_ratings--------------------------------------------------------------


@blogger.get("/get_blog_ratings/{blog_id}", response_model=BlogInDB)
def get_blog_ratings(blog_id: str):
    logger.info(f"Received request to get ratings for blog_id: {blog_id}")

    db_blog = db.query(Blog).filter(Blog.blog_id == blog_id, Blog.is_active == True, Blog.is_deleted == False).first()
    if not db_blog:
        logger.error(f"Blog with id {blog_id} not found or inactive/deleted")
        raise HTTPException(status_code=404, detail="Blog not found")
    
    logger.success(f"Successfully retrieved ratings for blog_id: {blog_id}")
    return db_blog


# ------------------------------------------------get_blog_ratings_count------------------------------------------------------------

@blogger.get("/get_blog_ratings_count/{blog_id}", response_model=dict)
def get_blog_ratings_count(blog_id: str):

    logger.info(f"Received request to get ratings count for blog_id: {blog_id}")
    db_blog = db.query(Blog).filter(Blog.blog_id == blog_id, Blog.is_active == True, Blog.is_deleted == False).first()

    if not db_blog:
        logger.error(f"Blog with id {blog_id} not found or inactive/deleted")
        raise HTTPException(status_code=404, detail="Blog not found")
    
    ratings_count = db_blog.ratings_count if db_blog.ratings_count else 0
    logger.success(f"Ratings count for blog_id {blog_id}: {ratings_count}")
    return {"ratings_count": ratings_count}