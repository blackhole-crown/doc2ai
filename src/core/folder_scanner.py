import os
import fnmatch
from pathlib import Path
from typing import List, Dict, Optional, Set
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
    
    def __init__(self, config: Dict):
        self.config = config
        self.exclude_patterns = config.get("exclude_patterns", [])
        self.include_extensions = set(config.get("include_extensions", []))
        self.exclude_extensions = set(config.get("exclude_extensions", []))
        self.max_file_size = config.get("max_file_size_mb", 10) * 1024 * 1024
        self.max_files = config.get("max_files", 1000)
        self.follow_symlinks = config.get("follow_symlinks", False)
        
        self.scanned_files: List[FileInfo] = []
        self.skipped_files: List[Dict] = []
        self.total_size = 0
    
    def scan(self, root_path: Path) -> List[FileInfo]:
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
                
                # 处理符号链接
                if item.is_symlink() and not self.follow_symlinks:
                    self.skipped_files.append({
                        "path": str(rel_path),
                        "reason": "symlink_skipped"
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
        
        # 检查排除模式
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(path_str, pattern):
                return True
            # 检查目录部分
            if '/' + pattern in path_str or pattern + '/' in path_str:
                return True
        
        # 如果是文件，检查扩展名
        if rel_path.suffix:
            ext = rel_path.suffix.lower()
            if self.include_extensions and ext not in self.include_extensions:
                return True
            if ext in self.exclude_extensions:
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
                    "size_bytes": file_size,
                    "size_limit": self.max_file_size
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
            "file_types": extensions
        }
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"