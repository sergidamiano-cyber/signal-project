from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from database import SessionLocal
from database import Interaction


# ==========================
# APP
# ==========================

app = FastAPI()

templates = Jinja2Templates(
    directory="templates"
)


# ==========================
# HOME DASHBOARD
# ==========================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    db = SessionLocal()

    interactions = db.query(
        Interaction
    ).all()

    total = len(interactions)

    risk = len([
        x for x in interactions
        if x.toxicity > 0.5
    ])

    avg = 0

    if total > 0:

        avg = sum(
            x.toxicity
            for x in interactions
        ) / total

    latest = interactions[-10:]

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={

            "total": total,
            "risk": risk,
            "avg": round(avg,2),
            "latest": [

    {
        "username": x.username,

        "original_message": x.original_message,

        "toxicity": round(
            x.toxicity * 100,
            2
        )

    }

    for x in latest

]

        }
    )