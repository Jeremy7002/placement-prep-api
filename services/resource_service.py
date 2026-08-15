from sqlalchemy.orm import Session

from models import Resource
from schemas import CreateResourceRequest


class ResourceService:

    @staticmethod
    def create(db: Session, user_id: int, data: CreateResourceRequest) -> Resource:
        new_resource = Resource(
            user_id=user_id,
            topic=data.topic,
            title=data.title,
            url=data.url,
            notes=data.notes
        )
        db.add(new_resource)
        db.commit()
        db.refresh(new_resource)
        return new_resource

    @staticmethod
    def get_all(db: Session, user_id: int) -> list[Resource]:
        return db.query(Resource).filter(Resource.user_id == user_id).all()

    @staticmethod
    def get_by_id(db: Session, id: int, user_id: int) -> Resource | None:
        return db.query(Resource).filter(Resource.id == id, Resource.user_id == user_id).first()

    @staticmethod
    def delete(db: Session, resource: Resource) -> None:
        db.delete(resource)
        db.commit()