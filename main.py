import os
import json
import shutil
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import (
    init_db, save_scan, get_recent_scans, get_scan_details, delete_scan,
    get_user_settings, update_user_settings, get_developer_profile, update_developer_profile,
    update_file_humanized_code, register_user, login_user, get_user_by_id,
    decrement_user_scan, upgrade_user_to_pro, update_user_participation,
    save_feedback, get_feedback_list
)
from engine.detector import detect_ai_code, detect_ai_model_family, LANG_EXTENSIONS, UNIVERSAL_NORMALIZER_MATRIX
from engine.humanizer import humanize_code, MASTER_SYSTEM_PROMPT, UNIVERSAL_SYSTEM_PROMPT, extract_developer_style

init_db()

app = FastAPI(title="CodeShield AI - AI Code Detector & Stealth Humanizer", version="2.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
if os.path.exists(os.path.join(STATIC_DIR, "css")):
    app.mount("/css", StaticFiles(directory=os.path.join(STATIC_DIR, "css")), name="css")
if os.path.exists(os.path.join(STATIC_DIR, "js")):
    app.mount("/js", StaticFiles(directory=os.path.join(STATIC_DIR, "js")), name="js")
if os.path.exists(os.path.join(STATIC_DIR, "img")):
    app.mount("/img", StaticFiles(directory=os.path.join(STATIC_DIR, "img")), name="img")

IGNORED_DIRS = {".git", ".svn", "node_modules", "__pycache__", ".venv", "venv", ".idea", ".vscode", "dist", "build"}
IGNORED_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".pyc", ".exe", ".bin", ".zip", ".tar", ".gz", ".lock", ".db", ".sqlite"}

class SnippetRequest(BaseModel):
    code: str
    filename: Optional[str] = "snippet.py"
    language: Optional[str] = None
    user_id: Optional[int] = None

class HumanizeRequest(BaseModel):
    code: str
    language: Optional[str] = "python"
    mode: Optional[str] = "pragmatic"
    persona: Optional[str] = None                                                
    reference_samples: Optional[List[str]] = None
    target_scope: Optional[str] = "whole"                            
    flagged_line_numbers: Optional[List[int]] = None
    file_id: Optional[int] = None
    variation_seed: Optional[int] = None
    academic_year: Optional[str] = "year_1"
    purpose: Optional[str] = "assignment"

class CloneStyleRequest(BaseModel):
    samples: List[str]

class FeedbackRequest(BaseModel):
    user_name: str
    user_email: Optional[str] = None
    category: Optional[str] = "Feedback"
    rating: Optional[int] = 5
    message: str

class SettingsRequest(BaseModel):
    theme: Optional[str] = "cyberpunk"
    font: Optional[str] = "JetBrains Mono"
    particle_mode: Optional[str] = "cyber_grid"
    particle_density: Optional[str] = "high"
    glow_intensity: Optional[int] = 85
    scanlines_enabled: Optional[bool] = True
    sound_fx_enabled: Optional[bool] = True
    custom_accent_color: Optional[str] = "#00f0ff"

class DeveloperProfileRequest(BaseModel):
    name: str
    title: str
    bio: str
    avatar_url: str
    github: str
    linkedin: str
    email: str
    portfolio: str
    skills: List[str]

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    participation_type: Optional[str] = "General"

class LoginRequest(BaseModel):
    email: str
    password: str

class PaymentUpgradeRequest(BaseModel):
    user_id: int
    plan: Optional[str] = "monthly_1000"
    payment_method: Optional[str] = "UPI"
    payment_id: Optional[str] = "mock_pay_1000"

class ChatMessageRequest(BaseModel):
    message: str
    user_id: Optional[int] = None
    participation_type: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>CodeShield AI Frontend Initializing...</h1>")

@app.get("/manifest.json")
async def serve_manifest():
    m_path = os.path.join(STATIC_DIR, "manifest.json")
    if os.path.exists(m_path):
        return FileResponse(m_path, media_type="application/json")
    raise HTTPException(status_code=404, detail="Manifest not found")
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "CodeShield AI",
        "version": "2.5.0",
        "engine": "active"
    }

@app.post("/api/auth/register")
async def handle_register(req: RegisterRequest):
    try:
        user = register_user(req.username, req.email, req.password, req.participation_type or "General")
        return {"status": "success", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
async def handle_login(req: LoginRequest):
    user = login_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"status": "success", "user": user}

@app.get("/api/auth/user/{user_id}")
async def fetch_user_info(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/payment/upgrade")
async def handle_payment_upgrade(req: PaymentUpgradeRequest):
    user = upgrade_user_to_pro(req.user_id, req.plan or "monthly_1000")
    if not user:
        raise HTTPException(status_code=404, detail="User not found to upgrade")
    return {
        "status": "success",
        "message": "Payment of ₹1,000 processed successfully. CodeShield PRO activated for 1 month!",
        "plan": "PRO Monthly (₹1,000)",
        "user": user
    }

@app.post("/api/chat/assistant")
async def handle_chat_assistant(req: ChatMessageRequest):
    msg = req.message.lower().strip()
    p_type = req.participation_type or "General"

    if req.user_id and req.participation_type:
        update_user_participation(req.user_id, req.participation_type)

    if any(w in msg for w in ["college", "university", "assignment", "homework", "exam", "coursework", "evs", "ca1", "school"]):
        reply = (
            "🎓 **Academic / Assignment Mode Configured:**\n\n"
            "Academic detectors like Turnitin, MOSS, and Canvas Lookalike algorithms heavily penalize "
            "overly verbose commentary, mechanical step annotations, and uniform syntax.\n\n"
            "🛡️ **Our Advice:**\n"
            "1. Run your code through our **Radar Scan**.\n"
            "2. When prompted, select **'⚡ Humanize Code'** and choose **'Zero-Comment Pragmatic'**.\n"
            "3. We will completely strip robotic commentary and flatten textbook structures so it passes clean with natural human entropy!"
        )
    elif any(w in msg for w in ["hackathon", "competition", "contest", "leetcode", "codeforces"]):
        reply = (
            "🏆 **Hackathon / Competition Mode Configured:**\n\n"
            "Hackathon judges look for rapid, pragmatic, and high-impact code. AI boilerplate code is easy to spot by its generic variable names.\n\n"
            "🛡️ **Our Strategy:**\n"
            "Use our **Stealth Humanizer** with **'Clean Minimalist'** mode. It strips 100% of comments, condenses loops, and makes your codebase look like a seasoned competitive coder wrote it in flow state."
        )
    elif any(w in msg for w in ["interview", "take-home", "assessment", "job", "company", "hiring"]):
        reply = (
            "💼 **Technical Interview / Take-Home Assessment Mode:**\n\n"
            "Tech interviewers use automated code scanners to verify originality. Obvious ChatGPT scaffolds like generic `try...except Exception as e:` or mechanical docstrings trigger instant red flags.\n\n"
            "🛡️ **Recommendation:**\n"
            "Upload your project folder. Inspect flagged files and click **'Humanize Whole Code'**. It refactors variable names to industry standards and guarantees zero telltale AI comments!"
        )
    else:
        reply = (
            f"🤖 **CodeShield Assistant:**\n\n"
            f"You are set up for **{p_type}**. We provide multi-metric AST and perplexity detection. "
            "Your first **5 scans are 100% FREE**, after which you can unlock unlimited scans for **₹1,000 / month**.\n\n"
            "Paste your code snippet or drop your folder below to get started!"
        )

    return {
        "reply": reply,
        "participation_type": p_type
    }

@app.post("/api/scan/snippet")
async def scan_snippet(req: SnippetRequest):
    if not req.code or not req.code.strip():
        raise HTTPException(status_code=400, detail="No code content provided")

    credit_res = decrement_user_scan(req.user_id)
    if not credit_res["allowed"]:
        raise HTTPException(status_code=402, detail=credit_res.get("message", "Payment Required: Free tier exhausted"))

    result = detect_ai_code(req.code, req.filename or "snippet.py")

    file_entry = {
        "filename": req.filename or "snippet.py",
        "file_path": req.filename or "snippet.py",
        "language": result["language"],
        "ai_score": result["ai_score"],
        "verdict": result["verdict"],
        "indicators": result["indicators"],
        "line_heatmaps": result["line_heatmaps"],
        "original_code": req.code,
        "humanized_code": None
    }

    scan_id = save_scan(
        scan_type="snippet",
        project_name=req.filename or "Code Snippet",
        total_files=1,
        avg_ai_score=result["ai_score"],
        verdict=result["verdict"],
        files_data=[file_entry]
    )

    scan_details = get_scan_details(scan_id)
    file_id = scan_details["files"][0]["id"] if scan_details and scan_details.get("files") else None

    return {
        "scan_id": scan_id,
        "file_id": file_id,
        "filename": req.filename,
        "ai_score": result["ai_score"],
        "verdict": result["verdict"],
        "language": result["language"],
        "indicators": result["indicators"],
        "metrics": result["metrics"],
        "six_factors": result.get("six_factors", {}),
        "stylometry_dimensions": result.get("stylometry_dimensions", {}),
        "nine_signals": result.get("nine_signals", {}),
        "ai_family": result.get("ai_family", {}),
        "universal_matrix": result.get("universal_matrix", []),
        "line_heatmaps": result["line_heatmaps"],
        "should_humanize": result["ai_score"] >= 35.0,
        "credits": credit_res
    }

@app.post("/api/scan/folder")
async def scan_folder(
    files: List[UploadFile] = File(...), 
    paths: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    u_id = int(user_id) if user_id and user_id.isdigit() else None
    credit_res = decrement_user_scan(u_id)
    if not credit_res["allowed"]:
        raise HTTPException(status_code=402, detail=credit_res.get("message", "Payment Required: Free tier exhausted"))

    rel_paths = []
    if paths:
        try:
            rel_paths = json.loads(paths)
        except Exception:
            rel_paths = []

    files_data = []
    total_score = 0.0

    for i, file in enumerate(files):
        rel_path = rel_paths[i] if i < len(rel_paths) else file.filename

        parts = rel_path.replace("\\", "/").split("/")
        if any(p in IGNORED_DIRS for p in parts[:-1]):
            continue

        _, ext = os.path.splitext(file.filename)
        if ext.lower() in IGNORED_EXTS:
            continue

        if ext.lower() not in LANG_EXTENSIONS and ext.lower() not in [".txt", ".md", ".env"]:
            continue

        try:
            content_bytes = await file.read()
            try:
                code_text = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                code_text = content_bytes.decode("latin-1", errors="ignore")

            if not code_text.strip():
                continue

            analysis = detect_ai_code(code_text, file.filename)
            total_score += analysis["ai_score"]

            files_data.append({
                "filename": os.path.basename(rel_path),
                "file_path": rel_path,
                "language": analysis["language"],
                "ai_score": analysis["ai_score"],
                "verdict": analysis["verdict"],
                "indicators": analysis["indicators"],
                "line_heatmaps": analysis["line_heatmaps"],
                "original_code": code_text,
                "humanized_code": None,
                "line_count": len(code_text.splitlines())
            })
        except Exception:
            continue

    if not files_data:
        raise HTTPException(status_code=400, detail="No readable code files detected in folder upload")

    avg_ai_score = round(total_score / len(files_data), 1)
    if avg_ai_score < 20.0:
        proj_verdict = "Predominantly Human"
    elif avg_ai_score < 40.0:
        proj_verdict = "Likely Human"
    elif avg_ai_score < 65.0:
        proj_verdict = "Mixed / AI-Assisted"
    elif avg_ai_score < 85.0:
        proj_verdict = "High AI Concentration"
    else:
        proj_verdict = "Definitive AI Project"

    first_path = files_data[0]["file_path"].replace("\\", "/")
    project_name = first_path.split("/")[0] if "/" in first_path else "Uploaded Project"

    scan_id = save_scan(
        scan_type="folder",
        project_name=project_name,
        total_files=len(files_data),
        avg_ai_score=avg_ai_score,
        verdict=proj_verdict,
        files_data=files_data
    )

    scan_details = get_scan_details(scan_id)
    ai_flagged_files = [f for f in files_data if f["ai_score"] >= 35.0]

    return {
        "scan_id": scan_id,
        "project_name": project_name,
        "total_files": len(files_data),
        "avg_ai_score": avg_ai_score,
        "verdict": proj_verdict,
        "ai_flagged_count": len(ai_flagged_files),
        "should_humanize": len(ai_flagged_files) > 0,
        "files": scan_details["files"] if scan_details else files_data,
        "credits": credit_res
    }

@app.post("/api/humanize")
async def humanize_endpoint(req: HumanizeRequest):
    if not req.code or not req.code.strip():
        raise HTTPException(status_code=400, detail="No code provided to humanize")

    result = humanize_code(
        req.code, 
        language=req.language or "python", 
        mode=req.mode or "pragmatic",
        target_scope=req.target_scope or "whole",
        flagged_line_numbers=req.flagged_line_numbers,
        variation_seed=req.variation_seed,
        persona=req.persona,
        reference_samples=req.reference_samples,
        academic_year=req.academic_year or "year_1",
        purpose=req.purpose or "assignment"
    )

    if req.file_id:
        update_file_humanized_code(req.file_id, result["humanized_code"])

    return result

@app.get("/api/humanizer/master-prompt")
async def get_master_prompt():
    return {
        "status": "success",
        "title": "Master System Prompt for Senior Engineer Code Humanizer",
        "master_prompt": MASTER_SYSTEM_PROMPT
    }

@app.get("/api/humanizer/universal-matrix")
async def get_universal_matrix():
    return {
        "status": "success",
        "title": "Universal AI Code Signatures & Normalization Matrix",
        "matrix": UNIVERSAL_NORMALIZER_MATRIX,
        "universal_prompt": UNIVERSAL_SYSTEM_PROMPT
    }

@app.post("/api/humanizer/clone-style")
async def handle_clone_style(req: CloneStyleRequest):
    if not req.samples:
        raise HTTPException(status_code=400, detail="At least one code sample is required to extract developer style")
    profile = extract_developer_style(req.samples)
    return {
        "status": "success",
        "style_profile": profile
    }

@app.post("/api/feedback")
async def handle_feedback(req: FeedbackRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Feedback message cannot be empty")
    fb = save_feedback(
        req.user_name, 
        req.user_email, 
        req.category or "Feedback", 
        int(req.rating or 5), 
        req.message
    )
    return {
        "status": "success",
        "message": "Thank you! Your feedback/query has been recorded.",
        "feedback": fb
    }

@app.get("/api/feedback")
async def fetch_all_feedback():
    return get_feedback_list(50)

@app.get("/api/history")
async def fetch_history():
    return get_recent_scans(50)

@app.get("/api/history/{scan_id}")
async def fetch_scan_details(scan_id: int):
    details = get_scan_details(scan_id)
    if not details:
        raise HTTPException(status_code=404, detail="Scan record not found")
    return details

@app.delete("/api/history/{scan_id}")
async def remove_scan(scan_id: int):
    success = delete_scan(scan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scan not found or already deleted")
    return {"status": "deleted", "scan_id": scan_id}

@app.get("/api/settings")
async def fetch_settings():
    return get_user_settings()

@app.post("/api/settings")
async def save_settings(req: SettingsRequest):
    updated = update_user_settings(req.dict())
    return updated

@app.get("/api/developer")
async def fetch_developer_profile():
    return get_developer_profile()

@app.post("/api/developer")
async def save_developer_profile(req: DeveloperProfileRequest):
    updated = update_developer_profile(req.dict())
    return updated
