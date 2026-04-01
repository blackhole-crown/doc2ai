"""PPTX 文件读取器 - 使用 XML 直接提取"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


class PptxXmlReader:
    """通过解析 XML 直接提取文本（更可靠）"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.metadata = {}
    
    def read(self, file_path):
        """通过解压 PPTX 文件直接读取 XML 中的文本"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return None
        
        text_parts = []
        
        try:
            # PPTX 本质是 ZIP 文件
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # 获取所有 slide 文件
                slide_files = [f for f in zip_ref.namelist() 
                              if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
                slide_files.sort()
                
                print(f"找到 {len(slide_files)} 个幻灯片文件")
                
                for i, slide_file in enumerate(slide_files, 1):
                    with zip_ref.open(slide_file) as f:
                        content = f.read().decode('utf-8')
                        
                        # 提取所有 <a:t> 标签中的文本
                        # 使用简单的正则或 XML 解析
                        import re
                        texts = re.findall(r'<a:t>(.*?)</a:t>', content)
                        
                        if texts:
                            text_parts.append(f"=== 第 {i} 页 ===")
                            text_parts.extend([t for t in texts if t.strip()])
                            text_parts.append("")
            
            if not text_parts:
                print("未找到文本内容")
                return None
            
            full_text = '\n'.join(text_parts)
            print(f"XML 提取完成，共 {len(full_text)} 字符")
            
            return full_text
            
        except Exception as e:
            print(f"XML 提取失败: {e}")
            return None
    
    def get_metadata(self):
        return self.metadata