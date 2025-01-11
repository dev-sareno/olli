# File Management API

This is a RESTful API built using FastAPI for managing files on a server. The API supports various operations, including listing files, creating, reading, updating, deleting files, uploading and downloading files, and executing commands.

## Features

### File CRUD Operations

- **List files with pagination support**
- **Create files**, including nested files
- **View file content**
- **Update file content**
- **Delete files**

### File Upload and Download

- **Upload files** with a specified target location
- **Download files**

### Command Execution

- **Execute any shell commands**, including git commands

### Security

- **Excludes operations on the .git directory**
- **Prevents directory traversal attacks**

## Requirements

- **Python 3.8+**
- **FastAPI**
- **Uvicorn**
- **Pydantic**
- **Python-Multipart**
- **Httpx** (for testing)

## Installation

1. Clone the repository:

```bash
git clone <repository_url>
cd <repository_directory>
```

2. Create a virtual environment and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Run the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```

- The API documentation (Swagger UI) will be available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- The ReDoc documentation will be available at: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## API Endpoints

### Files

#### **GET /files**
List files in the directory with pagination.

**Query Parameters:**
- `page` (*int*): Page number (default: 1)
- `per_page` (*int*): Number of files per page (default: 100)

#### **POST /files**
Create a new file.

**Request Body:**
```json
{
  "file_name": "string",
  "content": "string"
}
```

#### **GET /files/{filename}**
View the content of a specified file.

#### **PUT /files/{filename}**
Update the content of an existing file.

**Request Body:**
```json
{
  "file_name": "string",
  "content": "string"
}
```

#### **DELETE /files/{filename}**
Delete a specified file.

#### **GET /files/download/{filename}**
Download a specified file.

#### **POST /files/upload**
Upload a new file.

**Form Data:**
- `file` (*file*): The file to upload
- `target_location` (*string*): The target directory for the uploaded file (optional)

### Command Execution

#### **POST /exec**
Execute a shell command.

**Request Body:**
```json
{
  "command": "string"
}
```

**Response:**
```json
{
  "command": "string",
  "exit_code": 0,
  "stdout": "string",
  "stderr": "string",
  "execution_duration": 0.123
}
```

## Testing

1. Install pytest and httpx:

```bash
pip install pytest httpx
```

2. Run the tests:

```bash
pytest main_tests.py
```

## Notes

- **Operations on the .git directory are prohibited** to enhance security.
- **Filenames are sanitized** to prevent directory traversal attacks.

## License

This project is licensed under the MIT License.
