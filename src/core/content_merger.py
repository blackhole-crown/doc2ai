# src/core/content_merger.py
from pathlib import Path  # 添加这行
from typing import List, Dict, Any, Optional
from datetime import datetime
from .folder_scanner import FileInfo
from .tree_builder import TreeBuilder


class ContentMerger:
    """内容合并器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.output_config = config.get("output", {})
        self.tree_builder = TreeBuilder(
            include_metadata=self.output_config.get("include_metadata", True)
        )
    
    def merge_to_json(self, 
                      files: List[FileInfo],
                      file_contents: Dict[str, Any],
                      statistics: Dict,
                      errors: List[Dict],
                      root_path: str = "") -> Dict[str, Any]:
        """合并为JSON格式"""
        
        # 构建目录树
        tree = self.tree_builder.build_tree(files, Path(root_path).name if root_path else "project")
        
        # 构建文件内容列表
        files_list = []
        for file_info in files:
            content_info = file_contents.get(file_info.path, {})
            
            file_data = {
                "file_info": {
                    "path": file_info.path,
                    "name": file_info.name,
                    "extension": file_info.extension,
                    "size_bytes": file_info.size_bytes,
                    "size_human": self._format_size(file_info.size_bytes),
                    "modified": file_info.modified.isoformat(),
                    "is_symlink": file_info.is_symlink
                },
                "content": content_info.get("content", {}),
                "metadata": {
                    "hash": content_info.get("hash"),
                    "encoding": content_info.get("encoding"),
                    "line_count": content_info.get("line_count", 0),
                    "truncated": content_info.get("truncated", False)
                }
            }
            
            # 添加语言信息（如果存在）
            if "language" in content_info:
                file_data["analysis"] = {
                    "language": content_info["language"]
                }
            
            files_list.append(file_data)
        
        # 构建完整输出
        output = {
            "metadata": {
                "project_name": Path(root_path).name if root_path else "unknown",
                "root_path": root_path,
                "processed_at": datetime.now().isoformat(),
                "version": self.config.get("app", {}).get("version", "1.0.0"),
                "config": self._get_config_summary()
            },
            "statistics": statistics,
            "tree": tree,
            "files": files_list,
            "errors": errors
        }
        
        # 根据输出格式调整
        output_format = self.output_config.get("format", "detailed")
        if output_format == "compact":
            output = self._to_compact_format(output)
        elif output_format == "minimal":
            output = self._to_minimal_format(output)
        
        return output
    
    def _to_compact_format(self, output: Dict) -> Dict:
        """转换为紧凑格式"""
        compact = {
            "meta": {
                "name": output["metadata"]["project_name"],
                "time": output["metadata"]["processed_at"],
                "stats": {
                    "files": output["statistics"]["total_files"],
                    "size": output["statistics"]["total_size_human"],
                    "tokens": output["statistics"].get("estimated_tokens", 0)
                }
            },
            "tree": output["tree"],
            "contents": []
        }
        
        for file_data in output["files"]:
            content = file_data["content"].get("raw", "")
            if len(content) > 500:
                content = content[:500] + "..."
            
            compact["contents"].append({
                "p": file_data["file_info"]["path"],
                "ext": file_data["file_info"]["extension"],
                "c": content,
                "trunc": file_data["metadata"].get("truncated", False)
            })
        
        if output.get("errors"):
            compact["errors"] = output["errors"]
        
        return compact
    
    def _to_minimal_format(self, output: Dict) -> Dict:
        """转换为最简格式"""
        minimal = {
            "files": {}
        }
        
        for file_data in output["files"]:
            minimal["files"][file_data["file_info"]["path"]] = \
                file_data["content"].get("raw", "")
        
        if output.get("errors"):
            minimal["errors"] = output["errors"]
        
        return minimal
    
    def _get_config_summary(self) -> Dict:
        """获取配置摘要"""
        processing = self.config.get("processing", {})
        analysis = self.config.get("analysis", {})
        
        return {
            "max_file_size_mb": processing.get("max_file_size_mb"),
            "exclude_patterns": processing.get("exclude_patterns", [])[:5],
            "max_line_count": analysis.get("max_line_count"),
            "truncate_mode": analysis.get("truncate_mode")
        }
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"