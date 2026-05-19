from pydantic import BaseModel


class ImageResponse(BaseModel):
    id: int
    name: str
    size: str
    width: int
    height: int
    type: str
    created_at: str
    path: str

    class Config:
        from_attributes = True