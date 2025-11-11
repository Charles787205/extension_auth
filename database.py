from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    _db = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        if cls.client is not None:
            return  # Already connected
            
        mongodb_url = os.getenv("MONGODB_URL")
        if not mongodb_url:
            raise ValueError("MONGODB_URL environment variable is not set")
        
        try:
            cls.client = AsyncIOMotorClient(
                mongodb_url,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
            )
            # Verify connection
            await cls.client.admin.command('ping')
            print("✓ Connected to MongoDB!")
        except Exception as e:
            print(f"✗ MongoDB connection failed: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            cls.client = None
            cls._db = None
            print("✓ Closed MongoDB connection")
    
    @classmethod
    def get_db(cls):
        """Get database instance"""
        if not cls.client:
            raise RuntimeError("Database not connected. Call connect_db() first.")
        
        if cls._db is None:
            database_name = os.getenv("DATABASE_NAME", "ext_auth")
            cls._db = cls.client[database_name]
        
        return cls._db

# Helper function to get database
async def get_database():
    if Database.client is None:
        await Database.connect_db()
    return Database.get_db()
