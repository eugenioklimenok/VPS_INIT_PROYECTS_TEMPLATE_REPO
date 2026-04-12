from fastapi import FastAPI


app = FastAPI(title="__PROJECT_NAME__ API", version="0.1.0")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "project": "__PROJECT_NAME__",
        "status": "ok",
        "message": "Template API running",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}
