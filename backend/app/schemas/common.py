from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str

    model_config = ConfigDict(from_attributes=True)


class ResponseEnvelope(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def success_response(cls, data: Any = None) -> "ResponseEnvelope":
        return cls(success=True, data=data, error=None)

    @classmethod
    def error_response(cls, code: str, message: str) -> "ResponseEnvelope":
        return cls(success=False, data=None, error=ErrorDetail(code=code, message=message))
