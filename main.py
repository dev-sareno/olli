from fastapi import FastAPI, HTTPException, UploadFile, Form, File, Depends
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List
import os
import subprocess
import time

# Configuration
BASE_DIR = "/Users/sareno/src/dev-sareno/mkdocs"
USERNAME = os.getenv("API_USERNAME", "admin")
PASSWORD = os.getenv("API_PASSWORD", "password")

app = FastAPI(title="File Management API", description="A simple REST API to manage files and interact with shell", version="1.0.0")

security = HTTPBasic()

# Helper functions
def get_file_metadata(file_path: str):
    stats = os.stat(file_path)
    return {
        "file_name": os.path.relpath(file_path, BASE_DIR),
        "file_size_bytes": stats.st_size,
        "creation_date": time.ctime(stats.st_ctime),
        "update_date": time.ctime(stats.st_mtime)
    }

def list_files_recursively(base_dir: str):
    excluded_dir = os.path.join(base_dir, ".git")
    files = []
    for root, _, filenames in os.walk(base_dir):
        if excluded_dir in root:
            continue
        for filename in filenames:
            file_path = os.path.join(root, filename)
            files.append(get_file_metadata(file_path))
    return files

def verify_credentials(credentials: HTTPBasicCredentials):
    if credentials.username != USERNAME or credentials.password != PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Basic"})

# Pydantic models
class FileRequest(BaseModel):
    file_name: str
    content: str = ""

class CommandRequest(BaseModel):
    command: str

class FileMetadata(BaseModel):
    file_name: str
    file_size_bytes: int
    creation_date: str
    update_date: str

class FileListResponse(BaseModel):
    page: int
    per_page: int
    total_files: int
    files: List[FileMetadata]

@app.get("/files", response_model=FileListResponse)
def list_files(page: int = 1, per_page: int = 100, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    """List files in the directory and subdirectories"""
    files = list_files_recursively(BASE_DIR)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    files_paginated = files[start_index:end_index]

    return {
        "page": page,
        "per_page": per_page,
        "total_files": len(files),
        "files": files_paginated
    }

@app.post("/files", status_code=201)
def create_file(file_request: FileRequest, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    sanitized_filename = os.path.normpath(file_request.file_name)
    if sanitized_filename.startswith(".git/") or ".." in sanitized_filename:
        raise HTTPException(status_code=403, detail="Operation not allowed on .git directory")
    os.makedirs(os.path.dirname(os.path.join(BASE_DIR, sanitized_filename)), exist_ok=True)
    file_path = os.path.join(BASE_DIR, sanitized_filename)
    with open(file_path, 'w') as file:
        file.write(file_request.content)
    return {"message": "File created successfully"}

@app.get("/files/{filename:path}")
def view_file(filename: str, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    sanitized_filename = os.path.normpath(filename)
    if sanitized_filename.startswith(".git/") or ".." in sanitized_filename:
        raise HTTPException(status_code=403, detail="Invalid or forbidden filename")
    if filename.startswith(".git/"):
        raise HTTPException(status_code=403, detail="Operation not allowed on .git directory")
    """View the content of a file"""
    file_path = os.path.join(BASE_DIR, sanitized_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(file_path, 'r') as file:
        content = file.read()
    return {"content": content}

@app.put("/files/{filename:path}")
def update_file(filename: str, file_request: FileRequest, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    sanitized_filename = os.path.normpath(filename)
    if sanitized_filename.startswith(".git/") or ".." in sanitized_filename:
        raise HTTPException(status_code=403, detail="Invalid or forbidden filename")
    if filename.startswith(".git/"):
        raise HTTPException(status_code=403, detail="Operation not allowed on .git directory")
    """Update an existing file"""
    file_path = os.path.join(BASE_DIR, sanitized_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(file_path, 'w') as file:
        file.write(file_request.content)
    return {"message": "File updated successfully"}

@app.delete("/files/{filename:path}")
def delete_file(filename: str, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    sanitized_filename = os.path.normpath(filename)
    if sanitized_filename.startswith(".git/") or ".." in sanitized_filename:
        raise HTTPException(status_code=403, detail="Invalid or forbidden filename")
    if filename.startswith(".git/"):
        raise HTTPException(status_code=403, detail="Operation not allowed on .git directory")
    """Delete a file"""
    file_path = os.path.join(BASE_DIR, sanitized_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return {"message": "File deleted successfully"}

@app.get("/files/download/{filename:path}")
def download_file(filename: str, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    """Download a file"""
    file_path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

@app.post("/files/upload")
def upload_file(file: UploadFile = File(...), target_location: str = Form(BASE_DIR), credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    sanitized_filename = os.path.normpath(file.filename)
    if target_location.startswith(".git/") or ".." in sanitized_filename:
        raise HTTPException(status_code=403, detail="Invalid or forbidden filename")
    if target_location.startswith(".git/"):
        raise HTTPException(status_code=403, detail="Operation not allowed on .git directory")
    """Upload a file"""
    target_path = os.path.join(target_location, file.filename)
    with open(target_path, 'wb') as f:
        f.write(file.file.read())
    return {"message": "File uploaded successfully"}

@app.post("/exec")
def execute_command(command_request: CommandRequest, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    """Execute a command"""
    command = command_request.command
    start_time = time.time()
    process = subprocess.Popen(command, cwd=BASE_DIR, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    end_time = time.time()

    return {
        "command": command,
        "exit_code": process.returncode,
        "stdout": stdout.decode('utf-8'),
        "stderr": stderr.decode('utf-8'),
        "execution_duration": end_time - start_time
    }
