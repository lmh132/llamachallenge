import asyncio
from database import SessionLocal, engine, Base
from models import Test, UserKnowledge, User  # or any other model

async def init_models():
    # (optional) create tables if you haven't run migrations yet
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def insert_user():
    async with SessionLocal() as session:
        # 1) Make sure tables exist
        await init_models()

        # 2) Create a new instance
        test_user = User(
            username = "TestingUser", 
            email = "by58@duke.edu",
            hashed_password = "hashed_password"
        )

        # 3) Add + commit
        session.add(test_user)
        await session.commit()

        # 4) Refresh to get auto‑populated fields
        await session.refresh(test_user)

        print(f"Inserted user: id={test_user.id}, username={test_user.username}, email={test_user.email}")

if __name__ == "__main__":
    asyncio.run(insert_user())