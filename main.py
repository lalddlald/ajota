from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="JobIdMobile API")

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     
    allow_methods=["*"],     
    allow_headers=["*"],     
)

# Modelo para receber dados via POST
class JobData(BaseModel):
    jobId1M: str = ""
    jobId5M: str = ""
    jobId10M: str = ""
    jobId50M: str = ""
    jobId100M: str = ""
    jobId300M: str = ""

# Variável global para armazenar os JobIds
current_jobs = {
    "1M": "",
    "5M": "",
    "10M": "",
    "50M": "",
    "100M": "",
    "300M": ""
}

# Endpoint POST para atualizar os JobIds via Pydantic
@app.post("/job")
async def update_jobs(data: JobData):
    global current_jobs
    current_jobs["1M"] = data.jobId1M or current_jobs["1M"]
    current_jobs["5M"] = data.jobId5M or current_jobs["5M"]
    current_jobs["10M"] = data.jobId10M or current_jobs["10M"]
    current_jobs["50M"] = data.jobId50M or current_jobs["50M"]
    current_jobs["100M"] = data.jobId100M or current_jobs["100M"]
    current_jobs["300M"] = data.jobId300M or current_jobs["300M"]
    print(f"[UPDATE] JobIds atualizados: {current_jobs}")
    return {"message": "JobIds atualizados", "jobIds": current_jobs}

# Endpoint GET para retornar todos os JobIds (e limpar depois)
@app.get("/job")
async def get_jobs():
    global current_jobs
    response = current_jobs.copy()
    # limpa todos depois do GET
    for k in current_jobs.keys():
        current_jobs[k] = ""
    print(f"[GET] Retornando e limpando todos os JobIds: {response}")
    return response

# Endpoint GET alternativo (retorna apenas um JobId específico e limpa depois)
@app.get("/job/{job_category}")
async def get_job_category(job_category: str):
    global current_jobs
    job_category = job_category.upper()
    if job_category in current_jobs:
        job_id = current_jobs[job_category]
        current_jobs[job_category] = ""  # limpa depois do GET
        print(f"[GET] Retornando e limpando {job_category}: {job_id}")
        return {"jobId": job_id}
    return {"error": "Categoria de JobId inválida"}

# Endpoint POST via JSON puro (mais flexível)
@app.post("/job/raw")
async def update_jobs_raw(request: Request):
    body = await request.json()
    global current_jobs
    for key in current_jobs.keys():
        if key + "M" in body:
            current_jobs[key] = body[key + "M"]
    print(f"[UPDATE RAW] JobIds atualizados: {current_jobs}")
    return {"message": "JobIds atualizados", "jobIds": current_jobs}
