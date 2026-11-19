# -*- coding: utf-8 -*-
"""系统设计文档 Markdown → DOCX 转换脚本"""

import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

def set_font(run, size=None, bold=None, color=None, font_name='宋体'):
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)

def add_heading(doc, text, level):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = '黑体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        if level == 1:
            run.font.size = Pt(22)
        elif level == 2:
            run.font.size = Pt(16)
        elif level == 3:
            run.font.size = Pt(14)
        else:
            run.font.size = Pt(12)
    return h

def add_paragraph(doc, text, indent=False):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Pt(24)
    run = p.add_run(text)
    set_font(run, size=11)
    return p

def add_table_from_data(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    # 表头
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        run = cell.paragraphs[0].add_run(h)
        set_font(run, size=10, bold=True, font_name='黑体')
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    # 数据行
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = ''
            run = cell.paragraphs[0].add_run(str(val))
            set_font(run, size=10)
    return table

def convert_md_to_docx(md_path, docx_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 拆分段落
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # 跳过空行
        if not line.strip():
            i += 1
            continue

        # 文档标题 (第一行 # )
        if line.startswith('# ') and i == 0:
            # 跳过，手动添加标题页
            i += 1
            continue

        # 标题
        h_match = re.match(r'^(#{1,4})\s+(.+)$', line)
        if h_match:
            level = len(h_match.group(1))
            text = h_match.group(2).strip()
            # 跳过 --- 分隔线
            if text.startswith('='):
                i += 1
                continue
            add_heading(doc, text, min(level, 4))
            i += 1
            continue

        # 代码块 (跳过 Mermaid 图, 保留代码示例)
        if line.startswith('```'):
            lang = line[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # 跳过结束 ```

            # 如果是 mermaid 图，跳过（Word不支持）
            if lang == 'mermaid':
                # 提取第一行作为图的标题
                mermaid_text = '\n'.join(code_lines)
                title_match = re.search(r'(graph|flowchart|sequenceDiagram|stateDiagram|erDiagram|classDiagram|timeline|gantt|pie)\s+(.+)', mermaid_text)
                if title_match:
                    add_paragraph(doc, f"[图示：{title_match.group(0)} — Mermaid 源码见 Markdown 文件]", indent=True)
                else:
                    add_paragraph(doc, "[图示：Mermaid 图表 — 源码见 Markdown 文件]", indent=True)
                continue

            # 其他代码块作为代码示例
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Pt(12)
            for cl in code_lines:
                run = p.add_run(cl + '\n')
                run.font.name = 'Consolas'
                run.font.size = Pt(9)
            continue

        # 表格
        if line.startswith('|') and line.endswith('|'):
            # 收集表格
            table_lines = []
            while i < len(lines) and lines[i].startswith('|'):
                table_lines.append(lines[i])
                i += 1

            # 跳过分隔行 |---|---|
            data_lines = [tl for tl in table_lines if not re.match(r'^\|[\s\-|:]+\|$', tl)]
            if not data_lines:
                continue

            headers = [c.strip() for c in data_lines[0].split('|')[1:-1]]
            rows = []
            for dl in data_lines[1:]:
                cells = [c.strip() for c in dl.split('|')[1:-1]]
                rows.append(cells)

            add_table_from_data(doc, headers, rows)
            continue

        # 列表项
        list_match = re.match(r'^(\s*)([-*]|\d+\.)\s+(.+)$', line)
        if list_match:
            indent_level = len(list_match.group(1)) // 2
            text = list_match.group(3)
            p = doc.add_paragraph(style='List Bullet')
            if indent_level > 0:
                p.paragraph_format.left_indent = Pt(18 * indent_level)
            # 处理加粗标记
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            run = p.add_run(text)
            set_font(run, size=11)
            i += 1
            continue

        # 普通段落
        text = line.strip()
        if text:
            # 清理 Markdown 格式
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # 加粗
            text = re.sub(r'`(.+?)`', r'\1', text)         # 行内代码
            text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text) # 链接
            # 跳过 HTML 注释
            if text.startswith('<!--') or text.startswith('> 版本') or text.startswith('> '):
                text = text.lstrip('> ').strip()
            # 以 > 开头的引用段落
            if line.startswith('>'):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Pt(24)
                run = p.add_run(text)
                set_font(run, size=10, color=(107, 114, 128))
            else:
                add_paragraph(doc, text, indent=True)

        i += 1

# ========= 主程序 =========
doc = Document()

# 设置默认字体
doc.styles['Normal'].font.name = '宋体'
doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
doc.styles['Normal'].font.size = Pt(11)

# 页面边距
from docx.shared import Inches
section = doc.sections[0]
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)
section.left_margin = Inches(1.2)
section.right_margin = Inches(1.2)

# 标题页
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.paragraph_format.space_after = Pt(6)
run = title.add_run('教室预约与使用登记系统')
run.font.name = '黑体'
run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
run.font.size = Pt(28)
run.bold = True

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
subtitle.paragraph_format.space_after = Pt(4)
run = subtitle.add_run('系统设计文档')
run.font.name = '黑体'
run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
run.font.size = Pt(22)
run.bold = True

doc.add_paragraph()  # 空行

info_lines = [
    '版本：v1.0',
    '日期：2026-09-14',
    '项目：教室预约与使用登记系统',
    '技术栈：Vue 3 + Spring Boot 3 + MySQL 8 + Redis 7'
]
for il in info_lines:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(il)
    set_font(run, size=12)

doc.add_page_break()

# 转换 Markdown
convert_md_to_docx(
    r'e:\教室预约与使用登记系统\项目文档\系统设计文档.md',
    r'e:\教室预约与使用登记系统\项目文档\系统设计文档.docx'
)

# 保存
output = r'e:\教室预约与使用登记系统\项目文档\系统设计文档.docx'
doc.save(output)
print(f'文档已生成: {output}')
