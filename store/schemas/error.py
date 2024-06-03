from pydantic import BaseModel


class ErrorBase(BaseModel):
    message: str
    file_id: int


class ErrorCreate(ErrorBase):
    pass


class Error(ErrorBase):
    id: int

    class Config:
        orm_mode = True
