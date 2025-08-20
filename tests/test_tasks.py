from uuid import UUID

import pytest


@pytest.fixture
def sample_task_payload():
    return {
        'title': 'тест название',
        'description': 'тест описание'
    }
    
    
@pytest.mark.anyio
async def test_health(client):
    r = await client.get('/health')
    status = r.json()['status']

    assert status == 'ok'
    

@pytest.mark.anyio
async def test_create_returns_task(client, sample_task_payload):
    r = await client.post('/create', json=sample_task_payload)
    
    assert r.status_code == 200
    
    data = r.json()
    
    assert set(['id', 'title', 'description', 'status']).issubset(data)
    assert data['title'] == sample_task_payload['title']
    assert str(data['status']).lower() == 'created'

    UUID(data['id'])


@pytest.mark.anyio
async def test_get_without_filters_returns_400(client):
    r = await client.get('/get')
    
    assert r.status_code == 400
    assert r.json()['detail'] == 'Нужно указать хотя бы один параметр'


@pytest.mark.anyio
async def test_filter_by_title(client, sample_task_payload):
    await client.post('/create', json=sample_task_payload)

    r = await client.get('/get', params={'title': sample_task_payload['title']})
    
    assert r.status_code == 200
    
    body = r.json()
    
    assert 'tasks' in body and isinstance(body['tasks'], list)
    assert any(t['title'] == sample_task_payload['title'] for t in body['tasks'])


@pytest.mark.anyio
async def test_update_and_get_by_id(client, sample_task_payload):
    r = await client.post('/create', json=sample_task_payload)
    
    task = r.json()
    task_id = task['id']

    new_desc = 'test_desc'
    r = await client.patch('/update', params={'id': task_id, 'description': new_desc})
    assert r.status_code == 200
    updated = r.json()
    assert updated['description'] == new_desc
    assert updated['title'] == sample_task_payload['title']

    r = await client.get('/get', params={'id': task_id})
    assert r.status_code == 200
    
    tasks = r.json()['tasks']
    
    assert len(tasks) == 1
    assert tasks[0]['id'] == task_id
    assert tasks[0]['description'] == new_desc


@pytest.mark.anyio
async def test_delete_then_404_on_get(client, sample_task_payload):
    r = await client.post('/create', json=sample_task_payload)
    task_id = r.json()['id']

    r = await client.delete('/delete', params={'id': task_id})
    assert r.status_code == 200
    assert r.json()['id'] == task_id

    r = await client.get('/get', params={'id': task_id})
    assert r.status_code == 404
    assert r.json()['detail'] == 'Задачи не найдены'
