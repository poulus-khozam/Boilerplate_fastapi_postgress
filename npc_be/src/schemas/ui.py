# npc_be/src/schemas/ui.py
from pydantic import BaseModel
from typing import List, Optional

class MenuItem(BaseModel):
    id: str
    label: str
    icon: str          # e.g., "mdi-lock" or "mdi-account"
    action_type: str   # e.g., "NAVIGATE", "LOGOUT", "OPEN_URL"
    destination: str   # e.g., "/change-password"
    color: str = "primary"
