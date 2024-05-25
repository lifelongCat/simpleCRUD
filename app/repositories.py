from abc import ABC, abstractmethod
from typing import Any, Union
from uuid import UUID
import json

from app.config import settings
from app.exceptions import MoreThanOneRecordException
from app.schemas import SMusicianInfo, SMusicianInfoWithRelationships


class AbstractRepository(ABC):
    @classmethod
    @abstractmethod
    async def create(cls, data: dict[str, Any]):
        pass

    @classmethod
    @abstractmethod
    async def find_one_or_none(cls, filter_by: dict[tuple[str, str], Any]):
        pass

    @classmethod
    @abstractmethod
    async def find_all(cls, limit: int, offset: int, filter_by: dict[tuple[str, str], Any] | None):
        pass

    @classmethod
    @abstractmethod
    async def update(cls, id: UUID, data: dict[str, Any]):
        pass

    @classmethod
    @abstractmethod
    async def delete(cls, id: UUID):
        pass


class SQLRepository(AbstractRepository):
    model = None
    model_pydantic_schema = None

    @classmethod
    async def create(cls, data: dict[str, Any]) -> UUID:
        async with settings.POSTGRES_POOL.acquire() as conn:
            record = await conn.fetchrow(f'''
                    INSERT INTO {cls.model} ({', '.join(data.keys())})
                    VALUES ({', '.join(f'${i}' for i in range(1, len(data) + 1))})
                    RETURNING id
                ''', *data.values())
        return record['id']

    @classmethod
    async def find_one_or_none(cls, filter_by: dict[str, Any]) -> Union[model_pydantic_schema, None]:
        async with settings.POSTGRES_POOL.acquire() as conn:
            records = await conn.fetch(f'''
                    SELECT *
                    FROM {cls.model}
                    WHERE {' AND '.join(f'{field_name} = ${field_index}'
                                        for field_index, field_name in enumerate(filter_by.keys(), 1))}
            ''', *filter_by.values())
        if not records:
            return None
        if len(records) != 1:
            raise MoreThanOneRecordException
        return cls.model_pydantic_schema(**records[0])

    @classmethod
    async def find_all(
            cls,
            limit: int,
            offset: int,
            filter_by: dict[tuple[str, str], Any] | None = None
    ) -> list[model_pydantic_schema]:
        async with settings.POSTGRES_POOL.acquire() as conn:
            records = await conn.fetch(f'''
                    SELECT *
                    FROM {cls.model}
                    {'WHERE' if filter_by else ''}
                    {' AND '.join(f'{field_name} {field_operation} ${field_index}'
                                  for field_index, (field_name, field_operation) in enumerate(filter_by.keys(), 1))}
                    {'ORDER BY 1' if not filter_by
                    else f'ORDER BY {", ".join(field_name for field_name, field_operation in filter_by.keys())}'}
                    LIMIT {limit}
                    OFFSET {offset}
            ''', *filter_by.values())
        return [cls.model_pydantic_schema(**record) for record in records]

    @classmethod
    async def update(cls, id: UUID, data: dict[str, Any]) -> UUID:
        async with settings.POSTGRES_POOL.acquire() as conn:
            record = await conn.fetchrow(f'''
                    UPDATE {cls.model} SET
                    {', '.join(f'{field_name} = ${field_index}'
                               for field_index, field_name in enumerate(data.keys(), 2))}
                    WHERE id = $1
                    RETURNING id
                ''', id, *data.values())
        return record['id']

    @classmethod
    async def delete(cls, id: UUID) -> str:
        async with settings.POSTGRES_POOL.acquire() as conn:
            operation_result = await conn.execute(f'''
                    DELETE FROM {cls.model}
                    WHERE id = $1
                ''', id)
        return operation_result


class MusiciansRepository(SQLRepository):
    model = 'music.musician'
    model_pydantic_schema = SMusicianInfo
    model_pydantic_schema_with_relationships = SMusicianInfoWithRelationships

    @classmethod
    async def find_all(
            cls,
            limit: int,
            offset: int,
            filter_by: dict[tuple[str, str], Any] | None = None
    ) -> list[model_pydantic_schema_with_relationships]:
        async with settings.POSTGRES_POOL.acquire() as conn:
            records = await conn.fetch(f'''
                WITH musicians_with_awards AS (
                    SELECT
                        m.id,
                        m.first_name,
                        m.last_name,
                        m.birth_date,
                        COALESCE(JSON_AGG(JSON_BUILD_OBJECT(
                            'id', aw.id, 'title', aw.title, 'year', aw.year
                            )) FILTER (WHERE aw.id IS NOT NULL), '[]'
                        ) as awards
                    FROM music.musician m
                    LEFT JOIN music.award aw on m.id = aw.musician_id
                    GROUP BY m.id
                ), musicians_with_pieces AS (
                    SELECT
                        m.id,
                        m.first_name,
                        m.last_name,
                        m.birth_date,
                        COALESCE(JSON_AGG(JSON_BUILD_OBJECT(
                            'id', p.id, 'title', p.title, 'genre', p.genre, 'duration', p.duration
                            )) FILTER (WHERE mp.musician_id IS NOT NULL), '[]'
                        ) as pieces
                    FROM music.musician m
                    LEFT JOIN music.musician_to_piece mp ON m.id = mp.musician_id
                    LEFT JOIN music.music_piece p ON p.id = mp.piece_id
                    GROUP BY m.id
                )

                SELECT mwa.id, mwa.first_name, mwa.last_name, mwa.birth_date, mwa.awards, mwp.pieces
                FROM musicians_with_awards mwa
                JOIN musicians_with_pieces mwp ON mwa.id = mwp.id
                {'WHERE' if filter_by else ''}
                {' AND '.join(f'mwa.{name_} {operation_} ${index_}'
                              for index_, (name_, operation_) in enumerate(filter_by.keys(), 1))}
                {'ORDER BY 1' if not filter_by
                else f'ORDER BY {", ".join(name_ for name_, operation_ in filter_by.keys())}'}
                LIMIT {limit}
                OFFSET {offset};
            ''', *filter_by.values())
        return [cls.model_pydantic_schema_with_relationships(**record) for record in records]
