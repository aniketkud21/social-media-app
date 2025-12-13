import uuid
from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager

from sqlalchemy.orm import Session
from app.config.database import engine, Base, get_db

from app.schemas import PostResponse
from app.schemas import PostCreate

import app.services.posts as Posts
import app.services.artifacts as Artifacts
import app.services.artifact_processing as ArtifactProcessing

from app.models import Post as PostModel
from app.models import Artifact as ArtifactModel 


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Welcome to my Application"}

@app.get("/posts")
def get_posts(page: int=None, page_size: int=5, db: Session = Depends(get_db)):
    total_no_posts = Posts.get_posts_count(db)
    
    if page is None:
        page = 1
        
    total_pages = (total_no_posts + page_size - 1) // page_size
    
    if page < 1 or page > total_pages:
        # A 400 Bad Request might be better than 404 for an invalid page number
        # but matching your original logic:
        return HTTPException(status_code=404, detail="Page not found")
        
    # 3. Determine the slice for the *most recent* posts
    # The start/end calculated here represent the *position* in the sorted list (latest first)
    offset = (page - 1) * page_size
    limit = page_size
    
    # We will fetch posts starting from the post at 'offset' position, up to 'limit' posts.
    
    # 4. Fetch the posts with ORDER BY ID DESC
    all_posts = Posts.get_latest_posts_with_pagination(db, offset, limit)
    
    # Optional: If the post object needs extra data loaded (like its original load_artifacts call)
    for post in all_posts:
        Posts.load_artifacts(post)    
    
    return {"no_of_posts": total_no_posts, "posts": all_posts, "current_page": page, "total_pages": total_pages}

@app.get("/posts/{public_id}")
def get_post(public_id: uuid.UUID, db: Session = Depends(get_db)) -> PostResponse:
    post = Posts.get_post_by_id(db, public_id)
    
    if post == None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return post

@app.post("/posts")
def create_post(payload: PostCreate, db: Session = Depends(get_db)):        
    post = Posts.create_post(db, payload.title, payload.content)

    # If artifacts exist, insert them
    if payload.artifacts:
        Artifacts.create_artifacts(db, post.id, payload.artifacts)
        
    post = Posts.get_post_by_id(db, post.public_id)
    
    if post == None:
        raise HTTPException(status_code=500, detail="Post creation failed")
        
    return post

@app.get("/upload_auth_params")
def get_auth_params():
    return ArtifactProcessing.generate_auth_params()

@app.get("/signed_url")
def get_signed_url(file_path: str):
    return ArtifactProcessing.generate_signed_url(file_path)
    
    
    
    