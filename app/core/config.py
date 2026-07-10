from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    supabase_url: str  # ej: https://ezpqfzjbauxluvxmqxvj.supabase.co
    cors_origins: str = "http://localhost:8081"
    admin_email: str = ""
    dispatcher_email: str = ""
    telegram_bot_token: str = ""
    # Service role de Supabase (Settings -> API -> service_role): solo para
    # borrar objetos de Storage al eliminar un pedido. Nunca se expone al
    # frontend. Si queda vacio, la limpieza de fotos simplemente se salta.
    supabase_service_role_key: str = ""

    @property
    def supabase_jwks_url(self) -> str:
        return f"{self.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
