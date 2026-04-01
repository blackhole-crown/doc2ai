#!/usr/bin/env python3
"""
使用示例
"""

import json
from pathlib import Path
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.processor import FolderProcessor
from src.config.config_manager import ConfigManager


def example_basic():
    """基本使用示例"""
    print("=== Basic Example ===")
    
    # 初始化配置
    config_manager = ConfigManager()
    
    # 修改配置
    config_manager.set("processing.max_file_size_mb", 5)
    config_manager.set("analysis.max_line_count", 200)
    
    # 创建处理器
    processor = FolderProcessor(config_manager.config)
    
    # 处理文件夹
    result = processor.process("./sample_project")
    
    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False)[:1000] + "...")
    
    return result


def example_with_progress():
    """带进度回调的示例"""
    print("\n=== Progress Example ===")
    
    def progress_callback(percentage, message):
        print(f"[{percentage:3d}%] {message}")
    
    config_manager = ConfigManager()
    processor = FolderProcessor(config_manager.config)
    
    result = processor.process("./sample_project", progress_callback)
    
    # 显示统计信息
    stats = result.get("statistics", {})
    print(f"\nStatistics:")
    print(f"  Total files: {stats.get('total_files', 0)}")
    print(f"  Total size: {stats.get('total_size_human', '0')}")
    print(f"  Skipped files: {stats.get('skipped_files', 0)}")
    
    return result


def example_custom_config():
    """自定义配置示例"""
    print("\n=== Custom Config Example ===")
    
    config_manager = ConfigManager()
    
    # 自定义配置
    custom_config = {
        "processing": {
            "max_file_size_mb": 1,
            "exclude_patterns": [".git", "*.log", "temp"],
            "include_extensions": [".py", ".md", ".txt"]
        },
        "analysis": {
            "max_line_count": 100,
            "truncate_mode": "head_only",
            "head_lines": 50
        },
        "output": {
            "format": "compact",
            "include_metadata": False
        }
    }
    
    config_manager.update(custom_config)
    processor = FolderProcessor(config_manager.config)
    
    result = processor.process("./sample_project")
    
    print(f"Output format: {config_manager.get('output.format')}")
    print(f"Files processed: {result['statistics']['total_files']}")
    
    return result


def save_to_file(result, filename):
    """保存结果到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nResult saved to: {filename}")


if __name__ == "__main__":
    # 创建示例项目
    sample_dir = Path("./sample_project")
    sample_dir.mkdir(exist_ok=True)
    
    # 创建示例文件
    (sample_dir / "README.md").write_text("# Sample Project\n\nThis is a sample project.")
    (sample_dir / "main.py").write_text("print('Hello World')\n\n\ndef main():\n    print('Hello')")
    
    src_dir = sample_dir / "src"
    src_dir.mkdir(exist_ok=True)
    (src_dir / "utils.py").write_text("def helper():\n    return 'help'")
    
    # 运行示例
    result1 = example_basic()
    result2 = example_with_progress()
    result3 = example_custom_config()
    
    # 保存结果
    save_to_file(result1, "output_basic.json")
    save_to_file(result3, "output_compact.json")