from typing import Dict, List
from pydantic import BaseModel, Field

class BeatConfig(BaseModel):
    beats: List[str] = Field(..., min_items=1)
    gen_metadata_flag: bool = False

class StoryResponse(BaseModel):
    final_story: str
    final_story_word_count: int
    generation_cost: Dict[str, float] 
    generation_time: float
    generation_metadata: dict = None