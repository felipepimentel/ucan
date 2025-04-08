# UCAN Chat Application

A modern chat application built with FastAPI and SQLite.

## Features

- Project management with conversations
- Real-time messaging
- Search functionality across projects and conversations
- Clean and modern API design
- SQLite database for easy setup

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ucan.git
cd ucan
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
uvicorn ucan.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Conversations
- `POST /api/conversations` - Create a new conversation
- `GET /api/conversations` - List all conversations
- `GET /api/conversations/{id}` - Get a specific conversation
- `PUT /api/conversations/{id}` - Update a conversation
- `DELETE /api/conversations/{id}` - Delete a conversation
- `POST /api/conversations/{id}/messages` - Add a message to a conversation
- `GET /api/conversations/{id}/messages` - Get all messages in a conversation

### Projects
- `POST /api/projects` - Create a new project
- `GET /api/projects` - List all projects
- `GET /api/projects/{id}` - Get a specific project
- `PUT /api/projects/{id}` - Update a project
- `DELETE /api/projects/{id}` - Delete a project

### Search
- `GET /api/search?q={query}` - Search across projects and conversations

## Development

The project uses:
- FastAPI for the API framework
- SQLite for the database
- Pydantic for data validation
- CORS middleware for frontend integration

## License

MIT License