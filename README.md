# Doc2AI

> 智能文档/文件夹分析工具 - 将项目或文档转换为 AI 友好的 JSON 格式

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-PEP8-brightgreen.svg)](https://www.python.org/dev/peps/pep-0008/)

## 📖 简介

Doc2AI 是一个专门解决 AI 无法直接读取文档和文件夹问题的工具。它能将：
- **整个文件夹**（包括目录结构和文件内容）转换为结构化的 JSON/JSONL 格式
- **单个文档**（TXT, MD, DOCX, PDF, PPTX 等）解析为纯文本

让 AI 能够轻松理解项目结构、文档内容和文件关系。

### 核心特性

- 🗂️ **完整目录结构** - 保留原始文件夹的层级结构
- 📄 **多格式支持** - 支持 50+ 种文件格式（代码、文档、配置等）
- 🔍 **OCR 识别** - 自动识别 PPTX 中的图片文字（需配置 Tesseract）
- ⚙️ **灵活配置** - 支持文件过滤、大小限制、内容截断等
- 🚀 **多种使用方式** - 命令行工具 + REST API + Web 界面
- 📊 **智能统计** - 自动统计文件数量、大小分布、文件类型
- 🎯 **AI 友好输出** - 自动生成项目描述，便于 AI 理解

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/yourname/doc2ai.git
cd doc2ai

# 安装依赖
pip install -r requirements.txt

# 安装为命令行工具
pip install -e .
```

### 基本使用

#### 命令行

```bash
# 处理文件夹
doc2ai /path/to/your/project -o output.json

# 处理单个文件
doc2ai document.pdf -o output.json

# 处理 PPTX 并启用 OCR
doc2ai presentation.pptx --use-ocr --tesseract-cmd "D:/Tools/tesseract/tesseract.exe"

# 紧凑格式输出
doc2ai /path/to/project --compact -o output.json

# 只处理特定类型文件
doc2ai /path/to/project --include-ext .py .md -o output.json

# 排除特定目录
doc2ai /path/to/project --exclude .git node_modules dist -o output.json

# 限制每个文件最多 200 行
doc2ai /path/to/project --max-lines 200 -o output.json
```

#### Python 代码

```python
from src.core.reader import DocumentReader

# 处理文件夹
reader = DocumentReader({'max_lines': 500})
files = scan_folder('/path/to/project')
contents = reader.read_all(files)

# 处理单个文件
content = reader.read_single('document.pdf')
print(content['content'])
```

#### Web 界面

```bash
# 启动 Web 服务
python run.py
# 访问 http://localhost:5000
```

## 📊 输出格式

### JSON 格式（文件夹）

```json
{
  "metadata": {
    "project_name": "myproject",
    "processed_at": "2026-03-30T10:30:00Z",
    "ai_description": "你好，这是一个【myproject】项目..."
  },
  "statistics": {
    "total_files": 42,
    "total_size_human": "2.34 MB",
    "file_types": {".py": 15, ".md": 5, ".txt": 22}
  },
  "files": [
    {
      "file_info": {"path": "src/main.py", "size_human": "1.21 KB"},
      "content": {"raw": "print('Hello World')"},
      "metadata": {"line_count": 45}
    }
  ]
}
```

### JSON 格式（单个文件）

```json
{
  "metadata": {
    "file_name": "document.pdf",
    "file_type": ".pdf",
    "file_size": "277.68 KB",
    "ai_description": "你好，这是一个【document.pdf】文件..."
  },
  "content": "文件内容...",
  "metadata_extracted": {"pages": 5, "has_text": true}
}
```

## 🔧 配置选项

通过 `src/config/default_config.yaml` 或命令行参数配置：

```yaml
processing:
  max_file_size_mb: 10          # 最大文件大小
  exclude_patterns:             # 排除模式
    - ".git"
    - "__pycache__"

analysis:
  max_line_count: 500           # 最大行数
  truncate_mode: "head_tail"    # 截断模式

ocr:
  enabled: true                 # 启用 OCR
  lang: "chi_sim+eng"           # 识别语言
  tesseract_cmd: ""             # Tesseract 路径
```

## 📦 项目结构

```
doc2ai/
├── README.md                   # 项目文档
├── requirements.txt            # 依赖列表
├── setup.py                    # 安装配置
├── run.py                      # Web 服务入口
├── src/                        # 源代码
│   ├── main.py                 # 命令行入口
│   ├── core/                   # 核心处理逻辑
│   │   ├── scanner.py          # 文件夹扫描
│   │   ├── reader.py           # 文档读取（统一接口）
│   │   └── ...
│   ├── formats/                # 格式解析器
│   │   ├── text.py             # 文本文件
│   │   ├── docx.py             # Word 文档
│   │   ├── pdf.py              # PDF 文档
│   │   └── pptx_ocr.py         # PPTX + OCR
│   ├── output/                 # 输出格式化
│   └── config/                 # 配置管理
└── web/                        # Web 界面
    ├── app.py                  # Flask 应用
    ├── templates/              # HTML 模板
    └── static/                 # CSS/JS 文件
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 添加适当的注释和文档字符串
- 编写单元测试

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**让 AI 更好地理解你的文档！** 🚀