"""在笔记根目录运行：python -m pytest -q demos/test_demos.py。"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from demos import ch01, ch02, ch03, ch04, ch05, ch06
from demos import ch07, ch08, ch09, ch10, ch11, ch12


def test_hello():
    with TestClient(ch01.app) as client:
        assert client.get('/hello').json() == {'message': 'Hello FastAPI'}


def test_parameters():
    with TestClient(ch02.app) as client:
        assert client.get('/tasks/3?limit=5').json() == {
            'task_id': 3, 'limit': 5, 'keyword': None}
        for path in ['/tasks/abc', '/tasks/0', '/tasks/1?limit=51', '/tasks/search']:
            assert client.get(path).status_code == 422
        assert client.get('/tasks/search?q=hello').json() == {'q': 'hello'}


def test_body():
    with TestClient(ch03.app) as client:
        response = client.post('/tasks', json={'title': '学习'})
        assert response.status_code == 201
        assert response.json() == {'title': '学习', 'priority': 1, 'tags': []}
        for body in [{'title': ''}, {'title': '学习', 'priority': 4},
                     {'title': '学习', 'unknown': 1}, {}]:
            assert client.post('/tasks', json=body).status_code == 422


def test_response_filter_and_error():
    with TestClient(ch04.app) as client:
        assert client.get('/tasks/1').json() == {'id': 1, 'title': '复习'}
        response = client.get('/tasks/9')
        assert response.status_code == 404
        assert response.json() == {'detail': '任务不存在'}


def test_dependencies():
    with TestClient(ch05.app) as client:
        assert client.get('/tasks?offset=1&limit=1').json() == ['写代码']
        assert client.get('/tasks?limit=0').status_code == 422


def test_async_and_stream_content():
    # TestClient 验证完整内容；不验证网络分块到达时机。
    with TestClient(ch06.app) as client:
        assert client.get('/wait').json() == {'done': True}
        response = client.get('/stream')
        assert response.text == '你好\n，\nFastAPI\n'
        assert response.headers['content-type'].startswith('text/plain')


def test_router():
    with TestClient(ch07.app) as client:
        assert client.get('/api/v1/tasks').json() == [{'id': 1, 'title': '拆分路由'}]
        assert client.get('/tasks').status_code == 404


@pytest.fixture
def db_client(monkeypatch):
    # 用内存库替换引擎：测试不会读写 demo 的持久数据库。
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False},
                           poolclass=StaticPool)
    monkeypatch.setattr(ch08, 'engine', engine)
    with TestClient(ch08.app) as client:
        yield client


def test_database_crud(db_client):
    client = db_client
    assert client.post('/tasks', json={'title': ''}).status_code == 422
    response = client.post('/tasks', json={'title': '学习数据库'})
    assert response.status_code == 201
    task_id = response.json()['id']
    assert client.get(f'/tasks/{task_id}').json()['title'] == '学习数据库'
    assert len(client.get('/tasks').json()) == 1
    response = client.put(f'/tasks/{task_id}', json={'title': '已经学会'})
    assert response.status_code == 200
    assert response.json()['title'] == '已经学会'
    response = client.delete(f'/tasks/{task_id}')
    assert response.status_code == 204
    assert response.content == b''
    assert client.get(f'/tasks/{task_id}').status_code == 404
    assert client.delete(f'/tasks/{task_id}').status_code == 404


def test_auth():
    with TestClient(ch09.app) as client:
        for headers in [{}, {'Authorization': 'Bearer wrong'}]:
            response = client.get('/me', headers=headers)
            assert response.status_code == 401
            assert response.headers['www-authenticate'] == 'Bearer'
        assert client.get('/me', headers={'Authorization': 'Bearer demo-token'}).json() == {
            'id': 1, 'name': '学习者'}


def test_upload():
    with TestClient(ch10.app) as client:
        response = client.post('/upload', files={'file': ('a.txt', b'hello', 'text/plain')},
                               data={'note': '测试'}, headers={'X-Request-ID': 'abc'})
        assert response.status_code == 200
        assert response.json() == {'filename': 'a.txt', 'size': 5,
                                   'note': '测试', 'request_id': 'abc'}
        assert client.post('/upload').status_code == 422


def test_lifespan_cors_background(capsys):
    with TestClient(ch11.app) as client:
        assert ch11.app.state.ready is True
        response = client.post('/events', headers={'Origin': 'http://localhost:5173'})
        assert response.status_code == 202
        assert response.json() == {'accepted': True}
        assert float(response.headers['x-process-time']) >= 0
        assert response.headers['access-control-allow-origin'] == 'http://localhost:5173'
        assert '后台任务: 收到事件' in capsys.readouterr().out
        preflight = client.options('/events', headers={
            'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'POST'})
        assert preflight.status_code == 200
        denied = client.options('/events', headers={
            'Origin': 'http://untrusted.example', 'Access-Control-Request-Method': 'POST'})
        assert denied.status_code == 400
    assert ch11.app.state.ready is False


def test_settings_and_health(monkeypatch):
    monkeypatch.setenv('DEMO_APP_NAME', '测试服务')
    assert ch12.Settings().app_name == '测试服务'
    with TestClient(ch12.app) as client:
        assert client.get('/health').json()['status'] == 'ok'


@pytest.mark.parametrize('module', [ch01, ch02, ch03, ch04, ch05, ch06,
                                   ch07, ch08, ch09, ch10, ch11, ch12])
def test_openapi(module):
    assert module.app.openapi()['paths']
