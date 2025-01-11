import os
import pytest
from fastapi.testclient import TestClient
from main import app, BASE_DIR, USERNAME, PASSWORD
import urllib.parse

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

auth = (USERNAME, PASSWORD)

def test_list_files_empty():
    response = client.get("/files", auth=auth)
    assert response.status_code == 200
    assert response.json() == {
        "page": 1,
        "per_page": 100,
        "total_files": 0,
        "files": []
    }

def test_create_and_list_file():
    response = client.post("/files", json={"file_name": "test.txt", "content": "Hello World"}, auth=auth)
    assert response.status_code == 201
    assert response.json()["message"] == "File created successfully"

    response = client.get("/files", auth=auth)
    assert response.status_code == 200
    assert len(response.json()["files"]) == 1
    assert response.json()["files"][0]["file_name"] == "test.txt"

def test_create_nested_file():
    response = client.post("/files", json={"file_name": "nested/dir/test.txt", "content": "Nested Hello"}, auth=auth)
    assert response.status_code == 201
    assert response.json()["message"] == "File created successfully"

    response = client.get("/files", auth=auth)
    assert response.status_code == 200
    assert len(response.json()["files"]) == 1
    assert response.json()["files"][0]["file_name"] == "nested/dir/test.txt"

def test_view_file():
    client.post("/files", json={"file_name": "view.txt", "content": "View Content"}, auth=auth)
    response = client.get("/files/view.txt", auth=auth)
    assert response.status_code == 200
    assert response.json()["content"] == "View Content"

def test_update_file():
    client.post("/files", json={"file_name": "update.txt", "content": "Old Content"}, auth=auth)
    response = client.put("/files/update.txt", json={"file_name": "update.txt", "content": "New Content"}, auth=auth)
    assert response.status_code == 200
    assert response.json()["message"] == "File updated successfully"

    response = client.get("/files/update.txt", auth=auth)
    assert response.status_code == 200
    assert response.json()["content"] == "New Content"

def test_delete_file():
    client.post("/files", json={"file_name": "delete.txt", "content": "To be deleted"}, auth=auth)
    response = client.delete("/files/delete.txt", auth=auth)
    assert response.status_code == 200
    assert response.json()["message"] == "File deleted successfully"

    response = client.get("/files/delete.txt", auth=auth)
    assert response.status_code == 404

def test_prohibit_git_directory_operations():
    response = client.post("/files", json={"file_name": ".git/test.txt", "content": "Forbidden"}, auth=auth)
    assert response.status_code == 403
    assert response.json()["detail"] == "Operation not allowed on .git directory"

def test_non_existing_file():
    response = client.get("/files/nonexistent.txt", auth=auth)
    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"

def test_special_characters_in_filename():
    special_filename = "special_!@#.txt"
    response = client.post("/files", json={"file_name": special_filename, "content": "Special"}, auth=auth)
    assert response.status_code == 201
    assert response.json()["message"] == "File created successfully"

    encoded_filename = urllib.parse.quote(special_filename)
    response = client.get(f"/files/{encoded_filename}", auth=auth)
    assert response.status_code == 200
    assert response.json()["content"] == "Special"
