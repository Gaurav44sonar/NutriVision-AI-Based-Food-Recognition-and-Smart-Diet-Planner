# # from fastapi import FastAPI, UploadFile, File
# # import shutil
# # import os
# # from utils.pipeline import process_image

# # app = FastAPI()

# # UPLOAD_DIR = "uploads"
# # os.makedirs(UPLOAD_DIR, exist_ok=True)

# # @app.post("/predict")
# # async def predict(file: UploadFile = File(...)):
# #     file_path = os.path.join(UPLOAD_DIR, file.filename)

# #     with open(file_path, "wb") as buffer:
# #         shutil.copyfileobj(file.file, buffer)

# #     result = process_image(file_path)

# #     return result


# from fastapi import FastAPI, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# import shutil
# import os
# import uuid

# from utils.pipeline import process_image

# app = FastAPI(title="NutriVision API 🚀")

# # =========================
# # 🔥 CORS (VERY IMPORTANT FOR REACT)
# # =========================
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],   # for development (React)
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # =========================
# # 📁 UPLOAD FOLDER
# # =========================
# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# # =========================
# # 🏠 ROOT ROUTE
# # =========================
# @app.get("/")
# def home():
#     return {"message": "NutriVision API is running 🚀"}

# # =========================
# # 🔍 PREDICTION ROUTE
# # =========================
# @app.post("/predict")
# async def predict(file: UploadFile = File(...)):

#     # 🔥 Unique filename (avoid overwrite issue)
#     file_ext = file.filename.split(".")[-1]
#     unique_name = f"{uuid.uuid4()}.{file_ext}"
#     file_path = os.path.join(UPLOAD_DIR, unique_name)

#     # Save file
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     try:
#         # 🔥 Run pipeline
#         result = process_image(file_path)

#         return {
#             "success": True,
#             "data": result
#         }

#     except Exception as e:
#         return {
#             "success": False,
#             "error": str(e)
#         }






from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid

# 🔥 Internal imports
from utils.pipeline import process_image
from auth import create_user, get_user
from db import users_collection   # ✅ FIXED
from utils.gemini import generate_diet_plan

app = FastAPI(title="NutriVision API 🚀")

# =========================
# 🔥 CORS (FOR REACT)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 📁 UPLOAD FOLDER
# =========================
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# =========================
# 🏠 ROOT
# =========================
@app.get("/")
def home():
    return {"message": "NutriVision API is running 🚀"}

# =========================
# 🔐 SIGNUP
# =========================
@app.post("/signup")
async def signup(user: dict = Body(...)):
    try:
        existing = get_user(user["email"])

        if existing:
            return {"success": False, "error": "User already exists"}

        create_user(user)

        return {"success": True, "message": "User created successfully"}

    except Exception as e:
        return {"success": False, "error": str(e)}

# =========================
# 🔐 LOGIN
# =========================
# @app.post("/login")
# async def login(data: dict = Body(...)):
#     try:
#         user = get_user(data["email"])

#         if not user:
#             return {"success": False, "error": "User not found"}

#         if user["password"] != data["password"]:
#             return {"success": False, "error": "Invalid password"}

#         return {
#             "success": True,
#             "message": "Login successful",
#             "user": {
#                 "email": user["email"],
#                 "name": user.get("name", "")
#             }
#         }

#     except Exception as e:
#         return {"success": False, "error": str(e)}

@app.post("/login")
async def login(data: dict = Body(...)):
    user = get_user(data["email"])

    if not user:
        return {"success": False, "error": "User not found"}

    if user["password"] != data["password"]:
        return {"success": False, "error": "Invalid password"}

    # 🔥 REMOVE PASSWORD BEFORE RETURN
    user.pop("password", None)
    user["_id"] = str(user["_id"])

    return {
        "success": True,
        "user": user
    }

# =========================
# 👤 CREATE PROFILE
# =========================
@app.post("/create-profile")
async def create_profile(profile: dict = Body(...)):
    try:
        users_collection.update_one(
            {"email": profile["email"]},
            {"$set": profile},
            upsert=True   # 🔥 IMPORTANT
        )

        return {"success": True, "message": "Profile saved"}

    except Exception as e:
        return {"success": False, "error": str(e)}

# =========================
# 🔍 PREDICT FOOD
# =========================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # 🔥 Unique filename
        file_ext = file.filename.split(".")[-1]
        unique_name = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 🔥 Run AI pipeline
        result = process_image(file_path)

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/ai-diet/{email}")
async def ai_diet(email: str, consumed: int):
    try:
        user = users_collection.find_one({"email": email})

        if not user:
            return {"success": False, "error": "User not found"}

        diet = generate_diet_plan(user, consumed)

        return {
            "success": True,
            "diet": diet   # ✅ IMPORTANT CHANGE
        }

    except Exception as e:
        return {"success": False, "error": str(e)}