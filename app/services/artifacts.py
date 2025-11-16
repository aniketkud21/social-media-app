from sqlalchemy.orm import Session
from app.models.artifact import Artifact

def get_all_artifacts(db: Session):
    return db.query(Artifact).all()

def get_artifacts_count(db: Session) -> int:
    return db.query(Artifact).count()

def get_artifact_by_id(db: Session, public_id: int):
    return db.query(Artifact).filter(Artifact.public_id == public_id).first()

def get_artifacts_between_ids(db: Session, start_id: int, end_id: int):
    return db.query(Artifact).filter(Artifact.id.between(start_id, end_id)).all()

def create_artifact(db: Session, post_id: int, attrs):
    artifact = Artifact(post_id=post_id, file_type=attrs.file_type, file_path=attrs.file_path, file_id=attrs.file_id, thumbnail_url=attrs.thumbnail_url)
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact

def create_artifacts(db: Session, post_id: int, artifacts: list[Artifact]):
    for artifact in artifacts:
        create_artifact(db, post_id, artifact)