from pydantic import BaseModel, ConfigDict, Field

# Схемы ответов в OpenAPI движка пустые — формы сверены по фактическим ответам движка


class RuleFolderCreateSchema(BaseModel):
    """Тело POST/PUT /detection-rule-folders (DetectionRuleFolderCreate движка)"""
    name: str = Field(..., min_length=1, max_length=120, description="Название папки, уникальное")

    model_config = ConfigDict(json_schema_extra={"examples": [{"name": "Web-атаки"}]})


class RuleFolderAssignmentSchema(BaseModel):
    """Тело PUT /detection-rules/{rule_id}/folder (DetectionRuleFolderAssignment движка)"""
    folder_id: str | None = Field(None, description="Папка правила; null — убрать правило из папки")

    model_config = ConfigDict(json_schema_extra={"examples": [{"folder_id": "b939f3f0064049f8b92ae3be034bae4f"}]})


class RuleFolderSchema(BaseModel):
    """Папка правил обнаружения"""
    folder_id: str
    name: str

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "folder_id": "b939f3f0064049f8b92ae3be034bae4f", "name": "Web-атаки",
    }]})


class RuleFolderListResponseSchema(BaseModel):
    """Ответ GET /detection-rule-folders"""
    items: list[RuleFolderSchema]
    count: int


class RuleFolderResponseSchema(BaseModel):
    """Ответ POST/PUT /detection-rule-folders"""
    success: bool
    folder: RuleFolderSchema


class RuleFolderDeleteResponseSchema(BaseModel):
    """Ответ DELETE /detection-rule-folders/{folder_id}"""
    success: bool
    deleted: str = Field(..., description="folder_id удалённой папки")


class RuleFolderRulesResponseSchema(BaseModel):
    """Ответ GET /detection-rule-folders/{folder_id}/rules"""
    folder: RuleFolderSchema
    rule_ids: list[str]
    count: int


class RuleFolderAssignmentItemSchema(BaseModel):
    """Привязка правила к папке"""
    rule_id: str
    folder_id: str | None = None


class RuleFolderAssignmentsResponseSchema(BaseModel):
    """Ответ GET /detection-rule-folders/assignments (правила без папки в список не входят)"""
    items: list[RuleFolderAssignmentItemSchema]
    count: int


class RuleFolderAssignResponseSchema(RuleFolderAssignmentItemSchema):
    """Ответ PUT /detection-rules/{rule_id}/folder"""
    success: bool
