# api/main.py (estrutura para Vercel + execução local)
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import time
import uvicorn

app = FastAPI(title="JobIdMobile API")

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# MODELOS
# ---------------------------
class JobData(BaseModel):
    jobId1M: str = ""
    jobId5M: str = ""
    jobId10M: str = ""
    jobId50M: str = ""
    jobId100M: str = ""
    jobId300M: str = ""

class StatusData(BaseModel):
    nome: str

# ---------------------------
# VARIÁVEIS GLOBAIS
# ---------------------------
current_jobs = {
    "1M": "",
    "5M": "",
    "10M": "",
    "50M": "",
    "100M": "",
    "300M": ""
}

active_status = {}  # {"nome": expiração_timestamp}

# ---------------------------
# ROTAS JOB
# ---------------------------
@app.post("/job")
async def update_jobs(data: JobData):
    global current_jobs
    current_jobs["1M"] = data.jobId1M or current_jobs["1M"]
    current_jobs["5M"] = data.jobId5M or current_jobs["5M"]
    current_jobs["10M"] = data.jobId10M or current_jobs["10M"]
    current_jobs["50M"] = data.jobId50M or current_jobs["50M"]
    current_jobs["100M"] = data.jobId100M or current_jobs["100M"]
    current_jobs["300M"] = data.jobId300M or current_jobs["300M"]
    return {"message": "JobIds atualizados", "jobIds": current_jobs}

@app.get("/job")
async def get_jobs():
    return current_jobs

@app.get("/job/{job_category}")
async def get_job_category(job_category: str):
    job_category = job_category.upper()
    if job_category in current_jobs:
        return {"jobId": current_jobs[job_category]}
    return {"error": "Categoria inválida"}

@app.post("/job/raw")
async def update_jobs_raw(request: Request):
    body = await request.json()
    global current_jobs
    for key in current_jobs.keys():
        if key + "M" in body:
            current_jobs[key] = body[key + "M"]
    return {"message": "JobIds atualizados", "jobIds": current_jobs}

# ---------------------------
# ROTAS STATUS
# ---------------------------
@app.post("/status")
async def update_status(data: StatusData):
    global active_status
    now = time.time()
    key = data.nome.strip()

    # remove expirados
    active_status = {nome: exp for nome, exp in active_status.items() if exp > now}

    # adiciona com expiração de 4 minutos
    active_status[key] = now + 240

    return {"ativos": len(active_status), "players": list(active_status.keys())}

@app.get("/status")
async def get_status():
    now = time.time()
    ativos = {nome: exp for nome, exp in active_status.items() if exp > now}
    return {"ativos": len(ativos), "players": list(ativos.keys())}


# ---------------------------
# EXECUÇÃO LOCAL
# ---------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
