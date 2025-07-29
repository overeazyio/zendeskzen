from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
from zendesk_extractor.core.main import main as run_extraction

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="zendesk_extractor/web/static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse('zendesk_extractor/web/static/index.html')

@app.post("/extract")
async def extract():
    try:
        run_extraction()
        return {"message": "Extraction process started."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
async def list_files():
    json_files = os.listdir("output/json")
    xml_files = os.listdir("output/xml")
    return {"json_files": json_files, "xml_files": xml_files}

@app.get("/files/json/{filename}")
async def get_json_file(filename: str):
    return FileResponse(f"output/json/{filename}")

@app.get("/files/xml/{filename}")
async def get_xml_file(filename: str):
    return FileResponse(f"output/xml/{filename}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
