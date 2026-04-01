"""PPTX 文件读取器 - 带 OCR 支持（配置化版本）"""

import os
import tempfile
import zipfile
import re
from pathlib import Path
import subprocess

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    Image = None
    ImageEnhance = None
    ImageFilter = None

try:
    import pytesseract
except ImportError:
    pytesseract = None


class PptxSimpleReader:
    """PPTX 文件读取器 - 解压提取图片并进行 OCR"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.metadata = {
            'slides': 0,
            'images_found': 0,
            'ocr_success': 0,
            'ocr_failed': 0,
            'error': None
        }
        
        # 从配置读取 Tesseract 路径
        self.tesseract_cmd = self.config.get('tesseract_cmd')
        self.tessdata_dir = self.config.get('tessdata_dir')
        
        # 如果提供了路径，则配置 pytesseract
        if self.tesseract_cmd and pytesseract:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        
        # 设置环境变量
        if self.tessdata_dir:
            os.environ['TESSDATA_PREFIX'] = self.tessdata_dir
    
    def _preprocess_image(self, img):
        """预处理图片，提高 OCR 识别率"""
        # 转换为灰度图
        img = img.convert('L')
        
        # 增强对比度
        if ImageEnhance:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
        
        # 二值化
        img = img.point(lambda x: 0 if x < 128 else 255, '1')
        
        return img
    
    def _ocr_image(self, img_path):
        """对单张图片进行 OCR"""
        if not pytesseract:
            return None
            
        try:
            img = Image.open(img_path)
            
            # 预处理
            img = self._preprocess_image(img)
            
            # 使用 pytesseract 进行 OCR
            lang = self.config.get('ocr_lang', 'chi_sim+eng')
            text = pytesseract.image_to_string(img, lang=lang)
            
            return text.strip()
            
        except Exception as e:
            print(f"    OCR 失败: {e}")
            return None
    
    def read(self, file_path):
        """解压 PPTX，提取所有图片进行 OCR"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.metadata['error'] = 'file_not_found'
            return None
        
        if pytesseract is None:
            self.metadata['error'] = 'pytesseract_not_installed'
            print("错误: pytesseract 未安装，请运行: pip install pytesseract")
            if self.tesseract_cmd:
                print(f"提示: 已配置 Tesseract 路径: {self.tesseract_cmd}")
            return None
        
        if Image is None:
            self.metadata['error'] = 'pillow_not_installed'
            print("错误: Pillow 未安装，请运行: pip install pillow")
            return None
        
        text_parts = []
        images_found = 0
        ocr_success = 0
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        try:
            print(f"解压 PPTX 文件...")
            
            # 解压 PPTX
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 查找所有图片文件
            image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
            image_files = []
            
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in image_extensions):
                        image_files.append(os.path.join(root, file))
            
            print(f"找到 {len(image_files)} 张图片")
            self.metadata['images_found'] = len(image_files)
            
            # 对每张图片进行 OCR
            for i, img_path in enumerate(image_files, 1):
                try:
                    print(f"  处理图片 {i}/{len(image_files)}...")
                    
                    # OCR 识别
                    text = self._ocr_image(img_path)
                    
                    if text and text.strip():
                        text_parts.append(f"=== 图片 {i} ===")
                        text_parts.append(text.strip())
                        text_parts.append("")
                        ocr_success += 1
                        print(f"    识别成功，长度: {len(text)} 字符")
                    else:
                        print(f"    未识别到文字")
                    
                except Exception as e:
                    print(f"    图片 {i} OCR 失败: {e}")
                    self.metadata['ocr_failed'] = self.metadata.get('ocr_failed', 0) + 1
            
            # 也尝试提取 slide 中的文本（如果有）
            slides_dir = os.path.join(temp_dir, 'ppt', 'slides')
            if os.path.exists(slides_dir):
                slide_files = sorted([f for f in os.listdir(slides_dir) if f.endswith('.xml')])
                print(f"找到 {len(slide_files)} 个幻灯片文件")
                
                for slide_file in slide_files:
                    slide_path = os.path.join(slides_dir, slide_file)
                    try:
                        with open(slide_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # 提取 XML 中的文本
                            texts = re.findall(r'<a:t>(.*?)</a:t>', content)
                            if texts:
                                text_parts.append(f"=== {slide_file} 文本 ===")
                                text_parts.extend([t for t in texts if t.strip()])
                                text_parts.append("")
                    except Exception as e:
                        print(f"  读取 {slide_file} 失败: {e}")
            
            if not text_parts:
                print("⚠️  未提取到任何内容")
                return None
            
            full_text = '\n'.join(text_parts)
            
            # 更新元数据
            self.metadata.update({
                'ocr_success': ocr_success,
                'ocr_failed': self.metadata.get('ocr_failed', 0)
            })
            
            print(f"\n✅ OCR 完成，成功识别 {ocr_success}/{len(image_files)} 张图片")
            
            return full_text
            
        except Exception as e:
            print(f"处理失败: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # 清理临时目录
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def get_metadata(self):
        return self.metadata