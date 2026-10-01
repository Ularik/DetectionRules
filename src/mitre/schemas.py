from pydantic import BaseModel


class MitreSchema(BaseModel):
    ids: list[str]
    tactics: list[str]
    techniques: list[str]