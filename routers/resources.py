from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User, Resource
from security import get_current_user

router = APIRouter()


def resource_to_dic(resource):
    return {
        "id": resource.id,
        "title": resource.title,
        "url": resource.url,
        "topic": resource.topic,
        "notes": resource.notes,
        "created_at": resource.created_at
    }


@router.post("/resources", status_code=201)
def create_resources(topic: str, title: str, url: str, notes: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    new_resource = Resource(user_id=current_user.id, topic=topic, title=title, url=url, notes=notes)
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return {"id": new_resource.id, "title": new_resource.title}


@router.get("/resources")
def get_resource(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Resource).filter(Resource.user_id == current_user.id)
    records = query.all()
    return [resource_to_dic(p) for p in records]


@router.delete("/resources/{id}")
def delete_resource(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == id, Resource.user_id == current_user.id).first()
    if resource:
        title_val = resource.title
        db.delete(resource)
        db.commit()
        return f"The Resource {title_val} has been deleted"
    else:
        raise HTTPException(status_code=404, detail="Resource Not Found")