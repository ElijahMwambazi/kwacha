from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Kwacha!"
    database_url: str = "sqlite:///./backend/data/kwacha.db"


settings = Settings()
