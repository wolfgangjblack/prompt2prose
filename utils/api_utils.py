from typing import Dict, List, Optional

from pydantic import BaseModel, Field, config


class BeatConfig(BaseModel):
    beats: List[str] = Field(..., min_items=1)
    gen_metadata_flag: bool = False


class StoryResponse(BaseModel):
    final_story: str
    final_story_word_count: int
    generation_cost: Dict[str, float]
    generation_time: float
    generation_metadata: dict = None


# class MetaDataConfig(config):
#     setting: Dict[str | str] = Field(..., min_items=1)
#     character: Dict[str | str] = Field(..., min_items=1)
#     genre: Optional[str] = None
#     style : Optional[str] = None

# class BeatMetaConfig(BeatConfig):
#     metadata: MetaDataConfig
