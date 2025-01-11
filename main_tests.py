import os
import pytest
from fastapi.testclient import TestClient
from main import app, BASE_DIR

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    # Create a temporary test directory
    os.makedirs(BASE_DIR, exist_ok=True)
    yield
    # Clean up after each test
    for root, dirs, files in os.walk(BASE_DIR, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))


def test_list_files_empty():
    response = client.get("/files")
    assert response.status_code == 200
    assert response.json() == {
        "page": 1,
        "per_page": 100,
        "total_files": 0,
        "files": []
    }


def test_create_and_list_file():
    response = client.post("/files", json={"file_name": "test.txt", "content": "Hello World"})
    assert response.status_code == 201
    assert response.json()["message"] == "File created successfully"

    response = client.get("/files")
    assert response.status_code == 200
    assert len(response.json()["files"]) == 1
    assert response.json()["files"][0]["file_name"] == "test.txt"


def test_create_nested_file():
    response = client.post("/files", json={"file_name": "nested/dir/test.txt", "content": "Nested Hello"})
    assert response.status_code == 201
    assert response.json()["message"] == "File created successfully"

    response = client.get("/files")
    assert response.status_code == 200
    assert len(response.json()["files"]) == 1
    assert response.json()["files"][0]["file_name"] == "nested/dir/test.txt"


def test_view_file():
    client.post("/files", json={"file_name": "view.txt", "content": "View Content"})
    response = client.get("/files/view.txt")
    assert response.status_code == 200
    assert response.json()["content"] == "View Content"


def test_update_file():
    client.post("/files", json={"file_name": "update.txt", "content": "Old Content"})
    response = client.put("/files/update.txt", json={"file_name": "update.txt", "content": "New Content"})
    assert response.status_code == 200
    assert response.json()["message"] == "File updated successfully"

    response = client.get("/files/update.txt")
    assert response.status_code == 200
    assert response.json()["content"] == "New Content"


def test_delete_file():
    client.post("/files", json={"file_name": "delete.txt", "content": "To be deleted"})
    response = client.delete("/files/delete.txt")
    assert response.status_code == 200
    assert response.json()["message"] == "File deleted successfully"

    response = client.get("/files/delete.txt")
    assert response.status_code == 404


def test_prohibit_git_directory_operations():
    response = client.post("/files", json={"file_name": ".git/test.txt", "content": "Forbidden"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Operation not allowed on .git directory"


def test_non_existing_file():
    response = client.get("/files/nonexistent.txt")
    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"


def test_special_characters_in_filename():
    response = client.post("/files", json={"file_name": "special_!@#.txt", "content": "Special"})
    assert response.status_code == 201
    assert response.json()["message"] == "File created successfully"

    response = client.get("/files/special_!@#.txt")
    assert response.status_code == 200
    assert response.json()["content"] == "Special"
