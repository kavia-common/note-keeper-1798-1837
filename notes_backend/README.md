# Notes Backend API

This is the RESTful backend API for the Note Keeper application.

## Features

- Create, read, update, delete notes
- Search notes by title/content
- In-memory storage (no external DB required)
- Well-documented OpenAPI/Swagger docs
- Ready to integrate with a frontend (CORS enabled)

## API Endpoints

- `POST /notes`: Create a note
- `GET /notes`: List/search notes (query param: `q` for search)
- `GET /notes/{id}`: Get a specific note
- `PUT /notes/{id}`: Update a note
- `DELETE /notes/{id}`: Delete a note

Full OpenAPI docs at `/docs`.

## Running

> Python 3.8+ required

Install dependencies:
```
pip install -r requirements.txt
```

Run development server:
```
uvicorn main:app --reload
```

Visit docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

## Data Persistence

- This implementation uses in-memory storage for simplicity.
- All notes are lost when the server restarts.
- Future upgrades can integrate a database (see `notes_database` dependency in the project structure).

## Example Note Object

```json
{
  "id": "b3d768d6-2268-43c6-bb3c-e7bd08d8a222",
  "title": "Sample Note",
  "content": "This is a sample note.",
  "created_at": "2024-06-01T12:00:00Z",
  "updated_at": "2024-06-01T12:01:00Z"
}
```
