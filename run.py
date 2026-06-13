# -*- coding: utf-8 -*-
"""项目入口 — 在项目根目录执行 python run.py"""
import sys
import os

# 将 src/ 加入搜索路径，确保内部模块互引用正常
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import main  # noqa: E402
