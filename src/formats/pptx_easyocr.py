import easyocr

class PptxEasyOCRReader:
    def __init__(self, config=None):
        self.config = config or {}
        self.reader = easyocr.Reader(['ch_sim', 'en'])  # 中英文
    
    def read(self, file_path):
        # 使用 easyocr 识别图片
        result = self.reader.readtext(image_data)
        text = ' '.join([item[1] for item in result])
        return text