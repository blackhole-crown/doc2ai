#!/usr/bin/env python3
"""
Doc2AI - 智能文档/文件夹分析工具
- 文件夹：扫描并读取所有文本文件
- 文件：根据格式智能解析（TXT, MD, DOCX, PDF, 代码文件等）
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.scanner import FolderScanner
from src.core.reader import DocumentReader
from src.formats.text import TextReader
from src.formats.docx import DocxReader
from src.formats.pdf import PdfReader
from src.output.json_formatter import JSONFormatter
from src.output.jsonl_formatter import JSONLFormatter


def get_output_path(input_path, output_dir=None):
    """自动生成输出路径"""
    name = Path(input_path).stem if Path(input_path).is_file() else Path(input_path).name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if output_dir is None:
        output_dir = Path.cwd() / "data"
    else:
        output_dir = Path(output_dir)
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 文件名
    filename = f"{name}_{timestamp}"
    
    return output_dir, filename


def generate_description(name, stats, is_folder=True):
    """生成 AI 友好的项目描述"""
    if is_folder:
        file_types = stats.get('file_types', {})
        main_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:3]
        main_type_str = "、".join([f"{ext} ({count}个)" for ext, count in main_types if ext])
        
        description = f"""你好，这是一个【{name}】项目，请你来解析这个项目。

项目概览：
- 项目名称：{name}
- 文件总数：{stats.get('total_files', 0)} 个
- 项目大小：{stats.get('total_size_human', '0')}
- 主要文件类型：{main_type_str if main_type_str else '无'}

请帮我分析这个项目的结构、主要功能和代码质量。
以下是项目的完整结构和文件内容："""
    else:
        description = f"""你好，这是一个【{name}】文件，请你来解析这个文件。

文件信息：
- 文件名称：{name}
- 文件类型：{stats.get('file_type', 'unknown')}
- 文件大小：{stats.get('file_size_human', '0')}

请帮我分析这个文件的内容和要点。
以下是文件的完整内容："""
    
    return description


def process_folder(folder_path, args):
    """处理文件夹（原 f2c 功能）"""
    print(f"📁 处理模式: 文件夹")
    print(f"   路径: {folder_path}")
    
    # 配置
    config = {
        'max_lines': args.max_lines or 500,
        'compact': args.compact,
        'extract_tables': args.extract_tables
    }
    
    # 输出路径
    output_dir, filename = get_output_path(folder_path, args.output)
    project_dir = output_dir / f"{Path(folder_path).name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 扫描文件夹
    print(f"\n⏳ 扫描文件夹...")
    scanner = FolderScanner(config)
    files = scanner.scan(str(folder_path))
    stats = scanner.get_statistics()
    
    print(f"   找到 {stats['total_files']} 个文件")
    
    # 2. 读取文件内容
    print(f"\n⏳ 读取文件内容...")
    reader = DocumentReader(config)
    contents = reader.read_all(files)
    
    # 更新统计
    stats.update(reader.get_statistics())
    
    # 3. 生成输出
    print(f"\n⏳ 生成输出...")
    
    if args.format == 'jsonl':
        formatter = JSONLFormatter()
        output_file = project_dir / f"{Path(folder_path).name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        formatter.save(contents, output_file, stats, Path(folder_path).name)
    else:
        formatter = JSONFormatter(config)
        description = None if args.no_desc else generate_description(Path(folder_path).name, stats, is_folder=True)
        
        result = formatter.format(
            files=files,
            contents=contents,
            stats=stats,
            root_path=str(folder_path),
            description=description
        )
        
        output_file = project_dir / f"{Path(folder_path).name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    # 生成摘要
    summary_file = project_dir / "summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"项目: {Path(folder_path).name}\n")
        f.write(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"文件数: {stats['total_files']}\n")
        f.write(f"总大小: {stats['total_size_human']}\n")
        f.write(f"成功读取: {stats.get('success_count', 0)}\n")
        f.write(f"读取失败: {stats.get('failed_count', 0)}\n")
        f.write(f"输出文件: {output_file.name}\n")
    
    print(f"\n✨ 处理完成!")
    print(f"   输出: {output_file}")
    print(f"   摘要: {summary_file}")
    
    return stats


def process_file(file_path, args):
    """处理单个文件（新增 FileReader 功能）"""
    print(f"📄 处理模式: 单个文件")
    print(f"   路径: {file_path}")
    
    # 配置
    config = {
        'max_lines': args.max_lines or 500,
        'extract_tables': args.extract_tables,
        'use_ocr': True,  # 启用 OCR
        'ocr_lang': 'chi_sim+eng',
        'tesseract_cmd': args.tesseract_cmd  # 从命令行参数获取
    }
    
    # 输出路径
    output_dir, filename = get_output_path(file_path, args.output)
    output_file = output_dir / f"{filename}.json"
    
    # 读取文件
    print(f"\n⏳ 读取文件...")
    reader = DocumentReader(config)
    content_info = reader.read_single(file_path)
    
    # 准备统计 - 修复这里
    file_stat = Path(file_path).stat()
    file_size_human = _format_size(file_stat.st_size)
    
    stats = {
        'file_name': Path(file_path).name,
        'file_type': Path(file_path).suffix.lower(),
        'file_size_bytes': file_stat.st_size,
        'file_size_human': file_size_human,  # 直接使用变量
        'success': content_info.get('content') is not None,
        'metadata': content_info.get('metadata', {})
    }
    
    # 生成输出
    print(f"\n⏳ 生成输出...")
    
    if args.format == 'jsonl':
        # JSONL 格式
        formatter = JSONLFormatter()
        contents = {str(file_path): content_info}
        output_file = output_dir / f"{filename}.jsonl"
        formatter.save(contents, output_file, stats, Path(file_path).name)
    else:
        # JSON 格式
        description = None if args.no_desc else generate_description(Path(file_path).name, stats, is_folder=False)
        
        result = {
            "metadata": {
                "file_name": Path(file_path).name,
                "file_path": str(file_path),
                "file_type": Path(file_path).suffix.lower(),
                "file_size": stats['file_size_human'],
                "processed_at": datetime.now().isoformat(),
                "ai_description": description
            },
            "content": content_info.get('content', ''),
            "metadata_extracted": content_info.get('metadata', {})
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✨ 处理完成!")
    print(f"   输出: {output_file}")
    
    return stats


def _format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def main():
    parser = argparse.ArgumentParser(
        description="Doc2AI - 智能文档/文件夹分析工具",
        usage="doc2ai <path> [options]"
    )
    parser.add_argument("path", help="要处理的文件夹路径或文件路径")
    parser.add_argument("-o", "--output", help="输出目录（默认: ./data）")
    parser.add_argument("--format", choices=['json', 'jsonl'], default='json',
                        help="输出格式: json 或 jsonl（默认: json）")
    parser.add_argument("--compact", action="store_true", help="紧凑格式输出（仅 JSON 格式）")
    parser.add_argument("--max-lines", type=int, help="每个文件最大行数（默认: 500）")
    parser.add_argument("--no-desc", action="store_true", help="不添加 AI 描述")
    parser.add_argument("--extract-tables", action="store_true", 
                        help="提取文档中的表格（DOCX/PDF）")
    parser.add_argument("--use-ocr", action="store_true", default=True,
                        help="启用 OCR 识别图片文字（默认: 启用）")
    parser.add_argument("--no-ocr", action="store_false", dest="use_ocr",
                        help="禁用 OCR 识别")
    parser.add_argument("--tesseract-cmd", help="Tesseract 可执行文件路径")
    parser.add_argument("--tessdata-dir", help="Tesseract tessdata 目录路径")
    
    args = parser.parse_args()
    # ... 其余代码保持不变
    
    # 检查路径是否存在
    input_path = Path(args.path)
    if not input_path.exists():
        print(f"❌ 错误：路径不存在 - {args.path}")
        sys.exit(1)
    
    print("=" * 50)
    print("Doc2AI - 智能文档分析工具")
    print("=" * 50)
    
    try:
        # 智能判断：文件夹 or 文件
        if input_path.is_dir():
            stats = process_folder(input_path, args)
        else:
            stats = process_file(input_path, args)
        
        # 显示统计
        print(f"\n📊 统计信息:")
        if input_path.is_dir():
            print(f"   文件总数: {stats.get('total_files', 0)}")
            print(f"   总大小: {stats.get('total_size_human', '0')}")
            print(f"   成功读取: {stats.get('success_count', 0)}")
            print(f"   读取失败: {stats.get('failed_count', 0)}")
        else:
            print(f"   文件大小: {stats.get('file_size_human', '0')}")
            print(f"   读取成功: {'✅ 是' if stats.get('success') else '❌ 否'}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()