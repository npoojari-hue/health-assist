# main.py - FastAPI routes. Run with:  uvicorn backend.app.main:app --reload
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from . import database as db
from .pipeline import answer_question
from .guidelines import compare_habits
from .rag import build_index, get_collection
from .schemas import Profile, Question, Feedback


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    if get_collection().count() == 0:
        build_index()
    yield


app = FastAPI(title="HealthAssist", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])


def require_consent():
    if not db.has_consent():
        raise HTTPException(status_code=403, detail="Consent is required first.")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/consent")
def get_consent():
    return {"accepted": db.has_consent()}


@app.post("/api/consent")
def accept_consent():
    db.save_consent()
    return {"accepted": True}


@app.get("/api/profile", dependencies=[Depends(require_consent)])
def get_profile():
    profile = db.load_profile()
    return {"profile": profile, "comparison": compare_habits(profile) if profile else []}


@app.put("/api/profile", dependencies=[Depends(require_consent)])
def put_profile(profile: Profile):
    data = profile.model_dump(exclude_none=True)
    db.save_profile(data)
    return {"profile": data, "comparison": compare_habits(data)}


@app.post("/api/ask", dependencies=[Depends(require_consent)])
def ask(q: Question):
    result = answer_question(q.text, db.load_profile(), model=q.model)
    history_id = db.add_history(q.text, result["answer"], result["sources"], result["outcome"])
    result.pop("passages", None)
    result["history_id"] = history_id
    return result


@app.get("/api/history", dependencies=[Depends(require_consent)])
def history():
    return db.list_history()


@app.post("/api/feedback", dependencies=[Depends(require_consent)])
def feedback(fb: Feedback):
    db.add_feedback(fb.history_id, fb.rating)
    return {"saved": True}


@app.delete("/api/my-data")
def delete_my_data():
    """Delete-my-data: removes consent, profile, history and feedback."""
    db.delete_all_data()
    return {"deleted": True}
