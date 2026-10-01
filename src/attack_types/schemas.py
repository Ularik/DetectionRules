from pydantic import BaseModel


class AttackSchema(BaseModel):
    label: str
    value: str

class AttackApiResponseSchema(BaseModel):
    items: list[AttackSchema]
    count: int