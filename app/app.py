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
    
    if page == None:
        page = 1
        
    start = (page - 1) * page_size
    end = start + page_size
    
    if start >= total_no_posts:
        return HTTPException(status_code=404, detail="Page not found")
    
    if end > total_no_posts:
        end = total_no_posts
    
    all_posts = Posts.get_posts_between_ids(db, start+1, end+1)
    for post in all_posts:
        Posts.load_artifacts(post)    
    
    return {"no_of_posts": total_no_posts, "posts": all_posts}

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
    
    
    
    