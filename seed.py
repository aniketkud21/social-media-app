from app.config.database import SessionLocal, engine, Base
from app.models.post import Post
from uuid import uuid4
from datetime import datetime, timezone

def create_dummy_posts(num_posts: int = 15):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for i in range(1, num_posts + 1):
            post = Post(
                public_id=uuid4(),
                title=f"Dummy Post {i}",
                content=f"This is the content for dummy post {i}. It's great!",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(post)
        db.commit()
        print(f"Added {num_posts} dummy posts to the database.")
    except Exception as e:
        db.rollback()
        print(f"Error adding dummy posts: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_dummy_posts(20) # Create 20 dummy posts
