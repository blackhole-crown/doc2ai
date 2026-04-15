"""JSON 格式输出器"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class JSONFormatter:
    """JSON 格式输出器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.compact = config.get('compact', False)
    
    def format(self, files: List, contents: Dict[int, Any], stats: Dict,
               root_path: str, description: str = None) -> Dict[str, Any]:
        """格式化输出为 JSON"""
        
        # 构建文件列表（按 ID 排序）
        files_list = []
        failed_file_ids = []
        error_types = {}
        
        for file_id in sorted(contents.keys()):
            item = contents[file_id]
            files_list.append(item)
            
            if item.get('status') == 'failed':
                failed_file_ids.append(file_id)
                error_type = item.get('metadata', {}).get('error', 'unknown')
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # 构建输出
        output = {
            "metadata": {
                "project_name": Path(root_path).name,
                "root_path": root_path,
                "processed_at": datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "statistics": {
                **stats,
                "failed_file_ids": failed_file_ids,
                "error_types": error_types
            },
            "files": files_list
        }
        
        # 添加 AI 描述
        if description:
            output["metadata"]["ai_description"] = description
        
        return output
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"