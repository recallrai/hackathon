from typing import List
from datetime import datetime
from pydantic import BaseModel, Field

DATETIME_FORMAT = "%Y/%m/%d %I:%M %p"

class Memory(BaseModel):
    id: str
    content: str
    created_at: str = Field(
        description="Datetime string in format YYYY/MM/DD HH:MM AM/PM"
    )

    @classmethod
    def validate_datetime(cls, dt_str: str) -> bool:
        try:
            # Clean up datetime string
            dt_str = dt_str.strip()
            datetime.strptime(dt_str, DATETIME_FORMAT)
            return True
        except ValueError:
            return False

    @classmethod
    def clean_datetime(cls, dt_str: str) -> str:
        return dt_str.strip()