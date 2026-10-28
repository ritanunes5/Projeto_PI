from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
import time
from datetime import datetime

from database import engine, Base, SessionLocal
import models
import schemas

import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for _ in range(10):
    try:
        Base.metadata.create_all(bind=engine)
        print("Base de dados ligada com sucesso.")
        break
    except OperationalError:
        print("MariaDB ainda não está pronta. A tentar novamente...")
        time.sleep(3)

def maior_de_idade(data_nascimento):
    hoje = datetime.today()

    idade = (
        hoje.year
        - data_nascimento.year
        - (
            (hoje.month, hoje.day)
            < (data_nascimento.month, data_nascimento.day)
        )
    )

    return idade >= 18

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "API do Sistema de Votação Eletrónica ativa"}


@app.get("/health")
def health():
    return {"status": "ok"}

def maior_de_idade(data_nascimento):
    hoje = datetime.today()

    idade = (
        hoje.year
        - data_nascimento.year
        - (
            (hoje.month, hoje.day)
            < (data_nascimento.month, data_nascimento.day)
        )
    )

    return idade >= 18

# CRIAR UTILIZADOR

@app.post("/criar_conta")
def criar_conta(dados: schemas.UserCreate, db: Session = Depends(get_db)):

    novo_user = models.UserDB(
        nome=dados.nome,
        numero_identificacao=dados.numero_identificacao,
        data_nascimento=dados.data_nascimento,
        role="eleitor",
        recenseado=True
    )

    db.add(novo_user)
    db.commit()
    db.refresh(novo_user)

    return novo_user

@app.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    novo_user = models.UserDB(**user.model_dump())
    db.add(novo_user)
    db.commit()
    db.refresh(novo_user)
    return novo_user


@app.get("/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.UserDB).all()

# ELIMINAR UTILIZADOR

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.UserDB).filter(
        models.UserDB.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado")

    db.delete(user)
    db.commit()

    return {"message": "Utilizador eliminado"}

# CRIAR ELEIÇÃO

@app.post("/elections", response_model=schemas.ElectionResponse)
def create_election(
    election: schemas.ElectionCreate,
    db: Session = Depends(get_db)
):
    nova_eleicao = models.ElectionDB(**election.model_dump())

    db.add(nova_eleicao)
    db.commit()
    db.refresh(nova_eleicao)

    return nova_eleicao


@app.get("/elections", response_model=list[schemas.ElectionResponse])
def get_elections(db: Session = Depends(get_db)):
    return db.query(models.ElectionDB).all()

# CRIAR CANDIDATO

@app.post("/candidates", response_model=schemas.CandidateResponse)
def create_candidate(
    candidate: schemas.CandidateCreate,
    db: Session = Depends(get_db)
):
    candidato_existente = db.query(models.CandidateDB).filter(
        models.CandidateDB.election_id == candidate.election_id,
        models.CandidateDB.nome == candidate.nome
    ).first()

    if candidato_existente:
        raise HTTPException(
            status_code=400,
            detail="Este candidato já está registado nesta eleição."
        )

    novo_candidato = models.CandidateDB(**candidate.model_dump())

    db.add(novo_candidato)
    db.commit()
    db.refresh(novo_candidato)

    return novo_candidato


@app.get("/candidates/{election_id}",
         response_model=list[schemas.CandidateResponse])
def get_candidates_by_election(
    election_id: int,
    db: Session = Depends(get_db)
):
    return db.query(models.CandidateDB).filter(
        models.CandidateDB.election_id == election_id
    ).all()

# CRIAR VOTO

@app.post("/votes", response_model=schemas.VoteResponse)
def create_vote(
    vote: schemas.VoteCreate,
    db: Session = Depends(get_db)
):
    novo_voto = models.VoteDB(
        election_id=vote.election_id,
        candidate_id=vote.candidate_id,
        token_voto=str(uuid.uuid4())
    )

    db.add(novo_voto)
    db.commit()
    db.refresh(novo_voto)

    return novo_voto

# REGRA PARA EVITAR VOTO DUPLICADO: VER SE O UTILIZADOR JÁ VOTOU NA ELEIÇÃO, SE SIM, NÃO PERMITIR NOVO VOTO

@app.post("/cast-vote", response_model=schemas.VoteResponse)
def cast_vote(vote: schemas.CastVoteCreate, db: Session = Depends(get_db)):
    status_existente = db.query(models.VoteStatusDB).filter(
        models.VoteStatusDB.user_id == vote.user_id,
        models.VoteStatusDB.election_id == vote.election_id,
        models.VoteStatusDB.ja_votou == True
    ).first()

    if status_existente:
        raise HTTPException(status_code=400, detail="Este utilizador já votou nesta eleição.")

    novo_voto = models.VoteDB(
        election_id=vote.election_id,
        candidate_id=vote.candidate_id,
        token_voto=str(uuid.uuid4())
    )

    db.add(novo_voto)

    novo_status = models.VoteStatusDB(
        user_id=vote.user_id,
        election_id=vote.election_id,
        ja_votou=True,
        voted_at=datetime.now()
    )

    db.add(novo_status)
    db.commit()
    db.refresh(novo_voto)

    return novo_voto

@app.get("/votes", response_model=list[schemas.VoteResponse])
def get_votes(db: Session = Depends(get_db)):
    return db.query(models.VoteDB).all()

@app.post("/vote-status", response_model=schemas.VoteStatusResponse)
def create_vote_status(
    status: schemas.VoteStatusCreate,
    db: Session = Depends(get_db)
):
    novo_status = models.VoteStatusDB(
        user_id=status.user_id,
        election_id=status.election_id,
        ja_votou=True
    )

    db.add(novo_status)
    db.commit()
    db.refresh(novo_status)

    return novo_status


@app.get("/vote-status", response_model=list[schemas.VoteStatusResponse])
def get_vote_status(db: Session = Depends(get_db)):
    return db.query(models.VoteStatusDB).all()

@app.post("/login_admin", response_model=schemas.UserResponse)
def login_admin(
    dados: schemas.LoginAdminRequest,
    db: Session = Depends(get_db)
):
    user = db.query(models.UserDB).filter(
        models.UserDB.email == dados.email_institucional,
        models.UserDB.password == dados.password
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Email ou password inválidos.")

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso reservado a administradores.")

    if user.codigo_admin != dados.codigo_admin:
        raise HTTPException(status_code=401, detail="Código de administrador inválido.")

    return user

@app.post("/login_cc")
def login_cc(dados: schemas.LoginCCRequest, db: Session = Depends(get_db)):
    user = db.query(models.UserDB).filter(
        models.UserDB.numero_identificacao == dados.numero_identificacao,
        models.UserDB.role == "eleitor",
        models.UserDB.recenseado == True
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Dados do Cartão de Cidadão inválidos.")

    if not maior_de_idade(user.data_nascimento):
        raise HTTPException(
            status_code=403,
            detail="Utilizador menor de idade não pode votar."
        )

    return {
        "id": user.id,
        "nome": user.nome,
        "numero_identificacao": user.numero_identificacao,
        "role": user.role
    }


@app.post("/login_cmd", response_model=schemas.UserResponse)
def login_cmd(dados: schemas.LoginCMDRequest, db: Session = Depends(get_db)):
    user = db.query(models.UserDB).filter(
        models.UserDB.telefone == dados.telefone,
        models.UserDB.codigo == dados.codigo,
        models.UserDB.role == "eleitor",
        models.UserDB.recenseado == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Telefone ou PIN inválidos."
        )

    if not maior_de_idade(user.data_nascimento):
        raise HTTPException(
            status_code=403,
            detail="Utilizador menor de idade não pode votar."
        )

    return user


@app.post("/login_recenseamento", response_model=schemas.UserResponse)
def login_recenseamento(dados: schemas.LoginRecenseamentoRequest, db: Session = Depends(get_db)):
    user = db.query(models.UserDB).filter(
        models.UserDB.numero_identificacao == dados.numero_identificacao,
        models.UserDB.freguesia == dados.freguesia,
        models.UserDB.data_nascimento == dados.data_nascimento,
        models.UserDB.role == "eleitor",
        models.UserDB.recenseado == True
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Dados de recenseamento inválidos.")
    
    if not maior_de_idade(user.data_nascimento):
        raise HTTPException(status_code=403, detail="Utilizador menor de idade não pode votar."
    )
    return user