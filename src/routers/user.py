import logging
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Header
from typing import List
from database.database import SessionLocal
import uuid
from passlib.context import CryptContext
from src.models.user_mod import User
from src.models.otp_mod import OTP
from src.models.category_mod import Category
from src.models.blog_mod import Blog
from src.schemas.user_sch import Users, UserBase, UserCreate, UserUpdate, UsersPatch
from src.utils.token import get_encode_token, decode_token_user_id, decode_token_password, decode_token_user_name, login_token, decode_token_email
from src.schemas.otp_sch import OTPRequest, OTPVerify
import string
import smtplib
import random
from logs.log_config import logger
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from src.utils.otp import generate_otp



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

user = APIRouter()
db = SessionLocal()
Otp = APIRouter()

# ----------------------------------------------encode_token_id------------------------------------------------------

@user.get("/encode_token_id")
def encode_token_id(id: str):
    logger.info(f"Encoding token for ID: {id}")
    access_token = get_encode_token(id)
    return access_token

# ----------------------------------------------Create_User_post------------------------------------------------------

@user.post("/Create_User_post", response_model=Users)
def create_register_user(user: Users):
    logger.info(f"Creating user: {user.email}")
    find_same_email = db.query(User).filter(User.email == user.email ).first()
    if find_same_email:
        logger.warning(f"Duplicate email found for: {user.email}")
        raise HTTPException(status_code=401, detail="Same E-mail  found please try another one!!!!!!")
    
    find_same_uname = db.query(User).filter( User.username == user.username).first()
    if find_same_uname:
        logger.warning(f"Duplicate  username found for : {user.email}")
        raise HTTPException(status_code=401, detail="Same username found please try another one!!!!!!")

    find_same_mobile_number=db.query(User).filter(User.mobile_no == user.mobile_no).first()
    if find_same_mobile_number:
        logger.warning(f"Duplicate email or username found for: {user.mobile_no}")
        raise HTTPException(status_code=401, detail="Same mobile number found please try another one!!!!!!")
    

    new_user = User(
        id=str(uuid.uuid4()),
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        mobile_no=user.mobile_no,
        password=pwd_context.hash(user.password),
        bio=user.bio,
        role=user.role,
        address=user.address,
        followers=[],
        following=[],
    )
    db.add(new_user)
    db.commit()
    logger.success(f"User created successfully: {user.email}")
    return new_user

# ----------------------------------------------get_all_users------------------------------------------------------

@user.get("/get_all_users", response_model=List[Users])
def get_all_user():
    logger.info("Fetching all users")
    db_user = db.query(User).filter(User.is_active == True, User.is_verified == True).all()
    if db_user is None:
        logger.warning("No active and verified users found")
        raise HTTPException(status_code=404, detail="User Not Found")
    return db_user

# ----------------------------------------------get_user_by_token_id------------------------------------------------------

@user.get("/get_user_by_token_id/", response_model=Users)
def get_employee_by_id(token=Header(...)):
    logger.info(f"Fetching user by token")
    user_id = decode_token_user_id(token)
    db_user = db.query(User).filter(User.id == user_id, User.is_active == True, User.is_verified == True).first()
    if db_user is None:
        logger.warning(f"User not found for token: {token}")
        raise HTTPException(status_code=404, detail="User Not Found !!!")
    return db_user

# # ----------------------------------------------update_user_by_token------------------------------------------------------

@user.put("/update_user_by_token/")
def update_user_data(user: Users, token=Header(...)):
    logger.info(f"Updating user by token")
    user_id = decode_token_user_id(token)
    db_user = db.query(User).filter(User.id == user_id, User.is_active == True, User.is_verified == True).first()
    if db_user is None:
        logger.warning(f"User not found for token: {token}")
        raise HTTPException(status_code=404, detail="User Not Found!!!!")
    
    existiong_user = db.query(User).filter(User.username == user.username).first()
    if existiong_user:
        logger.warning(f"Username already exists: {user.username}")
        raise HTTPException(status_code=404, detail="User already exist!!!!")
    
    existiong_email = db.query(User).filter(User.email == user.email).first()
    if existiong_email:
        logger.warning(f"E-mail already exists: {user.email}")
        raise HTTPException(status_code=404, detail="E-mail already exist!!!!")
    
    existiong_phoneno = db.query(User).filter(User.mobile_no == user.mobile_no).first()
    if existiong_phoneno:
        logger.warning(f"E-mail already exists: {user.mobile_no}")
        raise HTTPException(status_code=404, detail="Mobile-NO already exist!!!!")
    


    db_user.first_name = user.first_name,
    db_user.last_name = user.last_name,
    db_user.username = user.username,
    db_user.email = user.email,
    db_user.mobile_no = user.mobile_no,
    db_user.password = pwd_context.hash(user.password),
    db_user.bio = user.bio,
    db_user.role = user.role,
    db_user.address = user.address
    
    db.commit()
    logger.success(f"User details updated successfully for token: {token}")
    return "Your Detail Changed Successfully!!!!!!!!!!!"

# ----------------------------------------------update[PATCH]_user_by_token------------------------------------------------------

@user.patch("/update_user_patch")
def update_employee_patch(employeee: UsersPatch, token=Header(...)):
    logger.info(f"Patching user details by token")
    user_id = decode_token_user_id(token)
    find_user = db.query(User).filter(User.id == user_id, User.is_active == True, User.is_verified == True).first()
    if find_user is None:
        logger.warning(f"User not found for token: {token}")
        raise HTTPException(status_code=404, detail="User Not Found")
    update_data = employeee.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(find_user, key, value)
    db.commit()
    db.refresh(find_user)
    logger.success(f"User details patched successfully for token: {token}")
    return {"message": "Details changed successfully", "User": find_user}

# ----------------------------------------------Delete_User_by_token------------------------------------------------------

@user.delete("/delete_user_by_token/")
def delete_employee(token=Header(...)):
    emp_id = decode_token_user_id(token)
    db_user = db.query(User).filter(User.id == emp_id, User.is_active == True, User.is_verified == True).first()
    if db_user is None:
        logger.warning(f"User not found for token: {token}")
        raise HTTPException(status_code=404, detail="User Not Found.....")
    db_user.is_active = False
    db_user.is_deleted = True
    db.commit()
    logger.success(f"User deleted successfully for token: {token}")
    return "User Deleted Successfully !!!!!!!!!!!!!"

# --------------------------------------------------GENERATE_OTP ------------------------------------------------------------

def generate_otp(email: str):
    logger.info(f"Generating OTP for email: {email}")
    otp_code = str(random.randint(100000, 999999))
    expiration_time = datetime.now() + timedelta(minutes=5)
    
    otp_entry = OTP(
        email=email,
        otp=otp_code,
        expired_time=expiration_time,
    )
    db.add(otp_entry)
    db.commit()
    logger.success(f"OTP generated: {otp_code} for email: {email}")
    return otp_code

def send_otp_email(email: str, otp_code: str):
    logger.info(f"Sending OTP email to: {email}")
    sender_email = "ujasmungla@gmail.com"
    password = "wfrdhevqfopcssre"
    subject = "Your OTP Code"
    message_text = f"Your OTP is {otp_code} which is valid for 5 minutes"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = subject
    message.attach(MIMEText(message_text, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, email, message.as_string())
        server.quit()
        logger.info(f"OTP email sent successfully to: {email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

@Otp.post("/generate_otp")
def generate_otp_endpoint(request: OTPRequest):
    email = request.email  
    logger.info(f"OTP request received for email: {email}")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        logger.warning(f"User not found for email: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    otp_code = generate_otp(email)
    send_otp_email(email, otp_code)
    return {"message": "OTP generated and sent successfully to the provided email address."}

# --------------------------------------------------VERIFICATION_OTP ------------------------------------------------------------

@Otp.post("/verify_otp")
def verify_otp(otp_verify: OTPVerify):
    logger.info(f"Verifying OTP for email: {otp_verify.email}")
    otp_entry = db.query(OTP).filter(
        OTP.email == otp_verify.email,
        OTP.otp == otp_verify.otp,
        OTP.is_active == True,
        OTP.expired_time > datetime.now(),
    ).first()

    if not otp_verify.email:
        logger.warning("Email ID not provided for OTP verification")
        raise HTTPException(status_code=400, detail="Please enter email ID")
    if otp_entry is None:
        logger.warning(f"Invalid or expired OTP for email: {otp_verify.email}")
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    otp_entry.is_active = False  
    user = db.query(User).filter(User.email == otp_verify.email).first()
    if user is None:
        logger.warning(f"User not found for email: {otp_verify.email}")
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.delete(otp_entry)
    db.commit()
    logger.success(f"OTP verified successfully for email: {otp_verify.email}")
    return {"message": "OTP verified successfully"}

# ---------------------------------------------encode_token_login-----------------------------------------------------

@user.get("/encode_token_login")
def encode_token_id(id: str, password: str, email: str):
    logger.info(f"Encoding login token for ID: {id}, email: {email}")
    access_token = login_token(id, password, email)
    return access_token

# ----------------------------------------------LOGIN_USER-----------------------------------------------------

@user.get("/logging_users")
def logging_user(email: str, password: str):
    logger.info(f"Logging in user: {email}")
    db_user = db.query(User).filter(User.email == email, User.is_active == True, User.is_deleted == False, User.is_verified == True).first()
    if db_user is None:
        logger.warning(f"User not found: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(password, db_user.password):
        logger.warning(f"Incorrect password for user: {email}")
        raise HTTPException(status_code=404, detail="Password is incorrect")
    access_token = login_token(db_user.id, email, db_user.username)
    logger.success(f"User logged in successfully: {email}")
    return access_token

# ----------------------------------------------forgotpass_user_by_token------------------------------------------------------

@user.put("/forgotpass_user_by_token/")
def forgotpass_user_by_token(new_pass: str, token=Header(...)):
    logger.info("Handling forgot password request")
    user_id = decode_token_user_id(token)
    db_user = db.query(User).filter(User.id == user_id, User.is_active == True, User.is_verified == True).first()
    if db_user is None:
        logger.warning(f"User not found for token: {token}")
        raise HTTPException(status_code=404, detail="User Not Found!!!")
    db_user.password = pwd_context.hash(new_pass)
    db.commit()
    logger.success(f"Password changed successfully for user ID: {user_id}")
    return "Password Change Successfully"

# ----------------------------------------------reset_pass_user_token------------------------------------------------------

@user.put("/reset_pass_user_token/")
def reset_pass_user(old_pass: str, new_pass: str, token=Header(...)):
    logger.info("Handling reset password request")
    user_id = decode_token_user_id(token)
    db_user = db.query(User).filter(User.id == user_id, User.is_active == True, User.is_verified == True).first()
    if not db_user:
        logger.warning(f"User not found for token: {token}")
        raise HTTPException(status_code=404, detail="User not found")
    if pwd_context.verify(old_pass, db_user.password):
        db_user.password = pwd_context.hash(new_pass)
        db.commit()
        logger.success(f"Password reset successfully for user ID: {user_id}")
        return {"message": "Password Reset Successfully!!!"}
    else:
        logger.warning(f"Old password does not match for user ID: {user_id}")
        raise HTTPException(status_code=400, detail="Old password does not match")

# --------------------------------------------------------------- follow_to_someone-----------------------------------------------

@user.get("/follow_to_someone")
def follow_to_someone(user_id: str, token=Header(...)):
    logger.info(f"User requesting to follow user ID: {user_id}")
    db_user_id = decode_token_user_id(token)
    db_user = db.query(User).filter(User.id == db_user_id, User.is_active == True, User.is_deleted == False, User.is_verified == True).first()
    if db_user is None:
        logger.warning(f"User not found for token: {token}")
        raise HTTPException(status_code=404, detail="User not Found")
    
    samevalo_user = db.query(User).filter(User.id == user_id, User.is_active == True, User.is_deleted == False, User.is_verified == True).first()
    if samevalo_user is None:
        logger.warning(f"User to follow not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not Found")

    if user_id in db_user.following:
        logger.warning(f"User {db_user_id} is already following user: {user_id}")
        raise HTTPException(status_code=404, detail="You are already following this user")

    if db_user.following is None:
        db_user.following = []
    if samevalo_user.followers is None:
        samevalo_user.followers = []

    following_list = db_user.following.copy()
    followers_list = samevalo_user.followers.copy()

    if user_id not in following_list:
        following_list.append(user_id)
    db_user.following = following_list

    if db_user_id not in followers_list:
        followers_list.append(db_user_id)
    samevalo_user.followers = followers_list

    db.commit()
    logger.success(f"User {db_user_id} followed user {user_id} successfully")
    pass

# --------------------------------------------------------------get_following_by_id----------------------------------------------------------------

@user.get("/get_following_by_id")
def get_following(token=Header(...)):
    logger.info("Fetching following list")
    db_user_id = decode_token_user_id(token)
    db_user = db.query(User).filter(User.id == db_user_id, User.is_active == True, User.is_deleted == False, User.is_verified == True).first()
    
    if db_user is None:
        logger.warning(f"User not found for token: {token}")
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.following is None or len(db_user.following) == 0:
        return {"following": []}
    
    following_list = db.query(User).filter(User.id.in_(db_user.following), User.is_active == True, User.is_deleted == False, User.is_verified == True).all()
    
    result = []
    for user in following_list:
        result.append({
            "f_name": user.first_name,
            "l_name": user.last_name,
            "username": user.username
        })
    
    logger.success(f"Following list retrieved for user ID: {db_user_id}")
    return {"following": result}

# ----------------------------------------------------------------get_followers_by_id--------------------------------------------------

@user.get("/get_followers_by_id")
def get_followers(token=Header(...)):
    logger.info("Fetching followers list")
    db_user_id = decode_token_user_id(token)
    db_user = db.query(User).filter(User.id == db_user_id, User.is_active == True, User.is_deleted == False, User.is_verified == True).first()
    
    if db_user is None:
        logger.warning(f"User not found for token: {token}")
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.followers is None or len(db_user.followers) == 0:
        return {"followers": []}
    
    followers_list = db.query(User).filter(User.id.in_(db_user.followers), User.is_active == True, User.is_deleted == False, User.is_verified == True).all()
    
    result = []
    for user in followers_list:
        result.append({
            "f_name": user.first_name,
            "l_name": user.last_name,
            "username": user.username
        })
    
    logger.success(f"Followers list retrieved for user ID: {db_user_id}")
    return {"followers": result}

# --------------------------------------------------------------get_following_by_id_count------------------------------------------------

@user.get("/get_following_by_id_count")
def get_following_by_id_count(user_id: str):
    logger.info(f"Fetching following count for user ID: {user_id}")
    db_user = db.query(User).filter(User.id == user_id, User.is_active == True, User.is_deleted == False, User.is_verified == True).first()
    if db_user is None:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not Found")
    following_count = len(db_user.following)
    logger.success(f"Following count for user ID {user_id}: {following_count}")
    return f"following count {following_count}"

# ----------------------------------------------------------------get follower by id count--------------------------------------------------

@user.get("/get_followers_by_id_count")
def get_followers_by_id_count(user_id: str):
    logger.info(f"Fetching followers count for user ID: {user_id}")
    db_user = db.query(User).filter(User.id == user_id, User.is_active == True, User.is_deleted == False, User.is_verified == True).first()
    if db_user is None:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not Found")
    followers_count = len(db_user.followers)
    logger.success(f"Followers count for user ID {user_id}: {followers_count}")
    return f"followers count {followers_count}"





