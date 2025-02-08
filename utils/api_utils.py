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


class CharacterInfo(BaseModel):
    name: str
    profile: str


class SettingInfo(BaseModel):
    location: str
    notes: str


class MetadataConfig(BaseModel):
    setting: SettingInfo
    characters: List[CharacterInfo]
    genre: Optional[str] = None
    style: Optional[str] = None


class BeatMetadataConfig(BeatConfig):
    user_metadata: MetadataConfig
