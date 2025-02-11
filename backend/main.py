from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import timedelta, datetime
from bson import ObjectId
from .config import settings
from .schemas import UserCreate, User, Task, TaskCreate, Token
from .auth import get_password_hash, verify_password, create_access_token, get_current_user
import logging
from typing import Dict, Any, Optional
from .database import Database
from pymongo.errors import DuplicateKeyError, OperationFailure
import traceback
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application with metadata
app = FastAPI(
    title="TodoList API",
    description="RESTful API for managing tasks with JWT authentication",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI endpoint
    redoc_url="/redoc",  # ReDoc endpoint
    openapi_version="3.0.2",  # Usar una versión más compatible de OpenAPI
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Operations related to user authentication"
        },
        {
            "name": "Tasks",
            "description": "Operations for managing tasks"
        }
    ]
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "OK"}


@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection."""
    await Database.connect_to_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection."""
    await Database.close_database_connection()

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root endpoint to Swagger UI documentation"""
    return RedirectResponse(url="/docs")

@app.post("/auth/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Bad Request - Invalid data or duplicate email"},
        500: {"description": "Internal Server Error"}
    },
    tags=["Authentication"],
    summary="Register a new user"
)
async def signup(user: UserCreate):
    """Register a new user."""
    try:
        logger.info(f"Attempting to register new user: {user.email}")
        db = Database.get_db()
        
        # Create new user with hashed password
        hashed_password = get_password_hash(user.password)
        user_dict = user.model_dump(exclude={"password"})
        user_dict.update({
            "password": hashed_password,
            "_id": str(ObjectId()),  # Convertir a string inmediatamente
            "created_at": datetime.utcnow()
        })
        
        await db.users.insert_one(user_dict)
        
        # Return user without password
        created_user = {
            "_id": user_dict["_id"],  # Ya es string
            "name": user_dict["name"],
            "email": user_dict["email"]
        }
            
        logger.info(f"✅ Successfully registered user: {user.email}")
        return created_user

    except DuplicateKeyError:
        logger.warning(f"❌ Registration failed: Email already exists: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error during registration: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during registration"
        )

@app.post("/auth/login", response_model=Token,
          tags=["Authentication"],
          summary="Login user and get access token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login user and return JWT token.
    
    Args:
        form_data (OAuth2PasswordRequestForm): Login credentials
        
    Returns:
        Token: JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = await Database.get_db().users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/tasks", 
    response_model=list[Task],
    tags=["Tasks"],
    summary="Get all user tasks"
)
async def get_tasks(
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    completed: Optional[bool] = None
):
    """Get all tasks for the current user."""
    try:
        db = Database.get_db()
        query = {"user_id": ObjectId(current_user["_id"])}
        if completed is not None:
            query["completed"] = completed
            
        cursor = db.tasks.find(query).skip(skip).limit(limit)
        tasks = []
        
        async for task in cursor:
            task["_id"] = str(task["_id"])
            task["user_id"] = str(task["user_id"])
            tasks.append(task)
            
        return tasks
        
    except Exception as e:
        logger.error(f"❌ Error fetching tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching tasks"
        )

@app.post("/tasks", 
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
    summary="Create new task"
)
async def create_task(
    task: TaskCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new task."""
    try:
        db = Database.get_db()
        task_dict = task.model_dump()
        task_dict.update({
            "user_id": ObjectId(current_user["_id"]),
            "created_at": datetime.utcnow(),
            "completed": False
        })
        
        result = await db.tasks.insert_one(task_dict)
        created_task = await db.tasks.find_one({"_id": result.inserted_id})
        
        created_task["_id"] = str(created_task["_id"])
        created_task["user_id"] = str(created_task["user_id"])
        
        return created_task
        
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating task"
        )

@app.put("/tasks/{task_id}", 
    response_model=Task,
    tags=["Tasks"],
    summary="Update task"
)
async def update_task(
    task_id: str,
    task_update: TaskCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update a task."""
    try:
        db = Database.get_db()
        
        if not await Database.verify_task_ownership(task_id, current_user["_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this task"
            )
        
        update_data = task_update.model_dump()
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.tasks.find_one_and_update(
            {"_id": ObjectId(task_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
            
        result["_id"] = str(result["_id"])
        result["user_id"] = str(result["user_id"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating task"
        )

@app.delete("/tasks/{task_id}",
    tags=["Tasks"],
    summary="Delete task"
)
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a task."""
    try:
        db = Database.get_db()
        
        if not await Database.verify_task_ownership(task_id, current_user["_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this task"
            )
        
        result = await db.tasks.delete_one({"_id": ObjectId(task_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
            
        return {"message": "Task deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting task"
        )

# Add a custom exception handler for validation errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with proper logging and response format."""
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(DuplicateKeyError)
async def duplicate_key_exception_handler(request, exc):
    """Handle MongoDB duplicate key errors (e.g., duplicate email)."""
    logger.error(f"Duplicate key error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "message": "A record with this key already exists",
            "status_code": status.HTTP_400_BAD_REQUEST
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors with proper response format."""
    logger.error(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "detail": jsonable_encoder(exc.errors()),
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors with proper logging and response format."""
    logger.error(f"Unexpected error: {str(exc)}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.debug else "Internal server error",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    )