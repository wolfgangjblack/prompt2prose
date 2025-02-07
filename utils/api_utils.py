from pydantic import BaseModel

class StarterConfig(BaseModel):
    name: str
    age: int