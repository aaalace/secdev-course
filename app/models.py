from sqlalchemy import ARRAY, Column, Integer, String

from app.database import Base


class IssueModel(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    labels = Column(ARRAY(String), default=[])
    due_at = Column(Integer, nullable=False)
    status = Column(String(20), default="open", nullable=False)
