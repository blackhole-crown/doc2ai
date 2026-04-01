"""PDF 文件读取器"""

import os
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
    print("警告: PyMuPDF 未安装，请运行: pip install PyMuPDF")


class PdfReader:
    """PDF 文档读取器"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.metadata = {
            'pages': 0,
            'page_count': 0,
            'truncated': False,
            'line_count': 0,
            'displayed_lines': 0,
            'size': 0,
            'error': None
        }
    
    def read(self, file_path):
        """读取 PDF 文件"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.metadata['error'] = 'file_not_found'
            print(f"文件不存在: {file_path}")
            return None
        
        if fitz is None:
            self.metadata['error'] = 'PyMuPDF_not_installed'
            print("错误: PyMuPDF 未安装，请运行: pip install PyMuPDF")
            return None
        
        doc = None
        try:
            # 打开 PDF 文件
            doc = fitz.open(str(file_path))
            
            if doc.is_closed:
                self.metadata['error'] = 'document_closed'
                print(f"PDF 文件无法打开: {file_path}")
                return None
            
            text_parts = []
            total_pages = len(doc)
            
            # 提取每一页的内容
            for page_num in range(total_pages):
                page = doc[page_num]
                page_text = page.get_text()
                
                if page_text and page_text.strip():
                    text_parts.append(f"=== 第 {page_num + 1} 页 ===")
                    text_parts.append(page_text)
                    text_parts.append("")
            
            # 关闭文档
            doc.close()
            
            if not text_parts:
                self.metadata['error'] = 'no_text_content'
                print(f"PDF 文件没有文本内容: {file_path}")
                return None
            
            full_text = '\n'.join(text_parts)
            
            # 限制行数
            max_lines = self.config.get('max_lines', 500)
            lines = full_text.split('\n')
            original_lines = len(lines)
            
            if len(lines) > max_lines:
                lines = lines[:max_lines//2] + ['... 省略中间内容 ...'] + lines[-max_lines//2:]
                full_text = '\n'.join(lines)
                truncated = True
            else:
                truncated = False
            
            # 更新元数据
            self.metadata = {
                'pages': total_pages,
                'page_count': total_pages,
                'truncated': truncated,
                'line_count': original_lines,
                'displayed_lines': len(lines),
                'size': file_path.stat().st_size,
                'error': None
            }
            
            return full_text
            
        except Exception as e:
            self.metadata['error'] = str(e)
            print(f"读取 PDF 失败: {e}")
            if doc and not doc.is_closed:
                doc.close()
            return None
    
    def get_metadata(self):
        """返回元数据"""
        return self.metadata