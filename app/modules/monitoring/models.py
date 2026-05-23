from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class MonitoredProject(BaseModel):
    __tablename__ = "monitored_projects"

    name = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    check_interval_seconds = Column(Integer, default=300, nullable=False)  # Interval for checks
    expected_status_code = Column(Integer, default=200, nullable=False)
    
    last_status = Column(String, default="UNKNOWN", nullable=False)  # UP, DOWN, UNKNOWN
    last_checked_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)

    metrics = relationship("PerformanceMetric", back_populates="project", cascade="all, delete-orphan")

class PerformanceMetric(BaseModel):
    __tablename__ = "performance_metrics"

    project_id = Column(Integer, ForeignKey("monitored_projects.id", ondelete="CASCADE"), nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    status_code = Column(Integer, nullable=True)
    ssl_days_remaining = Column(Integer, nullable=True)
    is_up = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False)

    project = relationship("MonitoredProject", back_populates="metrics")
