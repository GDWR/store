from pydantic import BaseModel


class FileBase(BaseModel):
    path: str


class FileCreate(FileBase):
    pass


class File(FileBase):
    id: int

    class Config:
        orm_mode = True
