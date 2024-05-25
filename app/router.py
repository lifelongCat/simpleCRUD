from datetime import date
from uuid import UUID

from fastapi import APIRouter, Response, status

from app.exceptions import MusicianNotFoundException
from app.repositories import MusiciansRepository
from app.schemas import SMusician, SMusicianInfo, SMusicianInfoWithRelationships

router = APIRouter(
    prefix='/musicians',
    tags=['CRUD']
)


@router.get('', status_code=status.HTTP_200_OK)
async def get_musicians(
        limit: int = 10,
        offset: int = 0,
        first_name: str | None = None,
        last_name: str | None = None,
        birth_date: date | None = None
) -> list[SMusicianInfoWithRelationships]:
    # попробовать фильтр
    filter_by = {}
    filter_by |= {('first_name', 'ilike'): f'%{first_name}%'} if first_name else {}
    filter_by |= {('last_name', 'ilike'): f'%{last_name}%'} if last_name else {}
    filter_by |= {('birth_date', '='): birth_date} if birth_date else {}
    musicians = await MusiciansRepository.find_all(limit, offset, filter_by)
    return musicians


@router.get('/{musician_id}', status_code=status.HTTP_200_OK)
async def get_one_musician(
        musician_id: UUID,
) -> SMusicianInfo:
    musician = await MusiciansRepository.find_one_or_none({'id': musician_id})
    if not musician:
        raise MusicianNotFoundException
    return musician


@router.post('', status_code=status.HTTP_201_CREATED)
async def create_musician(
        musician: SMusician,
) -> dict[str, UUID]:
    musician_id = await MusiciansRepository.create(musician.model_dump())
    return {'id': musician_id}


@router.put('/{musician_id}')
async def update_musician(
        musician_id: UUID,
        musician: SMusician,
        response: Response
) -> dict[str, UUID]:
    if not await MusiciansRepository.find_one_or_none({'id': musician_id}):
        musician_id = await MusiciansRepository.create({'id': musician_id, **musician.model_dump()})
        response.status_code = status.HTTP_201_CREATED
    else:
        musician_id = await MusiciansRepository.update(musician_id, musician.model_dump())
        response.status_code = status.HTTP_200_OK
    return {'id': musician_id}


@router.delete('/{musician_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_musician(
        musician_id: UUID,
) -> None:
    operation_result = await MusiciansRepository.delete(musician_id)
    if operation_result == 'DELETE 0':
        raise MusicianNotFoundException
    return None
