"""
UI Components for PDF Bookmark Generator
Contains HTML, CSS, and JavaScript for the web interface
"""

def get_html_content():
    return '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF书签生成器</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { color: #333; }
        .section { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea, select { width: 100%; padding: 8px; margin-bottom: 15px; box-sizing: border-box; }
        button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px; margin-bottom: 10px; }
        button:hover { background-color: #45a049; }
        .btn-danger { background-color: #f44336; }
        .btn-danger:hover { background-color: #da190b; }
        .btn-secondary { background-color: #008CBA; }
        .btn-secondary:hover { background-color: #007B9A; }
        .btn-warning { background-color: #ff9800; }
        .btn-warning:hover { background-color: #e68a00; }
        .btn-info { background-color: #17a2b8; }
        .btn-info:hover { background-color: #138496; }
        .btn-primary { background-color: #007bff; }
        .btn-primary:hover { background-color: #0069d9; }
        .btn-dark { background-color: #343a40; }
        .btn-dark:hover { background-color: #23272b; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .toc-image-container { 
            max-height: 400px; 
            overflow-y: auto; 
            border: 1px solid #ccc; 
            padding: 10px; 
            margin-top: 15px;
            text-align: center;
        }
        .toc-image { max-width: 100%; }
        .actions { margin: 10px 0; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .status-success { background-color: #dff0d8; color: #3c763d; }
        .status-error { background-color: #f2dede; color: #a94442; }
        .status-info { background-color: #d9edf7; color: #31708f; }
        .hidden { display: none; }
        .offset-display { 
            background-color: #e9ecef; 
            padding: 10px; 
            border-radius: 4px; 
            margin-bottom: 15px; 
            font-weight: bold;
        }
        .bookmark-row {
            cursor: move;
        }
        .bookmark-row.dragging {
            opacity: 0.5;
            background-color: #f0f0f0;
        }
        .level-select {
            width: auto;
            min-width: 80px;
            padding: 4px;
        }
        .page-input {
            width: 80px;
        }
        .title-input {
            width: 100%;
        }
        .preview-section {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }
        .bookmarks-container {
            max-height: 500px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
        }
        .page-info {
            font-size: 0.9em;
            color: #666;
        }
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px;
            border-radius: 4px;
            color: white;
            z-index: 1000;
            opacity: 0.9;
            transition: opacity 0.3s;
        }
        .notification-success {
            background-color: #28a745;
        }
        .notification-error {
            background-color: #dc3545;
        }
        .notification-info {
            background-color: #17a2b8;
        }
        .batch-edit-section {
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            border: 1px solid #ffeaa7;
        }
        .draft-indicator {
            background-color: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PDF书签生成器 Beta</h1>
        <div class="draft-indicator" id="draftIndicator">
            检测到草稿文件，已自动加载上次的工作进度
        </div>
        <div class="page-info">
            <p><strong>页码说明：</strong>用户输入的页码为PDF显示页码（1基索引），系统会自动转换为PDF内部索引（0基索引）</p>
        </div>
        
        <!-- 文件上传部分 -->
        <div class="section">
            <h2>1. 上传PDF文件</h2>
            <form id="uploadForm" enctype="multipart/form-data">
                <label for="pdfFile">选择PDF文件:</label>
                <input type="file" id="pdfFile" name="pdfFile" accept=".pdf" required>
                <button type="submit">上传PDF</button>
                <button type="button" id="deleteFileBtn" class="btn-danger hidden" onclick="deleteUploadedFile()">删除已上传文件</button>
            </form>
            <div id="uploadStatus"></div>
        </div>
        
        <!-- 目录页提取部分 -->
        <div class="section">
            <h2>2. 提取目录页（可选）</h2>
            <label for="tocStartPage">目录起始页:</label>
            <input type="number" id="tocStartPage" min="1" value="1">
            
            <label for="tocEndPage">目录结束页:</label>
            <input type="number" id="tocEndPage" min="1" value="1">
            
            <button onclick="updateTocPages()" class="btn-warning">更新目录页范围</button>
            <button onclick="extractTocPages()">提取目录页</button>
            <button onclick="openQwen()" class="btn-info">使用通义千问识别目录</button>
            <div>
                <div style="display: flex; align-items: center;">
                    <div style="flex-grow: 1;">
                        <div style="font-weight: bold;">推荐提示词：</div>
                        <div id="promptContainer" style="max-height: 100px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9;">
请分析这个PDF文档的目录页，并按照以下要求输出目录结构：<br><br>

1. 保留完整的层级结构信息，使用缩进或编号方式表示层级关系<br>
2. 每行输出一个目录项，格式为："标题内容 ...................... 页码"（页码前的点线为可选）<br>
3. 对于缺失页码的条目，请根据上下文逻辑推断并补充完整页码<br>
4. 支持多种标题格式：<br>
&nbsp;&nbsp;&nbsp;- 章节编号格式：如"第1章 绪论"、"1.1 背景介绍"<br>
&nbsp;&nbsp;&nbsp;- Markdown格式：使用#符号表示层级<br>
&nbsp;&nbsp;&nbsp;- 缩进格式：通过空格或制表符表示层级<br>
&nbsp;&nbsp;&nbsp;- 中文序数格式：如"一、"、"1."、"（一）"等<br>
5. 保持原始层级结构，不要改变标题内容<br>
6. 输出时不要包含任何解释性文字，只输出目录内容本身<br><br>

示例输出格式：<br>
# 第一章 绪论 1<br>
## 1.1 研究背景 1<br>
## 1.2 研究意义 3<br>
# 第二章 文献综述 5<br>
## 2.1 国内研究现状 5<br>
## 2.2 国外研究现状 8<br>
                        </div>
                    </div>
                    <div style="margin-left: 10px;">
                        <button onclick="copyPrompt()" class="btn-secondary">复制提示词</button>
                    </div>
                </div>
            </div>
            <div id="tocImageContainer"></div>
        </div>
        
        <!-- 目录输入部分 -->
        <div class="section">
            <h2>3. 输入目录文本</h2>
            <label for="tocText">粘贴目录内容:</label>
            <textarea id="tocText" rows="10" placeholder="在此粘贴目录内容&#10;支持格式示例:&#10;章节1 标题 ...................... 1&#10;2 第二章 标题&#10;# 第一章 标题 5&#10;* 第一节 标题 10&#10;## 1.1 第一节标题 10"></textarea>
            <button onclick="parseTocText()">解析目录</button>
            <button onclick="previewParseResult()" class="btn-info">预览解析结果</button>
            <div id="parseStatus"></div>
            <div id="parsePreview" class="preview-section" style="display: none;"></div>
        </div>
        
        <!-- 参数设置部分 -->
        <div class="section">
            <h2>4. 设置参数</h2>
            <div class="offset-display">
                <strong>当前使用的偏移量:</strong> <span id="currentOffset">0</span>
            </div>
            
            <label for="contentStartPage">正文起始页:</label>
            <input type="number" id="contentStartPage" min="1" value="1">
            
            <button onclick="calculateAndApplyOffset()">计算并应用偏移量</button>
            
            <label for="manualOffset">手动设置偏移量:</label>
            <input type="number" id="manualOffset" value="0">
            <button onclick="applyManualOffset()">应用手动偏移量</button>
            
            <div class="preview-section">
                <h3>偏移量预览</h3>
                <p>应用偏移量后，将更新书签编辑器中的PDF页码列（实际页码 = 原始页码 + 偏移量）</p>
                <button onclick="previewOffsetChanges()">预览偏移量变化</button>
                <div id="offsetPreview"></div>
            </div>
            
            <label for="outputFileName">输出文件名:</label>
            <input type="text" id="outputFileName" value="">
        </div>
        
        <!-- 书签编辑部分 -->
        <div class="section">
            <h2>5. 编辑书签</h2>
            <div class="actions">
                <button onclick="addBookmarkBeforeSelected()">在选中行前添加书签</button>
                <button onclick="addBookmark()">添加书签到末尾</button>
                <button onclick="saveBookmarks()">保存修改</button>
                <button class="btn-danger" onclick="deleteSelectedBookmarks()">删除选中书签</button>
                <button class="btn-warning" onclick="moveSelectedUp()">上移</button>
                <button class="btn-warning" onclick="moveSelectedDown()">下移</button>
                <button onclick="invertSelection()">反选</button>
            </div>
            <div class="bookmarks-container">
                <table id="bookmarksTable">
                    <thead>
                        <tr>
                            <th><input type="checkbox" id="selectAll" onchange="toggleSelectAll()"></th>
                            <th>层级</th>
                            <th>标题</th>
                            <th>原始页码</th>
                            <th>PDF页码</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="bookmarksTableBody">
                        <!-- 书签将在这里动态生成 -->
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- 生成PDF部分 -->
        <div class="section">
            <h2>6. 生成PDF</h2>
            <button class="btn-secondary" onclick="generatePdf()">生成PDF</button>
            <button class="btn-danger" onclick="exitApplication()">退出程序</button>
            <div id="generationStatus"></div>
        </div>
    </div>

    <script>
        let draggedRow = null;
        
        // 解析目录文本
        function parseTocText() {
            const tocText = document.getElementById('tocText').value;
            fetch('/parse_toc', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({toc_text: tocText})
            })
            .then(response => response.json())
            .then(data => {
                const statusDiv = document.getElementById('parseStatus');
                if (data.status === 'success') {
                    renderBookmarks(data.bookmarks, data.original_bookmarks);
                    showNotification('目录解析成功，共识别到 ' + data.bookmarks.length + ' 个条目', 'success');
                    // 清空状态区域
                    statusDiv.innerHTML = '';
                    // 保存解析结果用于预览
                    window.lastParseResult = data;
                } else {
                    showNotification('解析失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showNotification('解析出错: ' + error, 'error');
            });
        }
        
        // 预览解析结果
        function previewParseResult() {
            if (!window.lastParseResult || window.lastParseResult.status !== 'success') {
                showNotification('请先解析目录', 'error');
                return;
            }
            
            const data = window.lastParseResult;
            const previewDiv = document.getElementById('parsePreview');
            
            let html = `
                <h3>目录解析结果报告</h3>
                <p><strong>解析状态:</strong> 成功</p>
                <p><strong>识别条目数:</strong> ${data.bookmarks.length} 个</p>
                
                <h4>详细信息:</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #f2f2f2;">
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">层级</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">标题</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">原始页码</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">PDF页码</th>
                        </tr>
                    </thead>
                    <tbody>`;
            
            data.bookmarks.forEach((bookmark, index) => {
                const originalPage = data.original_bookmarks[index] ? data.original_bookmarks[index].page : null;
                html += `
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">${bookmark.level}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">${escapeHtml(bookmark.title)}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">${originalPage || '无'}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">${bookmark.page || '无'}</td>
                    </tr>`;
            });
            
            html += `
                    </tbody>
                </table>
                <button onclick="this.parentElement.style.display='none'" class="btn-danger" style="margin-top: 10px;">关闭预览</button>
            `;
            
            previewDiv.innerHTML = html;
            previewDiv.style.display = 'block';
        }
        
        // 渲染书签表格
        function renderBookmarks(bookmarks, originalBookmarks = null) {
            const tbody = document.querySelector('#bookmarksTable tbody');
            tbody.innerHTML = '';
            
            // 如果没有提供原始书签，则使用当前书签作为原始书签
            if (!originalBookmarks) {
                originalBookmarks = bookmarks;
            }
            
            bookmarks.forEach((bookmark, index) => {
                const originalPage = originalBookmarks[index] ? originalBookmarks[index].page : null;
                const row = document.createElement('tr');
                row.className = 'bookmark-row';
                row.draggable = true;
                row.innerHTML = `
                    <td><input type="checkbox" class="bookmark-select" data-index="${index}"></td>
                    <td>
                        <select class="level-select" id="level_${index}" onchange="onLevelChange(this)">
                            <option value="0">级别0</option>
                            <option value="1">级别1</option>
                            <option value="2">级别2</option>
                            <option value="3">级别3</option>
                        </select>
                    </td>
                    <td><input type="text" class="title-input" id="title_${index}" value="${escapeHtml(bookmark.title)}"></td>
                    <td>${originalPage || ''}</td>
                    <td><input type="number" class="page-input" id="page_${index}" value="${bookmark.page || ''}"></td>
                    <td>
                        <button class="btn-danger" onclick="removeBookmark(this)">删除</button>
                    </td>
                `;
                
                // 添加拖拽事件
                row.addEventListener('dragstart', handleDragStart);
                row.addEventListener('dragover', handleDragOver);
                row.addEventListener('drop', handleDrop);
                row.addEventListener('dragend', handleDragEnd);
                
                tbody.appendChild(row);
            });
            
            // 在所有行添加完毕后再设置层级选择
            setTimeout(() => {
                bookmarks.forEach((bookmark, index) => {
                    // 设置层级选择
                    const levelSelect = document.getElementById(`level_${index}`);
                    if (levelSelect) {
                        levelSelect.value = bookmark.level;
                    }
                });
            }, 0);
            
            // 更新索引
            updateBookmarkIndices();
        }
        
        // 转义HTML特殊字符
        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, function(m) { return map[m]; });
        }
        
        // 层级选择变化事件
        function onLevelChange(selectElement) {
            // 获取当前行的索引
            const rowIndex = parseInt(selectElement.id.split('_')[1]);
            
            // 检查是否有其他选中的行
            const checkboxes = document.querySelectorAll('.bookmark-select:checked');
            if (checkboxes.length > 1) {
                // 如果有多个选中项，询问是否应用到所有选中项
                if (confirm(`是否将层级 ${selectElement.value} 应用到所有选中的 ${checkboxes.length} 个书签？`)) {
                    checkboxes.forEach(checkbox => {
                        const index = parseInt(checkbox.dataset.index);
                        const levelSelect = document.getElementById(`level_${index}`);
                        if (levelSelect && index !== rowIndex) {
                            levelSelect.value = selectElement.value;
                        }
                    });
                }
            }
        }
        
        // 拖拽开始
        function handleDragStart(e) {
            draggedRow = this;
            this.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/html', this.innerHTML);
        }
        
        // 拖拽经过
        function handleDragOver(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            
            const tbody = document.querySelector('#bookmarksTable tbody');
            const rows = Array.from(tbody.querySelectorAll('.bookmark-row'));
            const draggingRow = rows.find(row => row.classList.contains('dragging'));
            const targetRow = e.target.closest('.bookmark-row');
            
            if (targetRow && targetRow !== draggingRow) {
                const bounding = targetRow.getBoundingClientRect();
                const offset = bounding.y + (bounding.height / 2);
                
                if (e.clientY <= offset) {
                    tbody.insertBefore(draggingRow, targetRow);
                } else {
                    tbody.insertBefore(draggingRow, targetRow.nextSibling);
                }
            }
        }
        
        // 拖拽放下
        function handleDrop(e) {
            e.preventDefault();
            return false;
        }
        
        // 拖拽结束
        function handleDragEnd() {
            this.classList.remove('dragging');
            draggedRow = null;
            
            // 更新索引
            updateBookmarkIndices();
        }
        
        // 更新书签索引
        function updateBookmarkIndices() {
            const rows = document.querySelectorAll('#bookmarksTable tbody tr');
            rows.forEach((row, index) => {
                const checkbox = row.querySelector('.bookmark-select');
                const levelSelect = row.querySelector('select');
                const titleInput = row.querySelector('input[type="text"]');
                const pageInput = row.querySelector('input[type="number"]');
                
                if (checkbox) checkbox.dataset.index = index;
                if (levelSelect) levelSelect.id = `level_${index}`;
                if (titleInput) titleInput.id = `title_${index}`;
                if (pageInput) pageInput.id = `page_${index}`;
            });
        }
        
        // 添加书签到末尾
        function addBookmark() {
            const tbody = document.querySelector('#bookmarksTable tbody');
            const rowCount = tbody.children.length;
            
            const row = document.createElement('tr');
            row.className = 'bookmark-row';
            row.draggable = true;
            row.innerHTML = `
                <td><input type="checkbox" class="bookmark-select" data-index="${rowCount}"></td>
                <td>
                    <select class="level-select" id="level_${rowCount}" onchange="onLevelChange(this)">
                        <option value="0" selected>级别0</option>
                        <option value="1">级别1</option>
                        <option value="2">级别2</option>
                        <option value="3">级别3</option>
                    </select>
                </td>
                <td><input type="text" class="title-input" id="title_${rowCount}" value=""></td>
                <td></td>
                <td><input type="number" class="page-input" id="page_${rowCount}" value=""></td>
                <td>
                    <button class="btn-danger" onclick="removeBookmark(this)">删除</button>
                </td>
            `;
            
            // 添加拖拽事件
            row.addEventListener('dragstart', handleDragStart);
            row.addEventListener('dragover', handleDragOver);
            row.addEventListener('drop', handleDrop);
            row.addEventListener('dragend', handleDragEnd);
            
            tbody.appendChild(row);
            updateBookmarkIndices();
        }
        
        // 在选中行前添加书签
        function addBookmarkBeforeSelected() {
            const checkboxes = document.querySelectorAll('.bookmark-select:checked');
            
            if (checkboxes.length === 0) {
                // 没有选中行，添加到末尾
                addBookmark();
                return;
            }
            
            if (checkboxes.length > 1) {
                showNotification('请只选择一个位置来插入书签', 'error');
                return;
            }
            
            const selectedIndex = parseInt(checkboxes[0].dataset.index);
            const tbody = document.querySelector('#bookmarksTable tbody');
            
            const row = document.createElement('tr');
            row.className = 'bookmark-row';
            row.draggable = true;
            row.innerHTML = `
                <td><input type="checkbox" class="bookmark-select" data-index="${selectedIndex}"></td>
                <td>
                    <select class="level-select" id="level_${selectedIndex}" onchange="onLevelChange(this)">
                        <option value="0" selected>级别0</option>
                        <option value="1">级别1</option>
                        <option value="2">级别2</option>
                        <option value="3">级别3</option>
                    </select>
                </td>
                <td><input type="text" class="title-input" id="title_${selectedIndex}" value=""></td>
                <td></td>
                <td><input type="number" class="page-input" id="page_${selectedIndex}" value=""></td>
                <td>
                    <button class="btn-danger" onclick="removeBookmark(this)">删除</button>
                </td>
            `;
            
            // 添加拖拽事件
            row.addEventListener('dragstart', handleDragStart);
            row.addEventListener('dragover', handleDragOver);
            row.addEventListener('drop', handleDrop);
            row.addEventListener('dragend', handleDragEnd);
            
            // 插入到选中行之前
            const selectedRow = tbody.children[selectedIndex];
            tbody.insertBefore(row, selectedRow);
            updateBookmarkIndices();
        }
        
        // 删除书签
        function removeBookmark(button) {
            const row = button.closest('tr');
            if (row) {
                row.remove();
                updateBookmarkIndices();
            }
        }
        
        // 保存书签修改
        function saveBookmarks() {
            const rows = document.querySelectorAll('#bookmarksTable tbody tr');
            const bookmarks = [];
            
            rows.forEach((row, index) => {
                const level = document.getElementById(`level_${index}`).value;
                const title = document.getElementById(`title_${index}`).value;
                const page = document.getElementById(`page_${index}`).value;
                
                bookmarks.push({
                    level: parseInt(level),
                    title: title,
                    page: page ? parseInt(page) : null
                });
            });
            
            fetch('/save_bookmarks', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({bookmarks: bookmarks})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showNotification('书签保存成功', 'success');
                } else {
                    showNotification('保存失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showNotification('保存出错: ' + error, 'error');
            });
        }
        
        // 全选/取消全选
        function toggleSelectAll() {
            const selectAll = document.getElementById('selectAll');
            const checkboxes = document.querySelectorAll('.bookmark-select');
            
            checkboxes.forEach(checkbox => {
                checkbox.checked = selectAll.checked;
            });
        }
        
        // 反选
        function invertSelection() {
            const checkboxes = document.querySelectorAll('.bookmark-select');
            checkboxes.forEach(checkbox => {
                checkbox.checked = !checkbox.checked;
            });
            // 更新全选框状态
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            document.getElementById('selectAll').checked = allChecked;
        }
        
        // 删除选中的书签
        function deleteSelectedBookmarks() {
            const checkboxes = document.querySelectorAll('.bookmark-select:checked');
            if (checkboxes.length === 0) {
                showNotification('请先选择要删除的书签', 'error');
                return;
            }
            
            if (confirm(`确定要删除选中的 ${checkboxes.length} 个书签吗？`)) {
                // 从后往前删除，避免索引变化
                const indices = Array.from(checkboxes)
                    .map(cb => parseInt(cb.dataset.index))
                    .sort((a, b) => b - a);
                
                indices.forEach(index => {
                    removeBookmark(index);
                });
                
                // 重置全选按钮
                document.getElementById('selectAll').checked = false;
                showNotification(`已删除 ${checkboxes.length} 个书签`, 'success');
            }
        }
        
        // 上移选中的书签
        function moveSelectedUp() {
            const checkboxes = document.querySelectorAll('.bookmark-select:checked');
            if (checkboxes.length === 0) {
                showNotification('请先选择要移动的书签', 'error');
                return;
            }
            
            // 获取选中项的索引并排序
            const indices = Array.from(checkboxes)
                .map(cb => parseInt(cb.dataset.index))
                .sort((a, b) => a - b);
            
            // 检查是否可以移动（第一个不能移到-1位置）
            if (indices[0] === 0) {
                showNotification('已到顶部，无法继续上移', 'error');
                return;
            }
            
            // 发送到服务器进行移动
            fetch('/move_bookmark', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({indices: indices, direction: 'up'})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    renderBookmarks(data.bookmarks, data.original_bookmarks);
                    showNotification(`已上移 ${indices.length} 个书签`, 'success');
                } else {
                    showNotification('移动失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showNotification('移动出错: ' + error, 'error');
            });
        }
        
        // 下移选中的书签
        function moveSelectedDown() {
            const checkboxes = document.querySelectorAll('.bookmark-select:checked');
            if (checkboxes.length === 0) {
                showNotification('请先选择要移动的书签', 'error');
                return;
            }
            
            const totalRows = document.querySelectorAll('#bookmarksTable tbody tr').length;
            
            // 获取选中项的索引并排序（降序）
            const indices = Array.from(checkboxes)
                .map(cb => parseInt(cb.dataset.index))
                .sort((a, b) => b - a);
            
            // 检查是否可以移动（最后一个不能移到length位置）
            if (indices[0] === totalRows - 1) {
                showNotification('已到底部，无法继续下移', 'error');
                return;
            }
            
            // 发送到服务器进行移动
            fetch('/move_bookmark', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({indices: indices, direction: 'down'})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    renderBookmarks(data.bookmarks, data.original_bookmarks);
                    showNotification(`已下移 ${indices.length} 个书签`, 'success');
                } else {
                    showNotification('移动失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showNotification('移动出错: ' + error, 'error');
            });
        }
        
        // 计算并应用偏移量
        function calculateAndApplyOffset() {
            const contentStartPage = document.getElementById('contentStartPage').value;
            // 根据新公式计算偏移量: 偏移量 = 正文起始页 - 1
            const offset = parseInt(contentStartPage) - 1;
            
            document.getElementById('currentOffset').textContent = offset;
            
            fetch('/apply_offset', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({offset: offset, type: 'calculated'})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    renderBookmarks(data.bookmarks, data.original_bookmarks);
                    document.getElementById('currentOffset').textContent = data.offset;
                    showNotification(`偏移量已计算并应用: ${offset}`, 'success');
                } else {
                    showNotification('应用偏移量失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showNotification('应用偏移量出错: ' + error, 'error');
            });
        }
        
        // 应用手动偏移量
        function applyManualOffset() {
            const offset = parseInt(document.getElementById('manualOffset').value);
            document.getElementById('currentOffset').textContent = offset;
            
            fetch('/apply_offset', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({offset: offset, type: 'manual'})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    renderBookmarks(data.bookmarks, data.original_bookmarks);
                    document.getElementById('currentOffset').textContent = data.offset;
                    showNotification(`手动偏移量已应用: ${offset}`, 'success');
                } else {
                    showNotification('应用偏移量失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showNotification('应用偏移量出错: ' + error, 'error');
            });
        }
        
        // 预览偏移量变化
        function previewOffsetChanges() {
            const offset = parseInt(document.getElementById('currentOffset').textContent) || 0;
            fetch('/preview_offset', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({offset: offset})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const previewDiv = document.getElementById('offsetPreview');
                    let html = '<h4>偏移量应用预览:</h4><ul>';
                    data.changes.forEach(change => {
                        html += `<li>${escapeHtml(change.title)}: ${change.original_page || '无页码'} → ${change.new_page || '无页码'}</li>`;
                    });
                    html += '</ul>';
                    previewDiv.innerHTML = html;
                } else {
                    showNotification('预览失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showNotification('预览出错: ' + error, 'error');
            });
        }
        
        // 提取目录页
        function extractTocPages() {
            fetch('/extract_toc', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.image_url) {
                    document.getElementById('tocImageContainer').innerHTML = 
                        `<div class="toc-image-container"><img src="${data.image_url}" class="toc-image" alt="目录页"></div>`;
                    showNotification('目录页提取成功', 'success');
                } else {
                    showNotification('目录页提取失败: ' + (data.message || '未知错误'), 'error');
                }
            })
            .catch(error => {
                showNotification('目录页提取出错: ' + error, 'error');
            });
        }
        
        // 更新目录页范围
        function updateTocPages() {
            const tocStartPage = document.getElementById('tocStartPage').value;
            const tocEndPage = document.getElementById('tocEndPage').value;
            
            fetch('/update_toc_pages', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    toc_start_page: parseInt(tocStartPage),
                    toc_end_page: parseInt(tocEndPage)
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showNotification('目录页范围已更新', 'success');
                } else {
                    showNotification('更新目录页范围失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showNotification('更新目录页范围出错: ' + error, 'error');
            });
        }
        
        // 生成PDF
        function generatePdf() {
            const outputFileName = document.getElementById('outputFileName').value;
            
            fetch('/generate_pdf', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({output_filename: outputFileName})
            })
            .then(response => response.json())
            .then(data => {
                const statusDiv = document.getElementById('generationStatus');
                if (data.status === 'success') {
                    statusDiv.innerHTML = `<div class="status status-success">PDF生成成功: ${data.message}</div>`;
                    showNotification('PDF生成成功', 'success');
                } else {
                    statusDiv.innerHTML = `<div class="status status-error">PDF生成失败: ${data.message}</div>`;
                    showNotification('PDF生成失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                document.getElementById('generationStatus').innerHTML = 
                    `<div class="status status-error">PDF生成出错: ${error}</div>`;
                showNotification('PDF生成出错: ' + error, 'error');
            });
        }
        
        // 删除已上传文件
        function deleteUploadedFile() {
            fetch('/delete_file', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.getElementById('deleteFileBtn').classList.add('hidden');
                    showNotification('文件已删除', 'success');
                } else {
                    showNotification('删除文件失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showNotification('删除文件出错: ' + error, 'error');
            });
        }
        
        // 打开通义千问页面
        function openQwen() {
            window.open('https://tongyi.aliyun.com/', '_blank');
        }
        
        // 退出应用程序
        function exitApplication() {
            if (confirm('确定要退出程序吗？这将关闭Web服务并清理所有临时文件。')) {
                fetch('/exit', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showNotification('程序已退出，您可以关闭此窗口', 'success');
                        // 禁用页面上的所有按钮
                        const buttons = document.querySelectorAll('button');
                        buttons.forEach(button => {
                            button.disabled = true;
                        });
                    } else {
                        showNotification('退出失败: ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    showNotification('退出时出错: ' + error, 'error');
                });
            }
        }
        
        // 显示通知
        function showNotification(message, type) {
            // 创建通知div
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.textContent = message;
            
            // 添加到页面
            document.body.appendChild(notification);
            
            // 3秒后自动移除
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 3000);
        }
        
        // 处理PDF文件上传
        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const fileInput = document.getElementById('pdfFile');
            const file = fileInput.files[0];
            
            // 设置默认输出文件名
            const defaultOutputName = file.name.replace('.pdf', '') + '_bookmarked.pdf';
            document.getElementById('outputFileName').value = defaultOutputName;
            
            formData.append('pdfFile', file);
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const statusDiv = document.getElementById('uploadStatus');
                if (data.status === 'success') {
                    statusDiv.innerHTML = '<div class="status status-success">文件上传成功: ' + data.filename + '</div>';
                    document.getElementById('deleteFileBtn').classList.remove('hidden');
                    showNotification('文件上传成功', 'success');
                } else {
                    statusDiv.innerHTML = '<div class="status status-error">上传失败: ' + data.message + '</div>';
                    showNotification('上传失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                document.getElementById('uploadStatus').innerHTML = 
                    '<div class="status status-error">上传出错: ' + error + '</div>';
                showNotification('上传出错: ' + error, 'error');
            });
        });
        
        // 复制提示词到剪贴板
        function copyPrompt() {
            const promptText = `请分析这个PDF文档的目录页，并按照以下要求输出目录结构：

1. 保留完整的层级结构信息，使用缩进或编号方式表示层级关系
2. 每行输出一个目录项，格式为："标题内容 ...................... 页码"（页码前的点线为可选）
3. 对于缺失页码的条目，请根据上下文逻辑推断并补充完整页码
4. 支持多种标题格式：
   - 章节编号格式：如"第1章 绪论"、"1.1 背景介绍"
   - Markdown格式：使用#符号表示层级
   - 缩进格式：通过空格或制表符表示层级
   - 中文序数格式：如"一、"、"1."、"（一）"等
5. 保持原始层级结构，不要改变标题内容
6. 输出时不要包含任何解释性文字，只输出目录内容本身

示例输出格式：
# 第一章 绪论 1
## 1.1 研究背景 1
## 1.2 研究意义 3
# 第二章 文献综述 5
## 2.1 国内研究现状 5
## 2.2 国外研究现状 8`;
            
            navigator.clipboard.writeText(promptText).then(() => {
                showNotification('提示词已复制到剪贴板', 'success');
            }).catch(err => {
                showNotification('复制失败: ' + err, 'error');
            });
        }
        
        // 页面加载完成后检查是否有已上传文件
        window.addEventListener('load', function() {
            fetch('/check_file')
            .then(response => response.json())
            .then(data => {
                if (data.has_file) {
                    document.getElementById('deleteFileBtn').classList.remove('hidden');
                }
                
                // 检查是否有草稿
                fetch('/check_draft')
                .then(response => response.json())
                .then(draftData => {
                    if (draftData.has_draft) {
                        document.getElementById('draftIndicator').style.display = 'block';
                    }
                });
            });
        });
    </script>
</body>
</html>
    '''