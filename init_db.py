"""
Script to initialize MongoDB with default data
Run this once to set up your database with a default admin user
"""
import asyncio
from database import Database

async def init_database():
    """Initialize database with default data"""
    await Database.connect_db()
    
    try:
        db = Database.get_db()
        
        # Create credentials collection with default admin user
        credentials_col = db.credentials
        existing_admin = await credentials_col.find_one({"username": "admin"})
        
        if not existing_admin:
            await credentials_col.insert_one({
                "username": "admin",
                "password": "password"  # CHANGE THIS IN PRODUCTION!
            })
            print("✓ Created default admin user (username: admin, password: password)")
        else:
            print("✓ Admin user already exists")
        
        # Create index on username for faster lookups
        await credentials_col.create_index("username", unique=True)
        print("✓ Created index on username")
        
        # Initialize API state
        api_state_col = db.api_state
        existing_state = await api_state_col.find_one({"_id": "current_state"})
        
        if not existing_state:
            await api_state_col.insert_one({
                "_id": "current_state",
                "status": "off",
                "message": "API is currently disabled"
            })
            print("✓ Initialized API state")
        else:
            print("✓ API state already exists")
        
        print("\n✅ Database initialization complete!")
        print("⚠️  Remember to change the default password in production!")
        
    finally:
        await Database.close_db()

if __name__ == "__main__":
    asyncio.run(init_database())
