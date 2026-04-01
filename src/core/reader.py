"""文档读取器 - 统一处理各种文件"""

from pathlib import Path
from typing import List, Dict, Any

from src.formats.text import TextReader
from src.formats.docx import DocxReader
from src.formats.pdf import PdfReader
from src.formats.pptx_ocr import PptxOcrReader


class DocumentReader:
    """统一文档读取器"""
    
    # 格式映射
    READERS = {
        # 代码文件
        '.py': TextReader,
        '.js': TextReader,
        '.ts': TextReader,
        '.jsx': TextReader,
        '.tsx': TextReader,
        '.java': TextReader,
        '.c': TextReader,
        '.cpp': TextReader,
        '.go': TextReader,
        '.rs': TextReader,
        '.rb': TextReader,
        '.php': TextReader,
        
        # 配置文件
        '.json': TextReader,
        '.jsonl': TextReader,
        '.yaml': TextReader,
        '.yml': TextReader,
        '.toml': TextReader,
        '.ini': TextReader,
        '.conf': TextReader,
        
        # 文档文件
        '.txt': TextReader,
        '.md': TextReader,
        '.markdown': TextReader,
        '.rst': TextReader,
        '.log': TextReader,
        
        # 数据文件
        '.csv': TextReader,
        '.xml': TextReader,
        '.html': TextReader,
        '.css': TextReader,
        '.scss': TextReader,
        
        # 脚本文件
        '.sh': TextReader,
        '.bash': TextReader,
        '.bat': TextReader,
        '.ps1': TextReader,
        '.sql': TextReader,
        
        # 办公文档（专用解析器）
        '.docx': DocxReader,
        '.pdf': PdfReader,
        '.pptx': PptxOcrReader,
        '.ppt': PptxOcrReader,
    }
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.success_count = 0
        self.failed_count = 0
    
    def read_all(self, files: List) -> Dict[str, Any]:
        """读取所有文件内容"""
        results = {}
        self.success_count = 0
        self.failed_count = 0
        
        total = len(files)
        
        for i, file_info in enumerate(files):
            ext = file_info.extension.lower()
            
            # 显示进度
            if (i + 1) % 10 == 0 or i == total - 1:
                print(f"   进度: {i + 1}/{total}")
            
            # 读取单个文件
            content_info = self._read_single_file(file_info.absolute_path, ext)
            
            if content_info.get('content') or content_info.get('metadata', {}).get('error'):
                results[file_info.path] = content_info
                if content_info.get('metadata', {}).get('error'):
                    self.failed_count += 1
                else:
                    self.success_count += 1
            else:
                self.failed_count += 1
        
        print(f"\n   读取完成: 成功 {self.success_count} 个, 失败 {self.failed_count} 个")
        
        return results
    
    def read_single(self, file_path: str) -> Dict[str, Any]:
        """读取单个文件"""
        path = Path(file_path)
        
        if not path.exists():
            return {
                'content': None,
                'metadata': {'error': 'file_not_found'}
            }
        
        ext = path.suffix.lower()
        return self._read_single_file(path, ext)
    
    def _read_single_file(self, file_path: Path, ext: str) -> Dict[str, Any]:
        """内部方法：读取单个文件"""
        # 检查空文件
        if file_path.stat().st_size == 0:
            return {
                'content': None,
                'metadata': {
                    'empty': True,
                    'size': 0,
                    'error': 'empty_file'
                }
            }
        
        reader_class = self.READERS.get(ext)
        
        if reader_class:
            try:
                reader = reader_class(self.config)
                content = reader.read(file_path)
                
                if content is not None:
                    return {
                        'content': content,
                        'metadata': reader.get_metadata()
                    }
                else:
                    # 读取失败（但可能是格式问题）
                    return {
                        'content': None,
                        'metadata': reader.get_metadata()
                    }
            except Exception as e:
                return {
                    'content': None,
                    'metadata': {
                        'error': str(e),
                        'exception': True
                    }
                }
        else:
            return {
                'content': None,
                'metadata': {
                    'unsupported': True,
                    'extension': ext
                }
            }
    
    def get_statistics(self):
        return {
            'success_count': self.success_count,
            'failed_count': self.failed_count
        }