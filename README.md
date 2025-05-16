# Smart Campus Management Backend

A FastAPI-based backend service for the Smart Campus Management System.

## Features

- FastAPI framework for high-performance API development
- Automatic API documentation with Swagger UI and ReDoc
- CORS middleware for cross-origin requests
- Modular router structure for easy endpoint management
- Health check endpoint for system monitoring

## Prerequisites

- Python 3.8 or higher
- Conda (recommended) or pip
- Git

## Installation

### Using Conda (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd Smart-Campus-Management-backend
```

2. Create and activate the Conda environment:
```bash
conda env create -f environment.yml
conda activate smart-campus-backend
```

### Alternative: Using venv

1. Clone the repository:
```bash
git clone <repository-url>
cd Smart-Campus-Management-backend
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

To run the development server:

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   └── routers/
│       ├── __init__.py
│       └── health.py
├── main.py
├── environment.yml    # Conda environment file
└── requirements.txt   # pip requirements file
```

## Available Endpoints

### Health Check
- `GET /health/`
  - Returns the health status of the API
  - Response: `{"status": "healthy", "version": "1.0.0"}`

### Root
- `GET /`
  - Welcome message
  - Response: `{"message": "Welcome to Smart Campus Management API"}`

## Development

### Adding New Endpoints

1. Create a new router file in `app/routers/`
2. Import and include the router in `main.py`
3. Add your endpoints to the router file

Example:
```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/your-endpoint",
    tags=["Your Tag"]
)

@router.get("/")
async def your_endpoint():
    return {"message": "Your response"}
```

### Managing Dependencies

#### Using Conda
To add new dependencies:
1. Add them to `environment.yml`
2. Update the environment:
```bash
conda env update -f environment.yml
```

#### Using pip
To add new dependencies:
1. Add them to `requirements.txt`
2. Update the environment:
```bash
pip install -r requirements.txt
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license here]

## Contact

[Add your contact information here]