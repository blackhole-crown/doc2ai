"""JSON 格式输出器"""

from typing import List, Dict, Any
from datetime import datetime


class JSONFormatter:
    """JSON 格式输出器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.compact = config.get('compact', False)
    
    def format(self, files: List, contents: Dict, stats: Dict, 
               root_path: str, description: str = None) -> Dict[str, Any]:
        """格式化输出为 JSON"""
        
        # 构建文件列表
        files_list = []
        for file_info in files:
            content_info = contents.get(file_info.path, {})
            
            file_data = {
                "file_info": {
                    "path": file_info.path,
                    "name": file_info.name,
                    "extension": file_info.extension,
                    "size_bytes": file_info.size_bytes,
                    "size_human": self._format_size(file_info.size_bytes),
                    "modified": file_info.modified.isoformat()
                },
                "content": {
                    "raw": content_info.get('content', ''),
                    "truncated": False
                },
                "metadata": content_info.get('metadata', {})
            }
            
            files_list.append(file_data)
        
        # 构建输出
        output = {
            "metadata": {
                "project_name": Path(root_path).name,
                "root_path": root_path,
                "processed_at": datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "statistics": stats,
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


from pathlib import Path