#!/usr/bin/env python3
"""
启动 Folder2Context Web 服务
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 启动 Web 服务
from web.app import app

if __name__ == '__main__':
    print("=" * 50)
    print("Folder2Context Web 服务启动")
    print("=" * 50)
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)