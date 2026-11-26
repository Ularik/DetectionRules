from pydantic import BaseModel, ConfigDict, Field

# Схемы ответов в OpenAPI движка пустые — формы сверены по фактическим ответам движка


class CorrelationFolderCreateSchema(BaseModel):
    """Тело POST/PUT /correlation-folders (CorrelationFolderCreate движка)"""
    name: str = Field(..., min_length=1, max_length=120,
                      description="Название папки, уникальное внутри тактики MITRE")
    mitre_tactic: str = Field(..., min_length=1, max_length=100,
                              description="Тактика MITRE — value из GET /api/mitre/tactics")

    model_config = ConfigDict(json_schema_extra={"examples": [{"name": "Выполнение команд", "mitre_tactic": "execution"}]})


class CorrelationFolderAssignmentSchema(BaseModel):
    """Тело PUT /correlation-rules/{correlation_id}/folder (CorrelationFolderAssignment движка)"""
    folder_id: str | None = Field(None, description="Папка правила; null — убрать правило из папки")

    model_config = ConfigDict(json_schema_extra={"examples": [{"folder_id": "0906a1aecc4740fc9f7354a50bd15235"}]})


class CorrelationFolderSchema(BaseModel):
    """Папка правил корреляции"""
    folder_id: str
    name: str
    mitre_tactic: str

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "folder_id": "0906a1aecc4740fc9f7354a50bd15235", "name": "Выполнение команд", "mitre_tactic": "execution",
    }]})


class CorrelationFolderListResponseSchema(BaseModel):
    """Ответ GET /correlation-folders"""
    items: list[CorrelationFolderSchema]
    count: int


class CorrelationFolderResponseSchema(BaseModel):
    """Ответ POST/PUT /correlation-folders"""
    success: bool
    folder: CorrelationFolderSchema


class CorrelationFolderDeleteResponseSchema(BaseModel):
    """Ответ DELETE /correlation-folders/{folder_id}"""
    success: bool
    deleted: str = Field(..., description="folder_id удалённой папки")


class CorrelationFolderRulesResponseSchema(BaseModel):
    """Ответ GET /correlation-folders/{folder_id}/rules; полные правила — через GET /api/correlation-rules"""
    folder: CorrelationFolderSchema
    correlation_ids: list[str]
    count: int


class CorrelationFolderAssignmentItemSchema(BaseModel):
    """Привязка правила корреляции к папке"""
    correlation_id: str
    folder_id: str | None = None


class CorrelationFolderAssignmentsResponseSchema(BaseModel):
    """Ответ GET /correlation-folders/assignments; правила без привязки показываются в разделе «Без папки»"""
    items: list[CorrelationFolderAssignmentItemSchema]
    count: int


class CorrelationFolderAssignResponseSchema(CorrelationFolderAssignmentItemSchema):
    """Ответ PUT /correlation-rules/{correlation_id}/folder"""
    success: bool
