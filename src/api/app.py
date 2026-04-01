from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uuid
import os
import shutil
from pathlib import Path
import tempfile

from ..core.processor import FolderProcessor
from ..config.config_manager import ConfigManager
from .models.request_models import ProcessRequest, ProcessResponse
from .models.response_models import TaskResponse, ErrorResponse


app = FastAPI(title="Folder2Context API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化
config_manager = ConfigManager()
processor = FolderProcessor(config_manager.config)

# 存储任务（生产环境应使用Redis或数据库）
tasks = {}


class ProcessRequest(BaseModel):
    """处理请求模型"""
    folder_path: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    async_mode: bool = False


@app.post("/api/process", response_model=TaskResponse)
async def process_folder(request: ProcessRequest, background_tasks: BackgroundTasks):
    """
    处理文件夹
    """
    task_id = str(uuid.uuid4())
    
    # 验证输入
    if not request.folder_path:
        raise HTTPException(status_code=400, detail="folder_path is required")
    
    folder_path = Path(request.folder_path)
    if not folder_path.exists():
        raise HTTPException(status_code=400, detail=f"Path does not exist: {request.folder_path}")
    
    if not folder_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.folder_path}")
    
    # 更新配置
    if request.config:
        config_manager.update(request.config)
    
    if request.async_mode:
        # 异步处理
        background_tasks.add_task(_process_task, task_id, str(folder_path))
        return TaskResponse(
            task_id=task_id,
            status="processing",
            message="Task started"
        )
    else:
        # 同步处理
        try:
            result = processor.process(str(folder_path))
            return TaskResponse(
                task_id=task_id,
                status="completed",
                result=result
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_folder(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    上传压缩包并处理
    """
    if not file.filename.endswith(('.zip', '.tar', '.gz')):
        raise HTTPException(status_code=400, detail="Only zip/tar files are supported")
    
    task_id = str(uuid.uuid4())
    temp_dir = Path(tempfile.mkdtemp())
    temp_file = temp_dir / file.filename
    
    # 保存上传的文件
    with open(temp_file, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    
    # 解压
    extract_dir = temp_dir / "extracted"
    extract_dir.mkdir()
    
    if temp_file.suffix == '.zip':
        import zipfile
        with zipfile.ZipFile(temp_file, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    else:
        import tarfile
        with tarfile.open(temp_file, 'r:*') as tar_ref:
            tar_ref.extractall(extract_dir)
    
    # 找到根目录
    extracted_items = list(extract_dir.iterdir())
    if len(extracted_items) == 1 and extracted_items[0].is_dir():
        folder_path = extracted_items[0]
    else:
        folder_path = extract_dir
    
    # 处理
    try:
        result = processor.process(str(folder_path))
        return TaskResponse(
            task_id=task_id,
            status="completed",
            result=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """
    获取任务状态
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]


@app.get("/api/download/{task_id}")
async def download_result(task_id: str):
    """
    下载处理结果
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    # 这里应该返回实际的文件
    # 示例实现
    import tempfile
    import json
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(task["result"], temp_file, indent=2)
    temp_file.close()
    
    return FileResponse(
        temp_file.name,
        media_type="application/json",
        filename=f"folder_context_{task_id}.json"
    )


@app.get("/api/config")
async def get_config():
    """
    获取当前配置
    """
    return config_manager.config


@app.put("/api/config")
async def update_config(config: Dict[str, Any]):
    """
    更新配置
    """
    config_manager.update(config)
    return {"status": "success", "config": config_manager.config}


@app.get("/health")
async def health_check():
    """
    健康检查
    """
    return {"status": "healthy"}


def _process_task(task_id: str, folder_path: str):
    """后台处理任务"""
    try:
        tasks[task_id] = {"status": "processing", "progress": 0}
        
        def progress_callback(percentage, message):
            tasks[task_id]["progress"] = percentage
            tasks[task_id]["message"] = message
        
        result = processor.process(folder_path, progress_callback)
        tasks[task_id] = {
            "status": "completed",
            "result": result,
            "progress": 100
        }
    except Exception as e:
        tasks[task_id] = {
            "status": "failed",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)