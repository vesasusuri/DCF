from pydantic import BaseModel, EmailStr, Field


class CreatePortfolioManagerRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=255)


class AssignPortfolioManagerRequest(BaseModel):
    user_id: str


class PortfolioManagerResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    role: str
    created_at: str | None = None


class PortfolioManagerAssignmentResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    assigned_by: str | None
    assigned_at: str
    user_email: str | None = None
    user_full_name: str | None = None
