import hashlib
import chardet
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from datetime import datetime


class FileProcessor:
    """文件处理器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_line_count = config.get("max_line_count", 500)
        self.truncate_mode = config.get("truncate_mode", "head_tail")
        self.head_lines = config.get("head_lines", 100)
        self.tail_lines = config.get("tail_lines", 50)
        self.encoding = config.get("encoding", "auto")
    
    def process_file(self, file_path: Path, file_info: Dict) -> Dict[str, Any]:
        """处理单个文件"""
        result = {
            "content": {},
            "hash": None,
            "encoding": None,
            "line_count": 0,
            "truncated": False
        }
        
        try:
            # 检测编码
            encoding = self._detect_encoding(file_path)
            result["encoding"] = encoding
            
            # 读取文件内容
            content, line_count, truncated = self._read_file(file_path, encoding)
            result["line_count"] = line_count
            result["truncated"] = truncated
            
            # 计算哈希
            result["hash"] = self._calculate_hash(content)
            
            # 处理内容
            processed_content = self._process_content(content, truncated)
            result["content"] = processed_content
            
        except UnicodeDecodeError:
            # 如果是二进制文件，返回提示信息
            result["content"] = {
                "raw": "[Binary file - content not displayed]",
                "preview": "[Binary file - content not displayed]",
                "is_binary": True
            }
            result["line_count"] = 0
            result["truncated"] = True
        except Exception as e:
            result["content"] = {
                "raw": f"[Error reading file: {str(e)}]",
                "preview": f"[Error reading file: {str(e)}]",
                "error": True
            }
            result["line_count"] = 0
            result["truncated"] = True
        
        return result
    
    def _detect_encoding(self, file_path: Path) -> str:
        """检测文件编码"""
        if self.encoding != "auto":
            return self.encoding
        
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # 读取前10KB用于检测
                result = chardet.detect(raw_data)
                return result.get('encoding', 'utf-8') or 'utf-8'
        except:
            return 'utf-8'
    
    def _read_file(self, file_path: Path, encoding: str) -> Tuple[str, int, bool]:
        """读取文件内容"""
        lines = []
        line_count = 0
        truncated = False
        
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                for line in f:
                    line_count += 1
                    if line_count <= self.max_line_count:
                        lines.append(line.rstrip('\n\r'))
                    else:
                        truncated = True
                        break
        except Exception as e:
            raise Exception(f"Failed to read file: {e}")
        
        content = '\n'.join(lines)
        return content, line_count, truncated
    
    def _process_content(self, content: str, truncated: bool) -> Dict:
        """处理文件内容（截断等）"""
        if not truncated:
            return {
                "raw": content,
                "preview": content[:500] + "..." if len(content) > 500 else content,
                "start_line": 1,
                "end_line": len(content.split('\n')) if content else 0
            }
        
        # 需要截断
        lines = content.split('\n')
        total_lines = len(lines)
        
        if self.truncate_mode == "head_only":
            processed_lines = lines[:self.head_lines]
            result = {
                "raw": '\n'.join(processed_lines),
                "preview": '\n'.join(processed_lines[:10]) + "...",
                "start_line": 1,
                "end_line": len(processed_lines),
                "truncated": True,
                "truncation_info": {
                    "mode": "head_only",
                    "total_lines": total_lines,
                    "displayed_lines": len(processed_lines)
                }
            }
        elif self.truncate_mode == "tail_only":
            processed_lines = lines[-self.tail_lines:]
            result = {
                "raw": '\n'.join(processed_lines),
                "preview": '\n'.join(processed_lines[:10]) + "...",
                "start_line": total_lines - len(processed_lines) + 1,
                "end_line": total_lines,
                "truncated": True,
                "truncation_info": {
                    "mode": "tail_only",
                    "total_lines": total_lines,
                    "displayed_lines": len(processed_lines)
                }
            }
        else:  # head_tail
            head_lines = lines[:self.head_lines]
            tail_lines = lines[-self.tail_lines:]
            combined = head_lines + ["...", "--- 省略中间内容 ---", "..."] + tail_lines
            result = {
                "raw": '\n'.join(combined),
                "preview": '\n'.join(head_lines[:5] + ["..."] + tail_lines[-5:]),
                "start_line": 1,
                "end_line": total_lines,
                "truncated": True,
                "truncation_info": {
                    "mode": "head_tail",
                    "total_lines": total_lines,
                    "head_lines": len(head_lines),
                    "tail_lines": len(tail_lines)
                }
            }
        
        return result
    
    def _calculate_hash(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:8]