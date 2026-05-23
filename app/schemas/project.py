from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, ConfigDict

class MonitoredProjectBase(BaseModel):
    name: str
    url: str
    is_active: Optional[bool] = True
    check_interval_seconds: Optional[int] = 300
    expected_status_code: Optional[int] = 200

class MonitoredProjectCreate(MonitoredProjectBase):
    pass

class MonitoredProjectUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    is_active: Optional[bool] = None
    check_interval_seconds: Optional[int] = None
    expected_status_code: Optional[int] = None

class PerformanceMetricResponse(BaseModel):
    id: int
    project_id: int
    response_time_ms: int
    status_code: Optional[int]
    ssl_days_remaining: Optional[int]
    is_up: bool
    error_message: Optional[str]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class MonitoredProjectResponse(MonitoredProjectBase):
    id: int
    last_status: str
    last_checked_at: Optional[datetime] = None
    last_error: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
