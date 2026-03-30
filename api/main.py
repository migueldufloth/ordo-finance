from fastapi import FastAPI

app = FastAPI(title="Ordo Finance API", description="Microserviço de relatórios")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "reports-api"}

@app.get("/")
def root():
    return {"message": "Microserviço de relatórios (FastAPI) em operação"}
