from sqlalchemy import Column, String, Integer, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import text
from .database import Base

class Obra(Base):
    __tablename__ = "obras"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(PG_UUID(as_uuid=True), unique=True, nullable=False, server_default=text("uuid_generate_v4()"))
    nombre_archivo = Column(String(255), unique=True, nullable=False)
    titulo = Column(String(100), nullable=False)
    autor = Column(String(100))
    año = Column(Integer, CheckConstraint("año >= 0"))
    estilo = Column(String(50))
    descripcion = Column(Text)

class Medio(Base):
    __tablename__ = "medios"
    
    id = Column(Integer, primary_key=True, index=True)
    obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)
    tipo_medio = Column(String(20), CheckConstraint("tipo_medio IN ('audio', 'video', 'imagen', 'texto')"))
    url = Column(String(500), nullable=True)
    ruta_local = Column(String(500), nullable=True)
    info = Column(Text, nullable=True)
    __table_args__ = (
            Index("idx_medios_obra_id", "obra_id"),
            Index("idx_medios_tipo_medio", "tipo_medio"),
        )