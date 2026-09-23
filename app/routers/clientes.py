from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, or_

from app.database import obter_sessao
from app.models import (
    Clientes,
    ClientesCreate,
    ClientesUpdate,
    ClientesResponse,
)

router = APIRouter(prefix='/clientes', tags=["Clientes"])

# endsPoints METHOD + PATH, Ex.: "Get /cliente/18"
@router.get("/", response_model=list[ClientesResponse], summary="Listar Clientes")
def listar_clientes(
    busca: str | None = Query(default=None, description="Buscar por termo no nome ou descrição"),
    sessao: Session = Depends(obter_sessao),
):
    if busca:
        termo = f"%{busca}%"
        query = query.where(
            or_(
                Clientes.nome.ilike(termo),
            )
        )

    # Ordenar por ID para manter listagem consistente
    query = query.order_by(Clientes.id)
    cliente = sessao.exec(query).all()
    return cliente

@router.get('/{id}')
def obter_cliente(id: int):
    return f'Cliente de ID={id}'

@router.post('/')
def criar_cliente():
    return ''

@router.put('/{id}')
def atualizar_cliente(id: int):
    return ''
