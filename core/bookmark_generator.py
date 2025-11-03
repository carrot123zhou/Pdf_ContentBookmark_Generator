"""
PDF Bookmark Generator Core Class
Handles bookmark parsing, management, and PDF generation
"""

import os
import json
import tempfile
from collections import deque
from typing import Optional, List, Dict, Any
import re

try:
    import PyPDF2
    PY_PDF2_AVAILABLE = True
except ImportError:
    PY_PDF2_AVAILABLE = False
    PyPDF2 = None  # type: ignore
    print("警告: PyPDF2库未安装，将无法生成书签")

try:
    from pdf2image import convert_from_path
    PDF_TO_IMAGE_AVAILABLE = True
except ImportError:
    PDF_TO_IMAGE_AVAILABLE = False
    convert_from_path = None
    print("提示: pdf2image库未安装，将无法提取目录页为图片")


class PDFBookmarkGenerator:
    def __init__(self):
        self.uploaded_file: Optional[str] = None
        self.bookmarks: List[Dict[str, Any]] = []
        self.original_bookmarks: List[Dict[str, Any]] = []
        self.offset = 0
        self.toc_start_page = 1
        self.toc_end_page = 1
        self.content_start_page = 1
        self.output_filename = ""
        self.original_filename = ""
        # 用于撤销操作的历史记录
        self.history = deque(maxlen=5)
        # 草稿文件路径
        self.draft_file = os.path.join(tempfile.gettempdir(), "pdf_bookmark_draft.json")
        # 自动加载草稿
        self.load_draft()

    def save_draft(self):
        """保存当前状态为草稿"""
        try:
            draft_data = {
                'bookmarks': self.bookmarks,
                'original_bookmarks': self.original_bookmarks,
                'offset': self.offset,
                'toc_start_page': self.toc_start_page,
                'toc_end_page': self.toc_end_page,
                'content_start_page': self.content_start_page,
                'output_filename': self.output_filename,
                'original_filename': self.original_filename
            }
            with open(self.draft_file, 'w', encoding='utf-8') as f:
                json.dump(draft_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存草稿失败: {e}")

    def load_draft(self):
        """加载草稿"""
        try:
            if os.path.exists(self.draft_file):
                with open(self.draft_file, 'r', encoding='utf-8') as f:
                    draft_data = json.load(f)

                self.bookmarks = draft_data.get('bookmarks', [])
                self.original_bookmarks = draft_data.get('original_bookmarks', [])
                self.offset = draft_data.get('offset', 0)
                self.toc_start_page = draft_data.get('toc_start_page', 1)
                self.toc_end_page = draft_data.get('toc_end_page', 1)
                self.content_start_page = draft_data.get('content_start_page', 1)
                self.output_filename = draft_data.get('output_filename', "")
                self.original_filename = draft_data.get('original_filename', "")
                print("草稿加载成功")
        except Exception as e:
            print(f"加载草稿失败: {e}")

    def clear_draft(self):
        """清除草稿"""
        try:
            if os.path.exists(self.draft_file):
                os.remove(self.draft_file)
        except Exception as e:
            print(f"清除草稿失败: {e}")

    def save_state(self):
        """保存当前状态用于撤销操作"""
        state = {
            'bookmarks': [bookmark.copy() for bookmark in self.bookmarks],
            'original_bookmarks': [bookmark.copy() for bookmark in self.original_bookmarks],
            'offset': self.offset
        }
        self.history.append(state)

    def undo(self):
        """撤销操作"""
        if len(self.history) > 1:
            # 移除当前状态
            self.history.pop()
            # 恢复到上一个状态
            prev_state = self.history[-1]
            self.bookmarks = [bookmark.copy() for bookmark in prev_state['bookmarks']]
            self.original_bookmarks = [bookmark.copy() for bookmark in prev_state['original_bookmarks']]
            self.offset = prev_state['offset']
            self.save_draft()
            return True
        return False

    def parse_toc_text(self, toc_text: str) -> List[Dict[str, Any]]:
        """
        解析目录文本，提取标题和页码信息
        """
        self.save_state()
        bookmarks = []
        lines = toc_text.strip().split('\n')

        # 先收集所有Markdown层级信息，用于后续计算相对层级
        markdown_levels = set()
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查Markdown风格的标题标记
            markdown_match = re.match(r'^(#{1,4})\s+(.+)', line)
            if markdown_match:
                level = len(markdown_match.group(1))
                markdown_levels.add(level)

        # 创建层级映射，使最小的层级成为第0级
        sorted_levels = sorted(list(markdown_levels))
        level_mapping = {level: idx for idx, level in enumerate(sorted_levels)}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 保存原始行内容
            original_line = line

            # 移除行首的标记符号
            prefixes = ['#', '*', '-', '•', '★', '☆', '▶', '►', '→', '⇒']
            while any(line.startswith(prefix) for prefix in prefixes):
                for prefix in prefixes:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()
                        break

            # 尝试提取页码（数字在行尾）
            page_match = re.search(r'(\d+)(?:\s*)$', line)
            page_num = None
            title = line

            if page_match:
                page_num = int(page_match.group(1))
                title = line[:page_match.start()].strip()

            # 移除标题中的点线或其他分隔符
            title = re.sub(r'\.{3,}|\s{2,}$', '', title).strip()

            # 确定层级
            level = 0

            # 方法1: 检查缩进
            original_title_part = original_line
            # 移除行首符号
            for prefix in prefixes:
                if original_title_part.startswith(prefix):
                    original_title_part = original_title_part[len(prefix):].strip()
                    break
            # 检查缩进空格数
            leading_spaces = len(original_title_part) - len(original_title_part.lstrip())
            if leading_spaces > 0:
                level = min(3, leading_spaces // 2)

            # 方法2: 检查是否有层级编号（如1.1, 1.1.1等）
            chapter_match = re.search(r'^(\d+\.)*\d+', title)
            if chapter_match:
                dots = chapter_match.group(0).count('.')
                level = max(level, dots)

            # 方法3: 检查Markdown风格的标题标记
            markdown_match = re.match(r'^(#{1,4})\s+(.+)', original_line)
            if markdown_match:
                original_level = len(markdown_match.group(1))
                level = level_mapping.get(original_level, original_level - 1)
                title = markdown_match.group(2)

            # 方法4: 检查中文编号模式（如一、二、三等）
            chinese_numeral_match = re.search(r'^[一二三四五六七八九十百千万]+[、:]', title)
            if chinese_numeral_match:
                level = max(level, 0)

            # 方法5: 检查罗马数字模式（如I, II, III等）
            roman_numeral_match = re.search(r'^[IVXLCDM]+[\.、:]', title)
            if roman_numeral_match:
                level = max(level, 0)

            # 方法6: 检查特殊关键词
            if any(keyword in title for keyword in ['前言', '序言', '附录', '参考文献', '索引']):
                level = max(level, 0)

            if any(keyword in title for keyword in ['章节', '章', '篇']):
                level = max(level, 0)

            if any(keyword in title for keyword in ['节', '项', '条']):
                level = min(level + 1, 3)

            if any(keyword in title for keyword in ['小节', '子项', '子条']):
                level = min(level + 2, 3)

            bookmarks.append({
                'title': title,
                'page': page_num,
                'level': level
            })

        # 保存原始书签（未应用偏移量）
        self.original_bookmarks = [bookmark.copy() for bookmark in bookmarks]
        self.save_draft()
        return bookmarks

    def calculate_offset(self, content_start_page: Optional[int] = None) -> int:
        """
        根据正文起始页计算页码偏移量
        公式: 偏移量 = 正文起始PDF页码 - 1
        """
        if content_start_page is not None and content_start_page > 0:
            return content_start_page - 1
        elif self.content_start_page is not None and self.content_start_page > 0:
            return self.content_start_page - 1
        return 0

    def apply_offset(self, bookmarks: List[Dict[str, Any]], offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        将偏移量应用到书签页码
        """
        if offset is None:
            offset = self.offset

        # 应用偏移量到书签页码
        result_bookmarks = []
        for bookmark in bookmarks:
            new_bookmark = bookmark.copy()
            if new_bookmark['page'] is not None:
                new_bookmark['page'] = new_bookmark['page'] + offset
            result_bookmarks.append(new_bookmark)

        return result_bookmarks

    def add_bookmark(self, title: str, page: Optional[int], level: int = 0) -> None:
        """
        添加单个书签
        """
        self.save_state()
        self.bookmarks.append({
            'title': title,
            'page': page,
            'level': level
        })
        # 同时更新原始书签
        self.original_bookmarks.append({
            'title': title,
            'page': page,
            'level': level
        })
        self.save_draft()

    def remove_bookmark(self, index: int) -> None:
        """
        删除指定索引的书签
        """
        if 0 <= index < len(self.bookmarks):
            self.save_state()
            del self.bookmarks[index]
            # 同时删除原始书签
            del self.original_bookmarks[index]
            self.save_draft()

    def update_bookmark(self, index: int, title: Optional[str] = None,
                       page: Optional[int] = None, level: Optional[int] = None) -> None:
        """
        更新指定索引的书签
        """
        if 0 <= index < len(self.bookmarks):
            self.save_state()
            if title is not None:
                self.bookmarks[index]['title'] = title
                self.original_bookmarks[index]['title'] = title
            if page is not None:
                self.bookmarks[index]['page'] = page
                self.original_bookmarks[index]['page'] = page
            if level is not None:
                self.bookmarks[index]['level'] = level
                self.original_bookmarks[index]['level'] = level
            self.save_draft()

    def move_bookmark(self, index: int, direction: str) -> None:
        """
        移动书签位置
        direction: 'up' 或 'down'
        """
        if 0 <= index < len(self.bookmarks):
            self.save_state()
            if direction == 'up' and index > 0:
                self.bookmarks[index], self.bookmarks[index-1] = self.bookmarks[index-1], self.bookmarks[index]
                self.original_bookmarks[index], self.original_bookmarks[index-1] = self.original_bookmarks[index-1], self.original_bookmarks[index]
            elif direction == 'down' and index < len(self.bookmarks) - 1:
                self.bookmarks[index], self.bookmarks[index+1] = self.bookmarks[index+1], self.bookmarks[index]
                self.original_bookmarks[index], self.original_bookmarks[index+1] = self.original_bookmarks[index+1], self.original_bookmarks[index]
            self.save_draft()

    def extract_toc_pages(self, start_page: Optional[int] = None,
                         end_page: Optional[int] = None) -> Optional[str]:
        """
        提取目录页为图片
        """
        if not PDF_TO_IMAGE_AVAILABLE:
            return None

        if not self.uploaded_file:
            return None

        if start_page is None:
            start_page = self.toc_start_page

        if end_page is None:
            end_page = self.toc_end_page

        try:
            # 转换PDF页面为图片
            images = []
            if PDF_TO_IMAGE_AVAILABLE and convert_from_path is not None:
                images = convert_from_path(
                    self.uploaded_file,
                    first_page=start_page or self.toc_start_page,
                    last_page=end_page or self.toc_end_page
                )

            if images:
                # 保存图片到临时目录
                temp_dir = tempfile.gettempdir()

                # 如果只有一页，直接保存
                if len(images) == 1:
                    image_path = os.path.join(temp_dir, "toc_page.png")
                    images[0].save(image_path, 'PNG')
                    return image_path
                else:
                    # 如果有多页，合并为一张图片
                    from PIL import Image
                    # 计算合并后的图像尺寸
                    widths, heights = zip(*(i.size for i in images))
                    total_height = sum(heights)
                    max_width = max(widths)

                    # 创建新的图像
                    new_image = Image.new('RGB', (max_width, total_height), (255, 255, 255))

                    # 粘贴每张图片
                    y_offset = 0
                    for img in images:
                        new_image.paste(img, (0, y_offset))
                        y_offset += img.size[1]

                    # 保存合并后的图像
                    image_path = os.path.join(temp_dir, "toc_pages.png")
                    new_image.save(image_path, 'PNG')
                    return image_path
        except Exception as e:
            print(f"提取目录页时出错: {e}")

        return None

    def export_bookmarks(self, file_path: str) -> bool:
        """
        导出书签到文件
        """
        try:
            export_data = {
                'bookmarks': self.bookmarks,
                'original_bookmarks': self.original_bookmarks,
                'offset': self.offset
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出书签失败: {e}")
            return False

    def import_bookmarks(self, file_path: str) -> bool:
        """
        从文件导入书签
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            self.save_state()
            self.bookmarks = import_data.get('bookmarks', [])
            self.original_bookmarks = import_data.get('original_bookmarks', [])
            self.offset = import_data.get('offset', 0)
            self.save_draft()
            return True
        except Exception as e:
            print(f"导入书签失败: {e}")
            return False

    def search_bookmarks(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索书签
        """
        results = []
        for i, bookmark in enumerate(self.bookmarks):
            if keyword.lower() in bookmark['title'].lower():
                results.append({
                    'index': i,
                    'bookmark': bookmark
                })
        return results

    def filter_bookmarks_by_level(self, level: int) -> List[Dict[str, Any]]:
        """
        根据层级过滤书签
        """
        results = []
        for i, bookmark in enumerate(self.bookmarks):
            if bookmark['level'] == level:
                results.append({
                    'index': i,
                    'bookmark': bookmark
                })
        return results

    def batch_update_bookmarks(self, indices: List[int], title_prefix: Optional[str] = None,
                              page_offset: Optional[int] = None, level_offset: Optional[int] = None) -> None:
        """
        批量更新书签
        """
        self.save_state()
        for index in indices:
            if 0 <= index < len(self.bookmarks):
                if title_prefix is not None:
                    self.bookmarks[index]['title'] = title_prefix + self.bookmarks[index]['title']
                    self.original_bookmarks[index]['title'] = title_prefix + self.original_bookmarks[index]['title']
                if page_offset is not None:
                    if self.bookmarks[index]['page'] is not None:
                        self.bookmarks[index]['page'] += page_offset
                    if self.original_bookmarks[index]['page'] is not None:
                        self.original_bookmarks[index]['page'] += page_offset
                if level_offset is not None:
                    new_level = self.bookmarks[index]['level'] + level_offset
                    self.bookmarks[index]['level'] = max(0, min(3, new_level))
                    self.original_bookmarks[index]['level'] = max(0, min(3, new_level))
        self.save_draft()

    def generate_pdf_with_bookmarks(self, output_path: Optional[str] = None) -> bool:
        """
        生成带书签的PDF文件
        """
        if not PY_PDF2_AVAILABLE:
            print("错误: 需要安装PyPDF2库才能生成带书签的PDF")
            return False

        if not self.uploaded_file:
            print("错误: 未上传PDF文件")
            return False

        if not self.bookmarks:
            print("错误: 没有书签数据")
            return False

        try:
            # 读取原始PDF
            with open(self.uploaded_file, 'rb') as infile:
                if PyPDF2 is None:
                    raise RuntimeError("PyPDF2库未安装，无法生成PDF")
                    
                reader = PyPDF2.PdfReader(infile)
                writer = PyPDF2.PdfWriter()

                # 复制所有页面
                for page in reader.pages:
                    writer.add_page(page)

                # 添加书签
                bookmark_map = {}
                bookmarks_added = 0

                for i, bookmark in enumerate(self.bookmarks):
                    title = bookmark['title']
                    page_num = bookmark['page']
                    level = bookmark['level']

                    # 修复页码索引问题：用户输入的是1基索引，PDF内部使用0基索引
                    # 修正：用户输入的页码已经是应用偏移量后的结果，应直接减1转换为0基索引
                    # 修复问题：确保页码不小于1，并且不超过PDF总页数
                    if page_num is not None and 1 <= page_num <= len(reader.pages):
                        try:
                            # 根据层级添加书签
                            if level == 0:
                                # 顶级书签
                                parent = writer.add_outline_item(title, page_num-1)
                                bookmark_map[i] = parent
                                bookmarks_added += 1
                            elif level > 0:
                                # 子书签（正确处理层级嵌套）
                                # 找到最近的、层级比当前层级低的父书签
                                parent_key = None
                                for key in reversed(list(bookmark_map.keys())):
                                    if key < i and self.bookmarks[key]['level'] < level:
                                        parent_key = key
                                        break

                                if parent_key is not None:
                                    parent = bookmark_map[parent_key]
                                    child = writer.add_outline_item(title, page_num-1, parent=parent)
                                    bookmark_map[i] = child
                                    bookmarks_added += 1
                                else:
                                    # 如果没有找到合适的父书签，则作为顶级书签添加
                                    parent = writer.add_outline_item(title, page_num-1)
                                    bookmark_map[i] = parent
                                    bookmarks_added += 1
                        except Exception as e:
                            print(f"添加书签 '{title}' 时出错: {e}")
                    else:
                        print(f"警告: 书签 '{title}' 的页码 {page_num} 超出范围 (1-{len(reader.pages)})")

                print(f"成功添加 {bookmarks_added} 个书签")

                # 写入输出文件
                if output_path is None:
                    # 默认输出路径
                    output_dir = os.path.join(os.path.expanduser("~"), "Documents", "pdf编目")
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, self.output_filename)

                with open(output_path, 'wb') as outfile:
                    writer.write(outfile)

                print(f"成功生成带书签的PDF文件: {output_path}")
                # 清除草稿
                self.clear_draft()
                return True

        except Exception as e:
            print(f"生成PDF时出错: {e}")
            return False

        return False