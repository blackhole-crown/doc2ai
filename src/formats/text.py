"""文本文件读取器 - 支持所有文本格式"""

from pathlib import Path


class TextReader:
    """文本文件读取器 - 支持所有文本格式"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.metadata = {
            'encoding': None,
            'line_count': 0,
            'displayed_lines': 0,
            'truncated': False,
            'size': 0,
            'empty': False,
            'error': None
        }
    
    def read(self, file_path):
        """读取文本文件"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.metadata['error'] = 'file_not_found'
            return None
        
        # 检查空文件
        if file_path.stat().st_size == 0:
            self.metadata = {
                'empty': True,
                'size': 0,
                'line_count': 0,
                'displayed_lines': 0,
                'truncated': False,
                'error': None
            }
            return None
        
        # 尝试不同的编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'ascii', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    
                    # 限制行数
                    max_lines = self.config.get('max_lines', 500)
                    lines = content.split('\n')
                    original_lines = len(lines)
                    
                    if len(lines) > max_lines:
                        lines = lines[:max_lines//2] + ['... 省略中间内容 ...'] + lines[-max_lines//2:]
                        content = '\n'.join(lines)
                        truncated = True
                    else:
                        truncated = False
                    
                    self.metadata = {
                        'encoding': encoding,
                        'line_count': original_lines,
                        'displayed_lines': len(lines),
                        'truncated': truncated,
                        'size': file_path.stat().st_size,
                        'empty': False,
                        'error': None
                    }
                    
                    return content
                    
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"读取失败 ({encoding}): {e}")
                continue
        
        self.metadata['error'] = 'encoding_failed'
        print(f"无法读取文件: {file_path}")
        return None
    
    def get_metadata(self):
        """返回元数据"""
        return self.metadata