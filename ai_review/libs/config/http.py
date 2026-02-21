from pydantic import BaseModel, HttpUrl, SecretStr, FilePath, model_validator


class HTTPClientConfig(BaseModel):
    verify: FilePath | bool | None = True
    timeout: float = 120
    api_url: HttpUrl

    @property
    def api_url_value(self) -> str:
        return str(self.api_url)


class HTTPClientWithTokenConfig(HTTPClientConfig):
    api_token: SecretStr | None = None
    api_token_scheme: str = ""

    @model_validator(mode="after")
    def validate_api_token_scheme(self):
        if self.api_token and not self.api_token_scheme.strip():
            raise ValueError("api_token_scheme is required when api_token is set")
        return self

    @property
    def api_token_value(self) -> str:
        return self.api_token.get_secret_value() if self.api_token else ""

    @property
    def authorization_header_value(self) -> str:
        scheme = self.api_token_scheme.strip()
        token = self.api_token_value
        return f"{scheme} {token}".strip() if token and scheme else ""

    @property
    def authorization_headers(self) -> dict[str, str]:
        value = self.authorization_header_value
        return {"Authorization": value} if value else {}
