"""
Flask + Vue.js 前端应用
提供文件夹上传和处理的可视化界面
"""

import os
import json
import uuid
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import threading
import zipfile
import tarfile

# 添加项目路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.processor import FolderProcessor
from src.config.config_manager import ConfigManager

app = Flask(__name__)
CORS(app)

# 配置
app.config['SECRET_KEY'] = 'folder2context-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB 上传限制

# 初始化处理器
config_manager = ConfigManager()
processor = FolderProcessor(config_manager.config)

# 存储任务状态
tasks = {}
tasks_lock = threading.Lock()


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/process', methods=['POST'])
def process_folder():
    """
    处理本地文件夹
    """
    data = request.get_json()
    folder_path = data.get('folder_path')
    
    if not folder_path:
        return jsonify({'error': 'folder_path is required'}), 400
    
    path = Path(folder_path)
    if not path.exists():
        return jsonify({'error': f'Path does not exist: {folder_path}'}), 400
    
    if not path.is_dir():
        return jsonify({'error': f'Path is not a directory: {folder_path}'}), 400
    
    try:
        # 更新配置
        if 'config' in data:
            config_manager.update(data['config'])
        
        # 处理文件夹
        result = processor.process(str(path))
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_folder():
    """
    上传压缩包并处理
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # 检查文件类型
    if not file.filename.endswith(('.zip', '.tar', '.gz', '.tar.gz')):
        return jsonify({'error': 'Only zip/tar files are supported'}), 400
    
    task_id = str(uuid.uuid4())
    
    # 保存上传的文件
    temp_dir = Path(tempfile.mkdtemp())
    temp_file = temp_dir / file.filename
    file.save(str(temp_file))
    
    # 在后台线程中处理
    thread = threading.Thread(target=_process_upload, args=(task_id, temp_file, temp_dir))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'task_id': task_id,
        'status': 'processing'
    })


@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    with tasks_lock:
        task = tasks.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(task)


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    return jsonify(config_manager.config)


@app.route('/api/config', methods=['PUT'])
def update_config():
    """更新配置"""
    data = request.get_json()
    config_manager.update(data)
    return jsonify({'success': True, 'config': config_manager.config})


@app.route('/api/preview', methods=['POST'])
def preview_folder():
    """
    预览文件夹结构（不读取文件内容）
    """
    data = request.get_json()
    folder_path = data.get('folder_path')
    
    if not folder_path:
        return jsonify({'error': 'folder_path is required'}), 400
    
    path = Path(folder_path)
    if not path.exists() or not path.is_dir():
        return jsonify({'error': 'Invalid folder path'}), 400
    
    # 获取文件夹结构（不读取文件内容）
    tree = _get_folder_tree(path)
    
    return jsonify({
        'success': True,
        'tree': tree
    })


def _process_upload(task_id, temp_file, temp_dir):
    """处理上传的文件"""
    try:
        # 更新状态
        with tasks_lock:
            tasks[task_id] = {
                'status': 'extracting',
                'progress': 20,
                'message': 'Extracting archive...'
            }
        
        # 解压
        extract_dir = temp_dir / 'extracted'
        extract_dir.mkdir()
        
        if temp_file.suffix == '.zip':
            with zipfile.ZipFile(temp_file, 'r') as zf:
                zf.extractall(extract_dir)
        else:
            mode = 'r:gz' if temp_file.suffix == '.gz' else 'r:'
            with tarfile.open(temp_file, mode) as tf:
                tf.extractall(extract_dir)
        
        # 找到根目录
        extracted_items = list(extract_dir.iterdir())
        if len(extracted_items) == 1 and extracted_items[0].is_dir():
            folder_path = extracted_items[0]
        else:
            folder_path = extract_dir
        
        # 更新状态
        with tasks_lock:
            tasks[task_id]['status'] = 'processing'
            tasks[task_id]['progress'] = 50
            tasks[task_id]['message'] = 'Processing files...'
        
        # 定义进度回调
        def progress_callback(percentage, message):
            with tasks_lock:
                if task_id in tasks:
                    # 映射进度 50-95%
                    mapped_progress = 50 + int(45 * percentage / 100)
                    tasks[task_id]['progress'] = mapped_progress
                    tasks[task_id]['message'] = message
        
        # 处理文件夹
        result = processor.process(str(folder_path), progress_callback)
        
        # 更新状态
        with tasks_lock:
            tasks[task_id] = {
                'status': 'completed',
                'progress': 100,
                'result': result,
                'message': 'Complete!'
            }
        
    except Exception as e:
        with tasks_lock:
            tasks[task_id] = {
                'status': 'failed',
                'error': str(e),
                'message': f'Error: {str(e)}'
            }
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir, ignore_errors=True)


def _get_folder_tree(path, max_depth=3, current_depth=0):
    """获取文件夹树结构"""
    if current_depth >= max_depth:
        return None
    
    tree = {
        'name': path.name,
        'type': 'directory',
        'path': str(path),
        'children': []
    }
    
    try:
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        for item in items:
            # 跳过隐藏文件和常见排除目录
            if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules']:
                continue
            
            if item.is_dir():
                child = _get_folder_tree(item, max_depth, current_depth + 1)
                if child:
                    tree['children'].append(child)
            else:
                tree['children'].append({
                    'name': item.name,
                    'type': 'file',
                    'path': str(item),
                    'size': item.stat().st_size,
                    'size_human': _format_size(item.stat().st_size)
                })
    except PermissionError:
        pass
    
    return tree


def _format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)