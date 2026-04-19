from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from backend.cores.exception import EntityNotFound


class BaseService():
    """Base service class for FastAPI applications."""
    
    def __init__(self ,model:SQLModel , session: AsyncSession):
        # Get database session to perform database operations
        self.session = session
        self.model = model
    
    async def _get(self, id: str) :
        
        result = await self.session.get(self.model, id)
        return result 

    async def _create(self, obj_create: SQLModel) -> SQLModel:

        self.session.add(obj_create)
        await self.session.commit()
        await self.session.refresh(obj_create)

        return obj_create
   
    async def _update(self,obj_create: SQLModel) :
        return await self._create(obj_create)
    
    async def _delete(self, id: str) :
        obj = await self.get(id)
        if not obj:
            raise EntityNotFound()
        await self.session.delete(obj)
        await self.session.commit()