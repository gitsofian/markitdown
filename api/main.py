from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from markitdown import MarkItDown
import tempfile, os, shutil

app = FastAPI(title="MarkItDown API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tu restreindras plus tard à ton domaine frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

md = MarkItDown(enable_plugins=False)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[-1] or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        result = md.convert(tmp_path)
        return {"filename": file.filename, "markdown": result.text_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)