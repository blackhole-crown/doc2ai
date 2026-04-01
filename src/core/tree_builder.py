from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from .folder_scanner import FileInfo


class TreeBuilder:
    """目录树构建器"""
    
    def __init__(self, include_metadata: bool = True):
        self.include_metadata = include_metadata
    
    def build_tree(self, files: List[FileInfo], root_name: str = "root") -> Dict[str, Any]:
        """构建目录树结构"""
        tree = {
            "name": root_name,
            "type": "directory",
            "path": "",
            "children": []
        }
        
        # 按路径排序
        sorted_files = sorted(files, key=lambda f: f.path)
        
        for file_info in sorted_files:
            self._add_to_tree(tree, file_info)
        
        return tree
    
    def _add_to_tree(self, tree: Dict, file_info: FileInfo):
        """将文件添加到树结构中"""
        path_parts = Path(file_info.path).parts
        current = tree
        
        # 遍历路径部分，创建目录节点
        for i, part in enumerate(path_parts[:-1]):
            # 查找是否已存在该目录节点
            existing_child = None
            for child in current["children"]:
                if child["name"] == part and child["type"] == "directory":
                    existing_child = child
                    break
            
            if existing_child:
                current = existing_child
            else:
                # 创建新目录节点
                new_dir = {
                    "name": part,
                    "type": "directory",
                    "path": str(Path(*path_parts[:i+1])),
                    "children": []
                }
                current["children"].append(new_dir)
                current = new_dir
        
        # 添加文件节点
        file_node = {
            "name": file_info.name,
            "type": "file",
            "path": file_info.path,
            "extension": file_info.extension,
            "size_bytes": file_info.size_bytes,
            "size_human": self._format_size(file_info.size_bytes)
        }
        
        if self.include_metadata:
            file_node.update({
                "modified": file_info.modified.isoformat(),
                "is_symlink": file_info.is_symlink
            })
        
        current["children"].append(file_node)
        
        # 保持子节点排序（目录在前，文件在后，按名称排序）
        current["children"].sort(key=lambda x: (x["type"] != "directory", x["name"]))
    
    def get_flat_tree(self, files: List[FileInfo]) -> List[str]:
        """获取扁平的树形文本表示"""
        lines = []
        sorted_files = sorted(files, key=lambda f: f.path)
        
        for file_info in sorted_files:
            depth = len(Path(file_info.path).parts) - 1
            indent = "  " * depth
            lines.append(f"{indent}├── {file_info.name}")
        
        return lines
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"