# 
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class PriorityEnum(str, enum.Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"

class CategoryEnum(str, enum.Enum):
    Work = "Work"
    Personal = "Personal"
    Misc = "Misc"

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.Medium)
    category = Column(Enum(CategoryEnum), default=CategoryEnum.Misc)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="tasks")
