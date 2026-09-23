from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query ,status
from sqlmodel import Session, select, or_

from app.database import obter_sessao
from app.models import (
    Clientes,
    ClientesCreate,
    ClientesResponse,
    ClientesUpdate,
)

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("/", response_model=ClientesResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar novo cliente")
def criar_cliente(cliente: ClientesCreate, session: Session = Depends(obter_sessao)):
    novo_cliente = Clientes.model_validate(cliente)
    session.add(novo_cliente)
    session.commit()
    session.refresh(novo_cliente)
    return novo_cliente


@router.get("/", response_model=List[ClientesResponse], summary="Listar e buscar clientes com paginação")
def listar_clientes(
    busca: str | None = Query(
        default=None,
        description="Termo de busca para filtrar por nome, e-mail ou CPF"
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Número de registros a ignorar (offset para paginação)"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Quantidade máxima de registros a retornar"
    ),
    session: Session = Depends(obter_sessao)
):
    query = select(Clientes)
    if busca:
        query = query.where(
            or_(
                Clientes.nome.contains(busca),
                Clientes.email.contains(busca),
                Clientes.cpf.contains(busca)
            )
        )
    clientes = session.exec(query.offset(skip).limit(limit)).all()
    return clientes


@router.get("/{cliente_id}", response_model=ClientesResponse, summary="Buscar cliente por ID")
def buscar_cliente_por_id(cliente_id: int = Path(description="Identificador único (ID) do cliente") , session: Session = Depends(obter_sessao)):
    cliente = session.get(Clientes, cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    return cliente


@router.put("/{cliente_id}", response_model=ClientesResponse, summary="Atualizar dados do cliente")
def atualizar_cliente(
    cliente_id: int = Path(description="ID do cliente que terá os dados atualizados"),
    cliente_data: ClientesUpdate = ...,
    session: Session = Depends(obter_sessao)
):
    cliente_db = session.get(Clientes, cliente_id)
    if not cliente_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    dados_atualizados = cliente_data.model_dump(exclude_unset=True)
    for chave, valor in dados_atualizados.items():
        setattr(cliente_db, chave, valor)

    session.add(cliente_db)
    session.commit()
    session.refresh(cliente_db)
    return cliente_db


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir cliente")
def deletar_cliente(cliente_id: int = Path(description="ID do cliente a ser removido do sistema"), session: Session = Depends(obter_sessao)):
    cliente = session.get(Clientes, cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    session.delete(cliente)
    session.commit()
    return None