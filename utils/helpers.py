"""
Utility functions for PDF Bookmark Generator
"""

import os
import json
import tempfile
from typing import Optional, List, Dict, Any


def save_json_file(file_path: str, data: Dict[Any, Any]) -> bool:
    """
    Save data to a JSON file
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存文件失败: {e}")
        return False


def load_json_file(file_path: str) -> Optional[Dict[Any, Any]]:
    """
    Load data from a JSON file
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载文件失败: {e}")
    return None


def get_temp_dir() -> str:
    """
    Get the system temporary directory
    """
    return tempfile.gettempdir()


def escape_html(text: str) -> str:
    """
    Escape HTML special characters
    """
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#x27;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "".join(html_escape_table.get(c, c) for c in text)