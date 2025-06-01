from fastapi import FastAPI, HTTPException, Depends, Security, status 
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, field_validator
from typing import List, Optional
from . import models
from .database import get_db
from sqlalchemy.orm import Session
from uuid import UUID
import os

API_KEY_NAME = os.getenv("API_KEY_NAME")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI()

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):  # Clave almacenada en variables de entorno
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key inválida o faltante"
        )
    return api_key

# Modelos Pydantic
class ObraResponse(BaseModel):
    uuid: str
    nombre_archivo: str
    titulo: str
    autor: str
    año: int
    estilo: str
    descripcion: str

    @field_validator('uuid', mode='before')
    def uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from pydantic import ConfigDict
        model_config = ConfigDict(from_attributes=True)

class MedioResponse(BaseModel):
    tipo_medio: str
    url: Optional[str] = None
    info: Optional[str] = None
    ruta_local: Optional[str] = None

# Endpoints
@app.get("/obras/{obra_uuid}", response_model=ObraResponse, dependencies=[Depends(get_api_key)])
async def get_obra(obra_uuid: str, db: Session = Depends(get_db)):
    obra = db.query(models.Obra).filter(models.Obra.uuid == obra_uuid).first()
    if not obra:
        raise HTTPException(status_code=404, detail="Obra no encontrada")
    return obra

@app.get("/medios/{obra_uuid}", response_model=List[MedioResponse], dependencies=[Depends(get_api_key)])
async def get_medios(obra_uuid: str, db: Session = Depends(get_db)):
    obra = db.query(models.Obra).filter(models.Obra.uuid == obra_uuid).first()
    if not obra:
        raise HTTPException(status_code=404, detail="Obra no encontrada")
    
    medios = db.query(models.Medio).filter(models.Medio.obra_id == obra.id).all()
    return medios

