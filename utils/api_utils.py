from pydantic import BaseModel

class BeatConfig(BaseModel):
    beats: list[str] = None
    gen_metadata_flag: bool = False