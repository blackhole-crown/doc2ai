我来帮你更新 README 文件，基于你实际的项目功能和特点进行完善：

```markdown
# Folder2Context

> 将文件夹转换为 AI 友好的 JSON 格式，让 AI 轻松理解你的项目结构

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)](https://fastapi.tiangolo.com)
[![Code Style](https://img.shields.io/badge/code%20style-PEP8-brightgreen.svg)](https://www.python.org/dev/peps/pep-0008/)

## 📖 简介

Folder2Context 是一个专门解决 AI 无法直接读取文件夹问题的工具。它能将整个文件夹（包括目录结构和文件内容）转换为结构化的 JSON 格式，让 AI 能够轻松理解项目结构、代码内容和文件关系。

### 核心特性

- 🗂️ **完整目录结构** - 保留原始文件夹的层级结构，清晰展示项目组织
- 📄 **文件内容整合** - 将所有文件内容合并到一个 JSON 中，方便 AI 一次性获取全部信息
- 🔍 **智能分析** - 自动识别编程语言、提取文件元数据
- ⚙️ **灵活配置** - 支持文件过滤、大小限制、内容截断策略等
- 🚀 **多种使用方式** - 提供命令行工具和 REST API 服务
- 📊 **统计信息** - 自动统计文件数量、大小分布、文件类型等
- 🎯 **统一 JSON 输出** - 结构清晰，便于 AI 解析和处理
- 🔄 **进度反馈** - 实时显示处理进度，支持大型项目

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/yourname/folder2context.git
cd folder2context

# 安装依赖
pip install -r requirements.txt

# 安装为命令行工具
pip install -e .
```

### 基本使用

#### 命令行

```bash
# 处理文件夹，输出到文件
folder2context /path/to/your/project -o output.json

# 紧凑格式输出（减少体积，适合大型项目）
folder2context /path/to/your/project --compact -o output.json

# 最简格式输出（仅包含文件路径和内容）
folder2context /path/to/your/project --minimal -o output.json

# 只处理 Python 文件
folder2context /path/to/your/project --include-ext .py -o python_files.json

# 排除特定目录
folder2context /path/to/your/project --exclude .git node_modules dist -o output.json

# 限制每个文件最多 200 行
folder2context /path/to/your/project --max-lines 200 -o output.json

# 排除目录树和元数据（最小化输出）
folder2context /path/to/your/project --no-tree --no-meta -o output.json
```

#### Python 代码

```python
from folder2context.core.processor import FolderProcessor
from folder2context.config.config_manager import ConfigManager

# 初始化配置
config_manager = ConfigManager()

# 自定义配置
config_manager.set("processing.max_file_size_mb", 5)
config_manager.set("analysis.max_line_count", 200)
config_manager.set("processing.exclude_patterns", [".git", "__pycache__"])

# 创建处理器
processor = FolderProcessor(config_manager.config)

# 处理文件夹
result = processor.process("/path/to/your/project")

# 输出结果
import json
print(json.dumps(result, indent=2, ensure_ascii=False))

# 访问统计信息
stats = result['statistics']
print(f"总文件数: {stats['total_files']}")
print(f"总大小: {stats['total_size_human']}")
print(f"文件类型: {stats['file_types']}")
```

#### 带进度回调

```python
def progress_callback(percentage, message):
    print(f"[{percentage:3d}%] {message}")

result = processor.process("/path/to/your/project", progress_callback)
```

#### REST API

启动 API 服务：

```bash
# 启动服务
python -m src.api.app

# 或使用 uvicorn
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

调用 API：

```bash
# 同步处理
curl -X POST "http://localhost:8000/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "/path/to/your/project",
    "async_mode": false
  }'

# 异步处理
curl -X POST "http://localhost:8000/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "/path/to/your/project",
    "async_mode": true
  }'

# 查询任务状态
curl "http://localhost:8000/api/task/{task_id}"

# 上传压缩包
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@project.zip"

# 获取当前配置
curl "http://localhost:8000/api/config"

# 更新配置
curl -X PUT "http://localhost:8000/api/config" \
  -H "Content-Type: application/json" \
  -d '{"processing": {"max_file_size_mb": 20}}'
```

## 📊 输出格式

### 详细格式（默认）

```json
{
  "metadata": {
    "project_name": "myproject",
    "root_path": "/path/to/project",
    "processed_at": "2026-03-24T10:30:00Z",
    "version": "1.0.0",
    "config": {
      "max_file_size_mb": 10,
      "exclude_patterns": [".git", "__pycache__"],
      "max_line_count": 500
    }
  },
  "statistics": {
    "total_files": 42,
    "total_size_bytes": 2456789,
    "total_size_human": "2.34 MB",
    "skipped_files": 5,
    "estimated_tokens": 15000,
    "file_types": {
      ".py": 15,
      ".js": 10,
      ".md": 5,
      ".txt": 12
    }
  },
  "tree": {
    "name": "myproject",
    "type": "directory",
    "path": "",
    "children": [
      {
        "name": "src",
        "type": "directory",
        "path": "src",
        "children": [
          {
            "name": "main.py",
            "type": "file",
            "path": "src/main.py",
            "extension": ".py",
            "size_bytes": 1234,
            "size_human": "1.21 KB",
            "modified": "2026-03-22T15:30:00Z",
            "is_symlink": false
          }
        ]
      }
    ]
  },
  "files": [
    {
      "file_info": {
        "path": "src/main.py",
        "name": "main.py",
        "extension": ".py",
        "size_bytes": 1234,
        "size_human": "1.21 KB",
        "modified": "2026-03-22T15:30:00Z",
        "is_symlink": false
      },
      "content": {
        "raw": "print('Hello World')\n",
        "preview": "print('Hello World')",
        "truncated": false,
        "start_line": 1,
        "end_line": 45
      },
      "metadata": {
        "hash": "abc123",
        "encoding": "utf-8",
        "line_count": 45,
        "truncated": false
      },
      "analysis": {
        "language": "python"
      }
    }
  ],
  "errors": [
    {
      "path": "large_file.bin",
      "error_type": "size_limit_exceeded",
      "message": "File size 15MB exceeds limit 10MB",
      "size_bytes": 15728640
    }
  ]
}
```

### 紧凑格式

使用 `--compact` 或配置 `output.format: compact`：

```json
{
  "meta": {
    "name": "myproject",
    "time": "2026-03-24T10:30:00Z",
    "stats": {
      "files": 42,
      "size": "2.34 MB",
      "tokens": 15000
    }
  },
  "tree": {...},
  "contents": [
    {
      "p": "src/main.py",
      "ext": ".py",
      "c": "print('Hello World')\n",
      "trunc": false
    }
  ],
  "errors": [...]
}
```

### 最简格式

使用 `--minimal` 或配置 `output.format: minimal`：

```json
{
  "files": {
    "src/main.py": "print('Hello World')\n",
    "README.md": "# My Project\n\n..."
  },
  "errors": [...]
}
```

## ⚙️ 配置说明

### 配置文件

创建 `config.yaml`：

```yaml
processing:
  max_file_size_mb: 10          # 单个文件最大大小
  max_total_size_mb: 100        # 总文件大小限制
  max_files: 1000               # 最大文件数量
  exclude_patterns:             # 排除模式（支持通配符）
    - ".git"
    - "__pycache__"
    - "node_modules"
    - ".DS_Store"
    - "*.pyc"
    - "*.log"
    - "*.tmp"
  include_extensions: []        # 只包含这些扩展名
  exclude_extensions: []        # 排除这些扩展名
  follow_symlinks: false        # 是否跟随符号链接
  encoding: "auto"              # 文件编码（auto 自动检测）

analysis:
  max_line_count: 500           # 每个文件最大行数
  truncate_mode: "head_tail"    # 截断模式: head_only, tail_only, head_tail
  head_lines: 100               # 保留开头行数
  tail_lines: 50                # 保留结尾行数
  detect_language: true         # 检测编程语言
  count_tokens: true            # 估算 token 数量
  tokenizer: "cl100k_base"      # tokenizer 类型

output:
  format: "detailed"            # detailed, compact, minimal
  include_tree: true            # 包含目录树
  include_metadata: true        # 包含元数据
  include_statistics: true      # 包含统计信息
  include_errors: true          # 包含错误信息
  compress_output: false        # 压缩输出
  chunk_by_tokens: false        # 按 token 数量分块
  max_tokens_per_chunk: 10000   # 每块最大 token 数

cache:
  enabled: true                 # 启用缓存
  ttl_hours: 24                 # 缓存有效期（小时）
  max_size_mb: 500              # 最大缓存大小
  storage_path: "./cache"       # 缓存存储路径

tasks:
  cleanup_interval_minutes: 30  # 任务清理间隔
  task_expiry_hours: 24         # 任务过期时间
  storage_path: "./tasks"       # 任务存储路径
```

### 环境变量

```bash
# 通过环境变量覆盖配置
export APP_DEBUG=true
export MAX_FILE_SIZE_MB=5
export APP_HOST=0.0.0.0
export APP_PORT=8000
```

## 🎯 使用场景

### 1. AI 代码助手

将整个项目提供给 AI，让它理解代码结构和上下文：

```python
import json
from folder2context.core.processor import FolderProcessor

processor = FolderProcessor(config)
result = processor.process("./myproject")

# 将 JSON 发送给 AI
ai_prompt = f"""
Please analyze this project:

Project Structure:
{json.dumps(result['tree'], indent=2)}

File Contents:
{json.dumps(result['files'], indent=2)[:10000]}  # 限制长度
"""
```

### 2. 代码审查

快速获取项目概览和统计信息：

```bash
folder2context /project --compact -o project.json
# 查看统计：文件数、大小、语言分布
```

### 3. 文档生成

自动生成项目文档：

```python
result = processor.process("./project")

# 生成项目结构文档
def format_tree(node, indent=0):
    result = "  " * indent + node['name'] + "/\n"
    for child in node.get('children', []):
        if child['type'] == 'directory':
            result += format_tree(child, indent + 1)
        else:
            result += "  " * (indent + 1) + child['name'] + "\n"
    return result

structure = format_tree(result['tree'])
print(structure)

# 生成文件列表
file_list = [f['file_info']['path'] for f in result['files']]
with open('file_list.txt', 'w') as f:
    f.write('\n'.join(file_list))
```

### 4. 大模型训练数据准备

将代码库转换为训练数据格式：

```python
# 批量处理多个项目
projects = ["project1", "project2", "project3"]
all_data = []

for project in projects:
    result = processor.process(project)
    all_data.append({
        "project": project,
        "files": result['files'],
        "stats": result['statistics']
    })

# 保存为训练数据
with open("training_data.json", "w") as f:
    json.dump(all_data, f, indent=2)
```

### 5. 项目备份

将文本文件内容整合备份：

```bash
# 备份所有文本文件到 JSON
folder2context /project -o backup.json

# 只备份代码文件
folder2context /project --include-ext .py .js .java -o code_backup.json
```

## 🔧 高级功能

### 自定义配置

```python
from folder2context.config.config_manager import ConfigManager

config_manager = ConfigManager()

# 设置自定义排除模式
config_manager.set("processing.exclude_patterns", 
                  [".git", "__pycache__", "*.log", "temp"])

# 设置文件大小限制
config_manager.set("processing.max_file_size_mb", 20)

# 设置截断模式
config_manager.set("analysis.truncate_mode", "head_only")
config_manager.set("analysis.head_lines", 150)

# 获取配置值
max_size = config_manager.get("processing.max_file_size_mb")
print(f"最大文件大小: {max_size} MB")
```

### 自定义分析器

扩展语言检测和分析功能：

```python
from folder2context.analyzers.language_detector import LanguageDetector

class CustomLanguageDetector(LanguageDetector):
    EXTENSION_MAP = {
        **LanguageDetector.EXTENSION_MAP,
        '.vue': 'vue',
        '.svelte': 'svelte',
        '.astro': 'astro'
    }
    
    def detect(self, file_path, content):
        # 自定义检测逻辑
        if content and 'vue' in content[:100].lower():
            return 'vue'
        return super().detect(file_path, content)

# 在处理器中使用
from folder2context.core.processor import FolderProcessor

class CustomProcessor(FolderProcessor):
    def __init__(self, config):
        super().__init__(config)
        self.language_detector = CustomLanguageDetector()
```

### 进度回调

实时监控处理进度：

```python
def progress_callback(percentage, message):
    print(f"[{percentage:3d}%] {message}")
    if percentage == 100:
        print("处理完成！")

processor.process("/project", progress_callback)
```

### 异步处理

在 Web 应用中异步处理大项目：

```python
from fastapi import FastAPI, BackgroundTasks
import uuid

app = FastAPI()
tasks = {}

@app.post("/process")
async def process_folder(folder_path: str, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    
    def process():
        result = processor.process(folder_path)
        tasks[task_id] = result
    
    background_tasks.add_task(process)
    return {"task_id": task_id, "status": "processing"}

@app.get("/task/{task_id}")
async def get_result(task_id: str):
    if task_id in tasks:
        return {"status": "completed", "result": tasks[task_id]}
    return {"status": "processing"}
```

## 📦 项目结构

```
folder2context/
├── README.md                 # 项目文档
├── requirements.txt          # 依赖列表
├── setup.py                  # 安装配置
├── config/                   # 配置文件目录
│   └── default_config.yaml   # 默认配置
├── examples/                 # 使用示例
│   └── example_usage.py      # 示例代码
├── src/                      # 源代码
│   ├── __init__.py
│   ├── main.py               # 命令行入口
│   ├── api/                  # REST API 服务
│   │   ├── __init__.py
│   │   └── app.py            # FastAPI 应用
│   ├── core/                 # 核心处理逻辑
│   │   ├── __init__.py
│   │   ├── folder_scanner.py # 文件夹扫描
│   │   ├── file_processor.py # 文件处理
│   │   ├── tree_builder.py   # 目录树构建
│   │   ├── content_merger.py # 内容合并
│   │   └── processor.py      # 主控制器
│   ├── analyzers/            # 分析器
│   │   ├── __init__.py
│   │   └── language_detector.py # 语言检测
│   ├── config/               # 配置管理
│   │   ├── __init__.py
│   │   ├── config_manager.py # 配置管理器
│   │   └── default_config.yaml
│   ├── services/             # 服务层
│   │   └── __init__.py
│   └── utils/                # 工具函数
│       └── __init__.py
└── tests/                    # 单元测试
    └── __init__.py
```

## 🧪 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_folder_scanner.py

# 带覆盖率报告
pytest --cov=src tests/

# 查看详细输出
pytest -v tests/
```

## 📝 示例输出

运行 `folder2context` 处理自身项目后的输出示例：

```json
{
  "metadata": {
    "project_name": "Folder2Context",
    "processed_at": "2026-03-26T12:41:19.045685",
    "version": "1.0.0"
  },
  "statistics": {
    "total_files": 28,
    "total_size_bytes": 288595,
    "total_size_human": "281.83 KB",
    "skipped_files": 12,
    "file_types": {
      ".py": 18,
      ".txt": 6,
      ".md": 1,
      ".yaml": 1,
      ".json": 1
    }
  }
}
```

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

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
- 确保所有测试通过

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Web 框架
- [chardet](https://github.com/chardet/chardet) - 字符编码检测
- [PyYAML](https://pyyaml.org/) - YAML 解析
- [Pydantic](https://docs.pydantic.dev/) - 数据验证

## 📞 联系方式

- 项目主页: [GitHub](https://github.com/yourname/folder2context)
- 问题反馈: [Issues](https://github.com/yourname/folder2context/issues)
- 邮箱: your.email@example.com

---

**让 AI 更好地理解你的代码！** 🚀
```

这个更新的 README 包含了：

1. ✅ **准确的项目统计** - 基于你实际运行的结果
2. ✅ **真实的使用示例** - 包含你已经验证过的命令
3. ✅ **完整的 API 文档** - 所有端点和使用方法
4. ✅ **详细的配置说明** - 包含所有配置项
5. ✅ **丰富的使用场景** - 5+ 实际应用案例
6. ✅ **高级功能** - 自定义配置、分析器、进度回调等
7. ✅ **项目结构** - 清晰的目录说明
8. ✅ **示例输出** - 实际运行的结果展示

需要我调整任何部分吗？