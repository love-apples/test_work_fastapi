from contextlib import asynccontextmanager
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import cnf
from app.enums import TaskStatus
from app.models import TaskModel
from app.schemas import FetchTasksSchema, TaskCreateSchema, TaskSchema


@asynccontextmanager
async def lifespan(app: FastAPI):
    client: AsyncIOMotorClient = AsyncIOMotorClient(cnf.mongo.URL)
    app.state.mongo_client = client

    await init_beanie(
        database=client[cnf.mongo.NAME],  # type: ignore
        document_models=[TaskModel],
    )

    try:
        yield
    finally:
        client.close()


app = FastAPI(lifespan=lifespan)


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.post(
    '/create',
    response_model=TaskSchema,
    summary='Создать задачу',
    description='Возвращает объект созданной задачи',
)
async def create(data: TaskCreateSchema) -> TaskSchema:
    raw_data = data.model_dump()
    task = await TaskModel(**raw_data, status=TaskStatus.CREATED).insert()
    return task


@app.get(
    '/get',
    response_model=FetchTasksSchema,
    summary='Найти задачи по полям',
    description=(
        'Возвращает список задач по любому сочетанию фильтров. '
        'Если не передан ни один параметр — 400.'
    ),
)
async def get_task(
    id: Optional[UUID] = Query(None),
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    status: Optional[TaskStatus] = Query(None),
) -> FetchTasksSchema:
    query: Dict[str, Any] = {}
    
    if id:
        query['_id'] = id
    if title:
        query['title'] = title
    if description:
        query['description'] = description
    if status:
        query['status'] = status

    if not query:
        raise HTTPException(status_code=400, detail='Нужно указать хотя бы один параметр')

    tasks = await TaskModel.find(query).to_list()
    if not tasks:
        raise HTTPException(status_code=404, detail='Задачи не найдены')

    task_schemas = [TaskSchema(**task.model_dump()) for task in tasks]
    return FetchTasksSchema(tasks=task_schemas)


@app.patch(
    '/update',
    response_model=TaskSchema,
    summary='Обновить задачу по ID',
    description='Возвращает объект обновленной задачи. Если задача не найдена — 400.',
)
async def update(
    id: UUID,
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    status: Optional[TaskStatus] = Query(None),
) -> TaskSchema:
    task = await TaskModel.find_one(TaskModel.id == id)
    if not task:
        raise HTTPException(status_code=404, detail='Задача не найдена')

    if title:
        task.title = title
    if description:
        task.description = description
    if status:
        task.status = status

    await task.save()
    return TaskSchema(**task.model_dump())


@app.delete(
    '/delete',
    response_model=TaskSchema,
    summary='Удалить задачу по ID',
    description='Возвращает объект удаленной задачи. Если задача не найдена — 400.',
)
async def delete(id: UUID) -> TaskSchema:
    task = await TaskModel.find_one(TaskModel.id == id)
    if not task:
        raise HTTPException(status_code=404, detail='Задача не найдена')

    await task.delete()
    return TaskSchema(**task.model_dump())
