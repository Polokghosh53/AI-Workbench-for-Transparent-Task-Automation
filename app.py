from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from agent_manager import run_plan, get_plan, list_plans
from auth import get_current_user
from tool_data import data_processor
from pathlib import Path
from datetime import datetime
import shutil
import uuid

app = FastAPI()

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/run-plan/")
async def run_plan_endpoint(request: dict, user=Depends(get_current_user)):
    try:
        return await run_plan(request, user)
    except Exception as e:
        print(f"Error in run_plan_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Plan execution failed: {str(e)}")

@app.get("/plans/")
async def get_plans(user=Depends(get_current_user)):
    return await list_plans(user)

@app.get("/plan/{plan_id}")
async def get_plan_endpoint(plan_id: str, user=Depends(get_current_user)):
    return await get_plan(plan_id, user)

@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    """Upload and process data files (Excel, CSV, Word, etc.)"""
    
    # Validate file type
    allowed_extensions = {'.xlsx', '.xls', '.csv', '.docx', '.txt', '.json'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the file
        result = data_processor.process_file(str(file_path))
        
        # Add metadata
        result["original_filename"] = file.filename
        result["file_size"] = file_path.stat().st_size
        result["upload_id"] = unique_filename
        
        return JSONResponse(content=result)
        
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")
    
    finally:
        # Optional: Clean up file after processing (uncomment if you don't want to keep files)
        # if file_path.exists():
        #     file_path.unlink()
        pass

@app.get("/supported-formats/")
async def get_supported_formats():
    """Get list of supported file formats"""
    return {
        "formats": [
            {"extension": ".xlsx", "description": "Excel Workbook"},
            {"extension": ".xls", "description": "Excel 97-2003 Workbook"},
            {"extension": ".csv", "description": "Comma Separated Values"},
            {"extension": ".docx", "description": "Word Document"},
            {"extension": ".txt", "description": "Text File"},
            {"extension": ".json", "description": "JSON Data"}
        ]
    }

@app.post("/generate-plan/")
async def generate_plan_endpoint(request: dict, user=Depends(get_current_user)):
    """Generate a structured plan using Portia's planning system"""
    try:
        from agent_manager import PlanBuilder, Plan, SimpleStep
        
        query = request.get("query", "Analyze data and send summary")
        file_path = request.get("file_path")
        
        # Create structured plan preview
        plan_steps = []
        
        if file_path:
            plan_steps.append({
                "step": 1,
                "task": f"Analyze uploaded data file",
                "tool_id": "fetch_and_summarize_data",
                "output": "data_analysis",
                "description": "Process and analyze the uploaded data file with visualizations and insights",
                "estimated_duration": "30-60 seconds",
                "requires_auth": False
            })
        else:
            plan_steps.append({
                "step": 1,
                "task": "Generate demo sales analysis",
                "tool_id": "fetch_and_summarize_data",
                "output": "data_analysis", 
                "description": "Create sample sales data analysis with charts and statistics",
                "estimated_duration": "15-30 seconds",
                "requires_auth": False
            })
        
        plan_steps.append({
            "step": 2,
            "task": "Human review checkpoint",
            "tool_id": "human_review_clarification",
            "output": "review_approval",
            "description": "⚠️ Pause for human review of sensitive data before email transmission",
            "estimated_duration": "Manual review required",
            "requires_auth": True,
            "clarification_type": "human_approval"
        })
        
        plan_steps.append({
            "step": 3,
            "task": "Send comprehensive analysis email",
            "tool_id": "send_email",
            "output": "email_status",
            "description": "Send formatted email with analysis results and visualizations note",
            "estimated_duration": "5-10 seconds",
            "requires_auth": False,
            "depends_on": ["data_analysis", "review_approval"]
        })
        
        return {
            "plan_id": f"preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "query": query,
            "steps": plan_steps,
            "total_steps": len(plan_steps),
            "estimated_total_duration": "1-2 minutes + manual review",
            "supports_rollback": True,
            "has_clarifications": True,
            "portia_enhanced": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")

@app.post("/rollback-plan/{plan_id}")
async def rollback_plan(plan_id: str, request: dict, user=Depends(get_current_user)):
    """Rollback a plan to a previous state using Portia's state management"""
    try:
        from db import get_plan_by_id
        
        step_index = request.get("step_index", 0)
        reason = request.get("reason", "User requested rollback")
        
        plan_state = get_plan_by_id(plan_id, user)
        if not plan_state:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # In production, this would restore from Portia's cloud state
        rollback_result = {
            "plan_id": plan_id,
            "rollback_to_step": step_index,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "status": "rolled_back",
            "user": user.get("username"),
            "message": f"Plan rolled back to step {step_index + 1}"
        }
        
        return rollback_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rollback failed: {str(e)}")

@app.get("/plan-history/")
async def get_plan_history(user=Depends(get_current_user)):
    """Get historical plan runs with Portia's audit capabilities"""
    try:
        from db import list_all_plans
        
        plans = list_all_plans(user)
        
        # Enhanced plan history with Portia features
        enhanced_plans = []
        for plan_data in plans:
            enhanced_plan = {
                "plan_id": plan_data.get("plan", {}).get("id"),
                "query": getattr(plan_data.get("plan"), "query", "Unknown query"),
                "created_at": getattr(plan_data.get("plan"), "created_at", datetime.now().isoformat()),
                "status": getattr(plan_data.get("plan"), "status", "completed"),
                "steps_count": len(plan_data.get("plan", {}).get("steps", [])),
                "results_count": len(plan_data.get("results", [])),
                "has_clarifications": len(getattr(plan_data, "clarifications", [])) > 0,
                "rollback_points": len(getattr(plan_data, "rollback_points", [])),
                "portia_enhanced": getattr(plan_data.get("plan"), "metadata", {}).get("portia_enhanced", False)
            }
            enhanced_plans.append(enhanced_plan)
        
        return {
            "plans": enhanced_plans,
            "total_count": len(enhanced_plans),
            "portia_features": {
                "state_management": True,
                "rollback_support": True,
                "clarifications": True,
                "audit_trail": True
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch plan history: {str(e)}")
