from pydantic import BaseModel

from .error import Error

class FileBase(BaseModel):
    path: str


class FileCreate(FileBase):
    pass


class File(FileBase):
    id: int

    class Config:
        orm_mode = True


class FileWithErrors(FileBase):
    id: int
    errors: list[Error]

    class Config:
        orm_mode = True
