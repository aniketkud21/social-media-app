from sqlalchemy.orm import Session, joinedload
from app.models.post import Post
import app.services.artifact_processing as ArtifactProcessing

def get_all_posts(db: Session):
    return db.query(Post).options(joinedload(Post.artifacts)).order_by(Post.id.asc()).all()

def get_posts_count(db: Session) -> int:
    return db.query(Post).count()

def get_post_by_id(db: Session, public_id: int):
    return db.query(Post).options(joinedload(Post.artifacts)).filter(Post.public_id == public_id).first()

def get_posts_between_ids(db: Session, start_id: int, end_id: int):
    return db.query(Post).options(joinedload(Post.artifacts)).filter(Post.id.between(start_id, end_id)).all()

def create_post(db: Session, title: str, content: str):
    post = Post(title=title, content=content)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def load_artifacts(post: Post):
    for artifact in post.artifacts:
        signed_url = ArtifactProcessing.generate_signed_url(artifact.file_path)
        artifact.url = signed_url