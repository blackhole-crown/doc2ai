import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent / "default_config.yaml"
        self.config = self._load_config()
        self._apply_env_overrides()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _apply_env_overrides(self):
        """应用环境变量覆盖"""
        # 支持通过环境变量覆盖配置
        if os.getenv("APP_DEBUG"):
            self.config["app"]["debug"] = os.getenv("APP_DEBUG").lower() == "true"
        if os.getenv("APP_HOST"):
            self.config["app"]["host"] = os.getenv("APP_HOST")
        if os.getenv("APP_PORT"):
            self.config["app"]["port"] = int(os.getenv("APP_PORT"))
        if os.getenv("MAX_FILE_SIZE_MB"):
            self.config["processing"]["max_file_size_mb"] = int(os.getenv("MAX_FILE_SIZE_MB"))
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的键"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def update(self, updates: Dict[str, Any]):
        """批量更新配置"""
        for key, value in updates.items():
            self.set(key, value)
    
    def reload(self):
        """重新加载配置"""
        self.config = self._load_config()
        self._apply_env_overrides()
    
    def get_processing_config(self) -> Dict[str, Any]:
        """获取处理相关配置"""
        return self.config.get("processing", {})
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """获取分析相关配置"""
        return self.config.get("analysis", {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """获取输出相关配置"""
        return self.config.get("output", {})