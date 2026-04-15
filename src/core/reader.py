"""文档读取器 - 统一处理各种文件"""

from pathlib import Path
from typing import List, Dict, Any

from src.formats.text import TextReader
from src.formats.docx import DocxReader
from src.formats.pdf import PdfReader
from src.formats.pptx_ocr import PptxOcrReader


class DocumentReader:
    """统一文档读取器"""
    
    # 格式映射 - 所有文本格式都使用 TextReader
    READERS = {
        # 代码文件
        '.py': TextReader,
        '.js': TextReader,
        '.ts': TextReader,        # TypeScript
        '.jsx': TextReader,       # React JSX
        '.tsx': TextReader,       # React TSX
        '.vue': TextReader,       # Vue 组件
        '.svelte': TextReader,    # Svelte 组件
        '.astro': TextReader,     # Astro 组件
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
        
        # 样式文件
        '.css': TextReader,
        '.scss': TextReader,      # SCSS
        '.sass': TextReader,      # Sass
        '.less': TextReader,      # Less
        '.styl': TextReader,      # Stylus
        
        # 数据/模板文件
        '.csv': TextReader,
        '.xml': TextReader,
        '.html': TextReader,
        
        # 脚本文件
        '.sh': TextReader,
        '.bash': TextReader,
        '.bat': TextReader,
        '.ps1': TextReader,
        '.sql': TextReader,
        
        # GraphQL
        '.graphql': TextReader,
        '.gql': TextReader,
        
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
        self._failed_file_ids = []  # 新增：记录失败的文件 ID
    
    def read_all(self, files: List) -> Dict[int, Any]:
        """
        读取所有文件内容
        返回: {file_id: content_dict}
        """
        results = {}
        self.success_count = 0
        self.failed_count = 0
        self._failed_file_ids = []
        
        total = len(files)
        
        for i, file_info in enumerate(files):
            ext = file_info.extension.lower()
            
            # 显示进度
            if (i + 1) % 10 == 0 or i == total - 1:
                print(f"   进度: {i + 1}/{total}")
            
            # 读取单个文件
            content_info = self._read_single_file(file_info.absolute_path, ext)
            
            # 使用 file_info.id 作为 key
            results[file_info.id] = {
                'file_id': file_info.id,
                'file_info': {
                    'path': file_info.path,
                    'name': file_info.name,
                    'extension': file_info.extension,
                    'size_bytes': file_info.size_bytes,
                    'size_human': self._format_size(file_info.size_bytes),
                    'modified': file_info.modified.isoformat()
                },
                'content': content_info.get('content', ''),
                'metadata': content_info.get('metadata', {})
            }
            
            # 判断是否成功
            if content_info.get('metadata', {}).get('error'):
                self.failed_count += 1
                self._failed_file_ids.append(file_info.id)
                results[file_info.id]['status'] = 'failed'
            else:
                self.success_count += 1
                results[file_info.id]['status'] = 'success'
        
        print(f"\n   读取完成: 成功 {self.success_count} 个, 失败 {self.failed_count} 个")
        
        return results
    
    def read_single(self, file_path: str) -> Dict[str, Any]:
        """读取单个文件（不包含 ID）"""
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
                    return {
                        'content': None,
                        'metadata': reader.get_metadata() if reader.get_metadata() else {'error': 'read_failed'}
                    }
            except Exception as e:
                return {
                    'content': None,
                    'metadata': {
                        'error': str(e),
                        'error_type': 'exception'
                    }
                }
        else:
            return {
                'content': None,
                'metadata': {
                    'unsupported': True,
                    'extension': ext,
                    'error': 'unsupported_format'
                }
            }
    
    def get_statistics(self):
        return {
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'failed_file_ids': self._failed_file_ids
        }
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"