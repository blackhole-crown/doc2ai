"""格式支持模块"""

from .text import TextReader
from .docx import DocxReader
from .pdf import PdfReader
from .pptx import PptxReader
from .pptx_ocr import PptxOcrReader

__all__ = ['TextReader', 'DocxReader', 'PdfReader', 'PptxReader', 'PptxOcrReader']