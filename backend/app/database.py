"""
Database Module

This module handles all database-related operations including:
- Database connection management
- Collection initialization
- Index creation
"""

from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings
import logging
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect_to_database(cls):
        """
        Create database connection and verify it.
        
        Raises:
            ConnectionFailure: If connection to MongoDB fails
            ServerSelectionTimeoutError: If MongoDB server is unreachable
        """
        try:
            cls.client = AsyncIOMotorClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            
            # Verify connection
            await cls.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB")
            
            # Create indexes
            await cls.create_indexes()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error while connecting to MongoDB: {str(e)}")
            raise

    @classmethod
    async def close_database_connection(cls):
        """Close database connection safely."""
        try:
            if cls.client is not None:
                cls.client.close()
                logger.info("✅ Successfully closed MongoDB connection")
        except Exception as e:
            logger.error(f"❌ Error closing MongoDB connection: {str(e)}")
            raise

    @classmethod
    async def create_indexes(cls):
        """
        Create database indexes for optimization.
        
        Creates:
            - Unique index on users.email
            - Index on tasks.user_id
            - Compound index on tasks for filtering
        """
        try:
            db = cls.client[settings.database_name]
            
            # Create unique index for email in users collection
            await db.users.create_index("email", unique=True)
            
            # Create index for user_id in tasks collection
            await db.tasks.create_index("user_id")
            
            # Create compound index for task filtering
            await db.tasks.create_index([
                ("user_id", 1),
                ("completed", 1),
                ("due_date", 1)
            ])
            
            logger.info("✅ Database indexes created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create database indexes: {str(e)}")
            raise

    @classmethod
    def get_db(cls) -> AsyncIOMotorClient:
        """
        Get database client instance.
        
        Returns:
            AsyncIOMotorClient: MongoDB database instance
            
        Raises:
            ConnectionError: If database client is not initialized
        """
        if cls.client is None:
            logger.error("❌ Database client not initialized")
            raise ConnectionError("Database client not initialized")
        return cls.client[settings.database_name]

    @classmethod
    async def verify_task_ownership(cls, task_id: str, user_id: str) -> bool:
        """
        Verify if a task belongs to a specific user.
        
        Args:
            task_id: The ID of the task to verify
            user_id: The ID of the user to check against
            
        Returns:
            bool: True if the task belongs to the user, False otherwise
            
        Raises:
            ValueError: If task_id is invalid
        """
        try:
            db = cls.get_db()
            task = await db.tasks.find_one({
                "_id": ObjectId(task_id),
                "user_id": ObjectId(user_id)
            })
            return task is not None
        except Exception as e:
            logger.error(f"❌ Error verifying task ownership: {str(e)}")
            return False 