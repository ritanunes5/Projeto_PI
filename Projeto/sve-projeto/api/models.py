from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from database import Base


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    numero_identificacao = Column(String(30), unique=True, nullable=False)
    codigo_admin = Column(String(20), nullable=True)
    codigo = Column(String(4), nullable=True)
    telefone = Column(String(20))
    freguesia = Column(String(100))
    data_nascimento = Column(Date)
    recenseado = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class EleitorDB(Base):
    __tablename__ = "eleitores"

    id = Column(Integer, primary_key=True, index=True)
    numero_cc = Column(String(9), unique=True, nullable=False, index=True)
    nome = Column(String(100), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    freguesia = Column(String(100), nullable=False)
    telefone = Column(String(9), nullable=True)

class ElectionDB(Base):
    __tablename__ = "elections"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(Text)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    estado = Column(String(30), default="rascunho")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())


class CandidateDB(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    election_id = Column(Integer, ForeignKey("elections.id"))
    nome = Column(String(100), nullable=False)
    partido = Column(String(100))
    slogan = Column(String(150))
    descricao = Column(Text)
    campanha = Column(Text)
    foto = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())


class VoteDB(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    election_id = Column(Integer, ForeignKey("elections.id"))
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    token_voto = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class VoteStatusDB(Base):
    __tablename__ = "vote_status"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    election_id = Column(Integer, ForeignKey("elections.id"))
    ja_votou = Column(Boolean, default=False)
    voted_at = Column(DateTime)


class AuthCodeDB(Base):
    __tablename__ = "auth_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tipo = Column(String(30), nullable=False)
    codigo = Column(String(10), nullable=False)
    usado = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class AuditLogDB(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    acao = Column(String(255), nullable=False)
    detalhes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
