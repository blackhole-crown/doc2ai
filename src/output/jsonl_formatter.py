"""JSONL 格式输出器"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class JSONLFormatter:
    """JSONL 格式输出器"""
    
    def __init__(self):
        self.processed_files = set()
    
    def save(self, contents: Dict, output_file: Path, stats: Dict, project_name: str):
        """保存为 JSONL 格式"""
        output_file = Path(output_file)
        
        # 确保目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for file_path, content_info in contents.items():
                if content_info.get('content'):
                    record = {
                        'id': len(self.processed_files) + 1,
                        'description': content_info['content'],
                        'source_file': Path(file_path).name,
                        'file_path': file_path,
                        'file_type': Path(file_path).suffix.lower(),
                        'process_time': datetime.now().isoformat(),
                        'project': project_name,
                        **content_info.get('metadata', {})
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
                    self.processed_files.add(file_path)
        
        return output_file
    
    def save_summary(self, stats: Dict, summary_file: Path):
        """保存摘要文件"""
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"项目处理摘要\n")
            f.write(f"=" * 50 + "\n")
            f.write(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"文件总数: {stats.get('total_files', 0)}\n")
            f.write(f"总大小: {stats.get('total_size_human', '0')}\n")
            f.write(f"成功读取: {stats.get('success_count', 0)}\n")
            f.write(f"读取失败: {stats.get('failed_count', 0)}\n")
            
            if stats.get('file_types'):
                f.write(f"\n文件类型分布:\n")
                for ext, count in stats['file_types'].items():
                    f.write(f"  {ext or '无扩展名'}: {count} 个\n")