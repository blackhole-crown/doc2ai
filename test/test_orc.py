import pytesseract
from PIL import Image
import os

# 设置 Tesseract 路径
pytesseract.pytesseract.tesseract_cmd = r'D:\Mine\Tools\tesseract\tesseract.exe'

# 方法1：修改环境变量指向 tessdata 目录
os.environ['TESSDATA_PREFIX'] = r'D:\Mine\Tools\tesseract\tessdata'

# 测试图片
img_path = r"C:\Users\Administrator\Desktop\屏幕截图 2026-03-30 194401.png"

print("打开图片...")
img = Image.open(img_path)
print(f"图片尺寸: {img.size}")

print("\n开始 OCR 识别...")

# 先测试英文
try:
    text = pytesseract.image_to_string(img, lang='eng')
    print("英文识别成功")
    print(text[:200])
except Exception as e:
    print(f"英文识别失败: {e}")

# 测试中英文
print("\n测试中英文...")
try:
    text = pytesseract.image_to_string(img, lang='chi_sim+eng')
    print("\n识别结果:")
    print(text)
except Exception as e:
    print(f"中英文识别失败: {e}")