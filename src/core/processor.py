import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .folder_scanner import FolderScanner, FileInfo
from .file_processor import FileProcessor
from .content_merger import ContentMerger
from ..analyzers.language_detector import LanguageDetector


class FolderProcessor:
    """文件夹处理器 - 主控制类"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.scanner = FolderScanner(config.get("processing", {}))
        self.file_processor = FileProcessor(config.get("analysis", {}))
        self.merger = ContentMerger(config)
        self.language_detector = LanguageDetector()
        
        self.progress_callback = None
    
    def process(self, 
                folder_path: str, 
                progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """处理文件夹（同步版本）"""
        self.progress_callback = progress_callback
        
        # 1. 扫描文件夹
        self._update_progress(10, "Scanning folder...")
        files = self.scanner.scan(Path(folder_path))
        statistics = self.scanner.get_statistics()
        
        if not files:
            return {
                "error": "No files found or all files were excluded",
                "statistics": statistics,
                "skipped_files": self.scanner.skipped_files
            }
        
        # 2. 处理每个文件
        self._update_progress(30, f"Processing {len(files)} files...")
        file_contents = self._process_files(files)
        
        # 3. 语言检测和分析
        self._update_progress(80, "Analyzing files...")
        file_contents = self._analyze_files(file_contents)
        
        # 4. 合并结果
        self._update_progress(90, "Merging results...")
        result = self.merger.merge_to_json(
            files=files,
            file_contents=file_contents,
            statistics=statistics,
            errors=self.scanner.skipped_files,
            root_path=folder_path
        )
        
        self._update_progress(100, "Complete!")
        
        return result
    
    def _process_files(self, files: List[FileInfo]) -> Dict[str, Any]:
        """处理所有文件"""
        results = {}
        total = len(files)
        
        for i, file_info in enumerate(files):
            try:
                # 更新进度
                if i % 10 == 0:
                    progress = 30 + int(50 * i / total)
                    self._update_progress(progress, f"Processing {file_info.name}")
                
                # 处理文件
                processed = self.file_processor.process_file(
                    file_info.absolute_path,
                    {"path": file_info.path}
                )
                results[file_info.path] = processed
                
            except Exception as e:
                results[file_info.path] = {
                    "error": str(e),
                    "content": {"raw": f"[Error: {str(e)}]"}
                }
        
        return results
    
    def _analyze_files(self, file_contents: Dict[str, Any]) -> Dict[str, Any]:
        """分析文件内容"""
        for path, content in file_contents.items():
            raw_content = content.get("content", {}).get("raw", "")
            if raw_content and not content.get("error"):
                # 语言检测
                language = self.language_detector.detect(path, raw_content)
                content["language"] = language
        
        return file_contents
    
    def _update_progress(self, percentage: int, message: str):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(percentage, message)
    
    async def process_async(self, folder_path: str) -> Dict[str, Any]:
        """异步处理文件夹"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process, folder_path)