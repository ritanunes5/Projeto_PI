from pydantic import BaseModel, Field, constr
from datetime import datetime, date


# USERS

class UserCreate(BaseModel):
    nome: str
    email: str
    password: str
    role: str
    codigo_admin: str | None = None
    codigo: str | None = Field(default=None, min_length=4, max_length=4)
    numero_identificacao: str = Field(min_length=9, max_length=9)
    telefone: str | None = Field(default=None, min_length=9, max_length=9)
    freguesia: str | None = None
    data_nascimento: date | None = None
    recenseado: bool = False


class UserResponse(BaseModel):
    id: int
    nome: str
    email: str
    role: str

    class Config:
        from_attributes = True

class EleitorCCLogin(BaseModel):
    numero_cc: constr(min_length=9, max_length=9)

class EleitorResponse(BaseModel):
    id: int
    nome: str
    numero_cc: str
    freguesia: str

    class Config:
        from_attributes = True


# ELECTIONS

class ElectionCreate(BaseModel):
    titulo: str
    descricao: str
    data_inicio: datetime
    data_fim: datetime
    estado: str
    created_by: int

class ElectionResponse(BaseModel):
    id: int
    titulo: str
    descricao: str

    class Config:
        from_attributes = True


# CANDIDATES

class CandidateCreate(BaseModel):
    election_id: int
    nome: str
    partido: str
    slogan: str
    descricao: str
    campanha: str
    foto: str

class CandidateResponse(BaseModel):
    id: int
    election_id: int
    nome: str
    partido: str

    class Config:
        from_attributes = True


class ElectionCreate(BaseModel):
    titulo: str
    descricao: str
    data_inicio: datetime
    data_fim: datetime
    estado: str
    created_by: int


class ElectionResponse(BaseModel):
    id: int
    titulo: str
    descricao: str
    estado: str

    class Config:
        from_attributes = True


# VOTES

class VoteCreate(BaseModel):
    election_id: int
    candidate_id: int


class VoteResponse(BaseModel):
    id: int
    election_id: int
    candidate_id: int
    token_voto: str

    class Config:
        from_attributes = True

# VOTES STATUS

class VoteStatusCreate(BaseModel):
    user_id: int
    election_id: int


class VoteStatusResponse(BaseModel):
    id: int
    user_id: int
    election_id: int
    ja_votou: bool

    class Config:
        from_attributes = True

class CastVoteCreate(BaseModel):
    user_id: int
    election_id: int
    candidate_id: int

# LOGIN

class LoginAdminRequest(BaseModel):
    email_institucional: str
    password: str
    codigo_admin: str

class LoginCCRequest(BaseModel):
    numero_identificacao: str = Field(min_length=9, max_length=9)

class LoginRecenseamentoRequest(BaseModel):
    numero_identificacao: str = Field(min_length=9, max_length=9)
    data_nascimento: date
    freguesia: str

class LoginCMDRequest(BaseModel):
    telefone: str = Field(min_length=9, max_length=9)
    codigo: str