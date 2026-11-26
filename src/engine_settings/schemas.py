from pydantic import BaseModel, Field, model_validator


class CorrelationConfig(BaseModel):
    """Окна корреляции событий в атаки и кампании."""
    aggregation_window_seconds: int = Field(60, gt=0, description="Окно агрегации событий, сек")
    attack_ttl_seconds: int = Field(900, gt=0, description="Время жизни атаки, сек")
    campaign_ttl_seconds: int = Field(1800, gt=0, description="Время жизни кампании, сек")


class IOCScoringConfig(BaseModel):
    """Надбавки к риску за совпадение с IOC и пороги оценки IOC по уровням."""
    boost_critical: int = Field(10, description="Надбавка за IOC уровня critical")
    boost_high: int = Field(10, description="Надбавка за IOC уровня high")
    boost_medium: int = Field(5, description="Надбавка за IOC уровня medium")
    boost_low: int = Field(0, description="Надбавка за IOC уровня low")
    min_score_critical: int = Field(90, ge=0, le=100, description="Минимальный score IOC для уровня critical")
    min_score_high: int = Field(70, ge=0, le=100, description="Минимальный score IOC для уровня high")
    min_score_medium: int = Field(50, ge=0, le=100, description="Минимальный score IOC для уровня medium")
    min_score_low: int = Field(30, ge=0, le=100, description="Минимальный score IOC для уровня low")

    @model_validator(mode="after")
    def check_order(self):
        if not (self.min_score_critical >= self.min_score_high >= self.min_score_medium >= self.min_score_low):
            raise ValueError("Пороги score IOC должны убывать: critical >= high >= medium >= low")
        return self


class AssetScoringConfig(BaseModel):
    """Надбавки к риску в зависимости от критичности актива."""
    boost_critical: int = Field(10, ge=0, le=100, description="Надбавка для критичного актива")
    boost_high: int = Field(5, ge=0, le=100, description="Надбавка для актива высокой критичности")
    boost_medium: int = Field(0, ge=0, le=100, description="Надбавка для актива средней критичности")
    boost_low: int = Field(0, ge=0, le=100, description="Надбавка для актива низкой критичности")


class DecisionConfig(BaseModel):
    """Пороги risk score для итоговой критичности."""
    critical_score: int = Field(90, ge=0, le=100, description="Порог critical")
    high_score: int = Field(70, ge=0, le=100, description="Порог high")
    medium_score: int = Field(50, ge=0, le=100, description="Порог medium")
    low_score: int = Field(30, ge=0, le=100, description="Порог low")

    @model_validator(mode="after")
    def check_order(self):
        if not (self.critical_score >= self.high_score >= self.medium_score >= self.low_score):
            raise ValueError("Пороги решений должны убывать: critical >= high >= medium >= low")
        return self


class AttackTrackerConfig(BaseModel):
    """Таймауты трекера атак и кампаний."""
    attack_timeout_minutes: int = Field(15, gt=0, description="Таймаут атаки, мин")
    campaign_timeout_minutes: int = Field(30, gt=0, description="Таймаут кампании, мин")


class EngineSettingsSchema(BaseModel):
    """Тело PUT /engine-settings и POST /engine-settings/validate (EngineSettings движка).

    updated_by подставляется из текущего пользователя, updated_at выставляет движок.
    """
    settings_id: str = Field("default", description="Идентификатор набора настроек")
    correlation: CorrelationConfig = Field(default_factory=CorrelationConfig)
    ioc_scoring: IOCScoringConfig = Field(default_factory=IOCScoringConfig)
    asset_scoring: AssetScoringConfig = Field(default_factory=AssetScoringConfig)
    decision: DecisionConfig = Field(default_factory=DecisionConfig)
    attack_tracker: AttackTrackerConfig = Field(default_factory=AttackTrackerConfig)


class EngineSettingsResponseSchema(EngineSettingsSchema):
    """Настройки движка в ответе GET /engine-settings."""
    updated_by: str = Field("system", description="Кто последним изменил настройки")
    updated_at: str | None = Field(None, description="Когда настройки изменены (ISO 8601)")


class EngineSettingsValidateResponseSchema(BaseModel):
    """Ответ POST /engine-settings/validate."""
    valid: bool = Field(..., description="Настройки корректны")
    settings: EngineSettingsResponseSchema = Field(..., description="Проверенные настройки")


class EngineSettingsUpdateResponseSchema(BaseModel):
    """Ответ PUT /engine-settings."""
    success: bool = Field(..., description="Настройки сохранены")
    settings: EngineSettingsResponseSchema = Field(..., description="Сохранённые настройки")
