
from pydantic import BaseModel, Extra


class Model(BaseModel):

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.forbid
