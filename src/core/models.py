from pydantic import BaseModel, Field
from typing import Dict, Optional

class StorySpec(BaseModel):
    title: str = Field(..., description="The title of the specification")
    category: str = Field(..., description="The category (Lore, Canon, etc)")
    version: str = Field("0.1", description="Semantic version of the spec")
    description: Optional[str] = Field("", description="Short description")
    
    # Optional: We could validate category here against config.CATEGORIES
    
class StoryMetadata(BaseModel):
    specs: Dict[str, StorySpec] = Field(default_factory=dict, description="Map of relative file paths to Spec data")
