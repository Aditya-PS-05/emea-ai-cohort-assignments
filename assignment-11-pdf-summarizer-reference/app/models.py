from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class RootResponse(BaseModel):
    message: str


class UploadPDFResponse(BaseModel):
    filename: str
    character_count: int
    extracted_text: str


class ChunkPreview(BaseModel):
    chunk_number: int
    char_count: int
    preview: str


class UploadPDFChunkedResponse(BaseModel):
    filename: str
    character_count: int
    total_chunks: int
    chunks_preview: list[ChunkPreview]


class SummarizePDFResponse(BaseModel):
    filename: str
    character_count: int
    total_chunks: int
    chunk_summaries: list[str]
    final_summary: str


class WebSocketUploadRequest(BaseModel):
    """
    Client WebSocket-ku anuppura JSON message-oda shape.
    file_base64 max length check pannuvom - romba periya files
    accidental ah anupparadha thadukka.
    """
    filename: str = Field(..., min_length=1, max_length=255)
    file_base64: str = Field(..., min_length=1)


class ErrorResponse(BaseModel):
    detail: str