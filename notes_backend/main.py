from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from uuid import uuid4, UUID
from datetime import datetime

app = FastAPI(
    title="Notes Backend API",
    description="RESTful API for note-keeping web application. Supports CRUD and search for notes.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Notes", "description": "Operations on notes."}
    ]
)

# CORS for local frontend integration (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For demo, wildcard. In production set specific origins.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---

class NoteBase(BaseModel):
    title: str = Field(..., description="Title of the note", min_length=1, max_length=200)
    content: str = Field(..., description="Content of the note", min_length=1)

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated title of the note", max_length=200)
    content: Optional[str] = Field(None, description="Updated content of the note")

class Note(NoteBase):
    id: UUID = Field(..., description="Unique identifier for the note")
    created_at: datetime = Field(..., description="Timestamp of note creation")
    updated_at: datetime = Field(..., description="Timestamp of last note update")

# --- In-Memory Storage (simple dict) ---
notes_store: Dict[UUID, Note] = {}

# --- Routes ---

# PUBLIC_INTERFACE
@app.post("/notes", response_model=Note, tags=["Notes"], summary="Create a new note", response_description="Created note")
async def create_note(note: NoteCreate):
    """Create a new note with a unique ID."""
    note_id = uuid4()
    now = datetime.utcnow()
    new_note = Note(
        id=note_id,
        title=note.title,
        content=note.content,
        created_at=now,
        updated_at=now,
    )
    notes_store[note_id] = new_note
    return new_note

# PUBLIC_INTERFACE
@app.get("/notes", response_model=List[Note], tags=["Notes"], summary="List/search notes", response_description="List of notes")
async def list_notes(q: Optional[str] = Query(None, description="Search string for note title or content")):
    """
    Returns a list of notes. If `q` is given, filters notes by substring (case-insensitive) in title OR content.
    """
    results = list(notes_store.values())
    if q:
        q = q.lower()
        results = [
            note for note in results
            if q in note.title.lower() or q in note.content.lower()
        ]
    return sorted(results, key=lambda n: n.updated_at, reverse=True)

# PUBLIC_INTERFACE
@app.get("/notes/{note_id}", response_model=Note, tags=["Notes"], summary="Get note by ID", response_description="Note details")
async def get_note(
        note_id: UUID = Path(..., description="UUID of the note")
    ):
    """
    Get the details of a note by its ID.
    """
    note = notes_store.get(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

# PUBLIC_INTERFACE
@app.put("/notes/{note_id}", response_model=Note, tags=["Notes"], summary="Update a note", response_description="Updated note")
async def update_note(
        note_id: UUID = Path(..., description="UUID of the note"),
        note_update: NoteUpdate = ...
    ):
    """
    Update the title and/or content of a note by ID. Partial updates supported.
    """
    note = notes_store.get(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    updated = note.copy(update={
        "title": note_update.title if note_update.title is not None else note.title,
        "content": note_update.content if note_update.content is not None else note.content,
        "updated_at": datetime.utcnow(),
    })
    notes_store[note_id] = updated
    return updated

# PUBLIC_INTERFACE
@app.delete("/notes/{note_id}", response_model=dict, tags=["Notes"], summary="Delete a note", response_description="Result")
async def delete_note(
        note_id: UUID = Path(..., description="UUID of the note")
    ):
    """
    Delete a specific note by its ID.
    """
    if note_id in notes_store:
        del notes_store[note_id]
        return {"result": "Note deleted"}
    raise HTTPException(status_code=404, detail="Note not found")


# --- API Documentation Route ---
# PUBLIC_INTERFACE
@app.get("/", tags=["Docs"], include_in_schema=False)
async def root():
    """Redirects to Swagger docs UI."""
    return {"docs_url": "/docs", "openapi_url": "/openapi.json"}

