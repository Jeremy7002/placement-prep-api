from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User, Resource
from security import get_current_user
from schemas import CreateResourceRequest, ResourceResponse, DeleteResponse

router = APIRouter()


@router.post("/resources", status_code=201, response_model=ResourceResponse)
def create_resources(data: CreateResourceRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_resource = Resource(
        user_id=current_user.id,
        topic=data.topic,
        title=data.title,
        url=data.url,
        notes=data.notes
    )
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return new_resource


@router.get("/resources", response_model=list[ResourceResponse])
def get_resource(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(Resource).filter(Resource.user_id == current_user.id).all()
    return records


@router.delete("/resources/{id}", response_model=DeleteResponse)
def delete_resource(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == id, Resource.user_id == current_user.id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource Not Found")
    
    title_val = resource.title
    db.delete(resource)
    db.commit()
    return {"message": f"The Resource {title_val} has been deleted"}