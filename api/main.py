from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from markitdown import MarkItDown
import tempfile, os, shutil, resend

app = FastAPI(title="MarkItDown API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

resend.api_key = os.environ["RESEND_API_KEY"]
md = MarkItDown(enable_plugins=False)

@app.get("/")
def root():
    return {"message": "MarkItDown API", "docs": "/docs"}

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
        return {
            "filename": file.filename,
            "preview": result.text_content[:600]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)

@app.post("/convert-and-send")
async def convert_and_send(
    file: UploadFile = File(...),
    email: str = Form(...)
):
    suffix = os.path.splitext(file.filename)[-1] or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        result = md.convert(tmp_path)
        content = result.text_content
        original_name = os.path.splitext(file.filename)[0]
        md_filename = f"{original_name}.md"

        resend.Emails.send({
            "from": "MarkItDown <noreply@meriane.de>",
            "to": [email],
            "subject": f"Votre fichier converti : {md_filename}",
            "html": f"""
                <div style="font-family:sans-serif;max-width:600px;margin:auto;padding:2rem;">
                    <h2 style="color:#1a1a1a;">Votre fichier est prêt ✓</h2>
                    <p style="color:#555;">
                        Le fichier <strong>{file.filename}</strong> 
                        a été converti en Markdown.
                    </p>
                    <p style="color:#555;">
                        Vous trouverez <strong>{md_filename}</strong> en pièce jointe.
                    </p>
                    <hr style="border:none;border-top:1px solid #eee;margin:1.5rem 0;">
                    <p style="color:#999;font-size:12px;">
                        Converti via MarkItDown · meriane.de
                    </p>
                </div>
            """,
            "attachments": [{
                "filename": md_filename,
                "content": list(content.encode("utf-8")),
            }]
        })

        return {
            "success": True,
            "preview": content[:600],
            "filename": md_filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)