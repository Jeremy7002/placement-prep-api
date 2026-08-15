from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from security import get_current_user
from schemas import CreateResourceRequest, ResourceResponse, DeleteResponse
from services.resource_service import ResourceService

router = APIRouter()


@router.post("/resources", status_code=201, response_model=ResourceResponse)
def create_resources(data: CreateResourceRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ResourceService.create(db, current_user.id, data)


@router.get("/resources", response_model=list[ResourceResponse])
def get_resource(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ResourceService.get_all(db, current_user.id)


@router.delete("/resources/{id}", response_model=DeleteResponse)
def delete_resource(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resource = ResourceService.get_by_id(db, id, current_user.id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource Not Found")
    title_val = resource.title
    ResourceService.delete(db, resource)
    return {"message": f"The Resource {title_val} has been deleted"}