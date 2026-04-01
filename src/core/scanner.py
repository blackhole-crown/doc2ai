"""文件夹扫描器"""

import os
import fnmatch
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileInfo:
    """文件信息数据类"""
    path: str
    name: str
    absolute_path: Path
    size_bytes: int
    modified: datetime
    extension: str
    is_symlink: bool = False


class FolderScanner:
    """文件夹扫描器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.exclude_patterns = self.config.get('exclude_patterns', 
            ['.git', '__pycache__', 'node_modules', '.DS_Store', '*.pyc'])
        self.max_file_size = self.config.get('max_file_size_mb', 10) * 1024 * 1024
        self.max_files = self.config.get('max_files', 1000)
        
        self.scanned_files: List[FileInfo] = []
        self.skipped_files: List[Dict] = []
        self.total_size = 0
    
    def scan(self, root_path: str) -> List[FileInfo]:
        """扫描文件夹"""
        root_path = Path(root_path).resolve()
        
        if not root_path.exists():
            raise ValueError(f"Path does not exist: {root_path}")
        
        if not root_path.is_dir():
            raise ValueError(f"Path is not a directory: {root_path}")
        
        self.scanned_files = []
        self.skipped_files = []
        self.total_size = 0
        
        self._walk_directory(root_path, root_path)
        
        return self.scanned_files
    
    def _walk_directory(self, current_path: Path, root_path: Path):
        """递归遍历目录"""
        try:
            for item in current_path.iterdir():
                # 检查文件数量限制
                if len(self.scanned_files) >= self.max_files:
                    self.skipped_files.append({
                        "path": str(item),
                        "reason": "max_files_limit_exceeded"
                    })
                    continue
                
                rel_path = item.relative_to(root_path)
                
                # 检查是否应该排除
                if self._should_exclude(rel_path):
                    self.skipped_files.append({
                        "path": str(rel_path),
                        "reason": "excluded_by_pattern"
                    })
                    continue
                
                if item.is_dir():
                    self._walk_directory(item, root_path)
                elif item.is_file():
                    self._process_file(item, rel_path)
                    
        except PermissionError:
            self.skipped_files.append({
                "path": str(current_path),
                "reason": "permission_denied"
            })
        except Exception as e:
            self.skipped_files.append({
                "path": str(current_path),
                "reason": f"error: {str(e)}"
            })
    
    def _should_exclude(self, rel_path: Path) -> bool:
        """检查文件/目录是否应该排除"""
        path_str = str(rel_path)
        
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(path_str, pattern):
                return True
            if '/' + pattern in path_str or pattern + '/' in path_str:
                return True
        
        return False
    
    def _process_file(self, file_path: Path, rel_path: Path):
        """处理单个文件"""
        try:
            stat = file_path.stat()
            file_size = stat.st_size
            
            # 检查文件大小限制
            if file_size > self.max_file_size:
                self.skipped_files.append({
                    "path": str(rel_path),
                    "reason": "size_limit_exceeded",
                    "size_bytes": file_size
                })
                return
            
            file_info = FileInfo(
                path=str(rel_path),
                name=file_path.name,
                absolute_path=file_path,
                size_bytes=file_size,
                modified=datetime.fromtimestamp(stat.st_mtime),
                extension=file_path.suffix.lower(),
                is_symlink=file_path.is_symlink()
            )
            
            self.scanned_files.append(file_info)
            self.total_size += file_size
            
        except Exception as e:
            self.skipped_files.append({
                "path": str(rel_path),
                "reason": f"processing_error: {str(e)}"
            })
    
    def get_statistics(self) -> Dict:
        """获取扫描统计信息"""
        extensions = {}
        for file in self.scanned_files:
            ext = file.extension or "no_extension"
            extensions[ext] = extensions.get(ext, 0) + 1
        
        return {
            "total_files": len(self.scanned_files),
            "total_size_bytes": self.total_size,
            "total_size_human": self._format_size(self.total_size),
            "skipped_files": len(self.skipped_files),
            "file_types": extensions,
            "success_count": len(self.scanned_files),
            "failed_count": len(self.skipped_files)
        }
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"