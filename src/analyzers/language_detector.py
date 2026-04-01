# src/analyzers/language_detector.py
from pathlib import Path
from typing import Dict, Optional


class LanguageDetector:
    """编程语言检测器"""
    
    # 扩展名到语言的映射
    EXTENSION_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'jsx',
        '.tsx': 'tsx',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sql': 'sql',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'bash',
        '.ps1': 'powershell',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.txt': 'text',
        '.log': 'text',
        '.ini': 'ini',
        '.conf': 'ini',
        '.toml': 'toml',
        '.dockerfile': 'dockerfile',
        '.gitignore': 'gitignore',
        '.env': 'dotenv'
    }
    
    def detect(self, file_path: str, content: str = "") -> str:
        """检测文件语言"""
        path = Path(file_path)
        
        # 检查扩展名
        ext = path.suffix.lower()
        if ext in self.EXTENSION_MAP:
            return self.EXTENSION_MAP[ext]
        
        # 检查文件名（无扩展名的文件）
        name = path.name.lower()
        if name in self.EXTENSION_MAP:
            return self.EXTENSION_MAP[name]
        
        # 简单的内容检测
        if content and content.strip():
            if content.strip().startswith('<?xml'):
                return 'xml'
            if content.strip().startswith('{') or content.strip().startswith('['):
                return 'json'
        
        return 'unknown'