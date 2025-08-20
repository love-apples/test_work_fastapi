from pydantic_settings import BaseSettings


class MongoConfig(BaseSettings):
    NAME: str
    PORT: int
    HOST: str

    class Config:
        env_prefix = 'Mongo_'
        env_file = '.env'
        extra = 'ignore'

    @property
    def URL(self) -> str:
        return f"mongodb://{self.HOST}:{self.PORT}/{self.NAME}"


class Config:
    mongo = MongoConfig()  # type: ignore


cnf = Config()