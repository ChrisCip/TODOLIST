"""
Data Models Module

This module defines Pydantic models for data validation and serialization.
It includes models for:
- User registration and authentication
- Task management
- JWT tokens
"""

from pydantic import BaseModel, EmailStr, Field, validator, GetJsonSchemaHandler, field_validator
from pydantic.json_schema import JsonSchemaValue
from typing import Optional, Any, Annotated
from datetime import datetime
from bson import ObjectId
import re

class PyObjectId(str):
    """Custom type for handling MongoDB ObjectID"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler=None):
        if not isinstance(v, (str, ObjectId)):
            raise TypeError('ObjectId required')
        if not ObjectId.is_valid(str(v)):
            raise ValueError('Invalid ObjectId')
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema: Any, _handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        """Customize JSON schema for OpenAPI"""
        return {"type": "string", "format": "objectid"}

class UserCreate(BaseModel):
    """Schema for user registration data validation"""
    name: str = Field(..., min_length=2, max_length=50, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ..., 
        min_length=6,
        max_length=50,
        description="User's password"
    )

    @field_validator('name')
    def validate_name(cls, v):
        """Validate that name is properly formatted"""
        v = v.strip()
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters')
        if not re.match(r'^[a-zA-Z\s-]+$', v):
            raise ValueError('Name can only contain letters, spaces, and hyphens')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

class User(BaseModel):
    """Schema for user response data"""
    id: PyObjectId = Field(alias="_id")
    name: str
    email: EmailStr

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
        populate_by_name = True
        arbitrary_types_allowed = True

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for JWT token payload"""
    email: Optional[str] = None

class TaskCreate(BaseModel):
    """Schema for task creation"""
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class Task(BaseModel):
    """Schema for task response data"""
    id: str = Field(alias="_id")
    user_id: str
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    completed: bool = Field(default=False)

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "title": "Complete project",
                "description": "Finish the API implementation",
                "due_date": "2024-12-31T23:59:59",
                "created_at": "2024-01-01T00:00:00",
                "completed": False
            }
        }
    }
