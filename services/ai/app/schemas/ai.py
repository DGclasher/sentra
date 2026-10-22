from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500,
                       description="The query string to search for.")
    top_k: int = Field(default=5, ge=1, le=15,
                       description="The number of top results to return.")


class QueryResponseItem(BaseModel):
    content: str = Field(description="The content of the document chunk.")
    score: float = Field(
        description="The similarity score of the document chunk.")


class QueryResponse(BaseModel):
    response: str = Field(
        description="The answer generated from retrieved context.")
