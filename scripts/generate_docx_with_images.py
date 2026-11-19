# -*- coding: utf-8 -*-
"""
渲染 Mermaid 图表为 PNG 并生成带图的 Word 文档
使用 Kroki API (https://kroki.io) 免费在线渲染
"""

import re
import base64
import urllib.request
import urllib.parse
import json
import os

# 输出目录
OUTPUT_DIR = r'e:\教室预约与使用登记系统\项目文档\diagrams'
MD_PATH = r'e:\教室预约与使用登记系统\项目文档\系统设计文档.md'
DOCX_PATH = r'e:\教室预约与使用登记系统\项目文档\系统设计文档.docx'

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 读取 Markdown
with open(MD_PATH, 'r', encoding='utf-8') as f:
    md_content = f.read()

# 提取所有 mermaid 代码块
mermaid_pattern = re.compile(r'```mermaid\n(.*?)```', re.DOTALL)
matches = mermaid_pattern.findall(md_content)

print(f'找到 {len(matches)} 个 Mermaid 图表')

# 图表名称映射（按顺序）
diagram_names = [
    '01_系统架构图',
    '02_模块划分图',
    '03_登录时序图',
    '04_JWT鉴权时序图',
    '05_预约创建流程图',
    '06_预约状态机',
    '07_ER图',
    '08_审批通过时序图',
    '09_签到签退时序图',
    '10_JWT拦截器流程图',
    '11_预约状态机流程图',
]

# 渲染每个图表
diagram_files = []
for idx, mermaid_code in enumerate(matches):
    name = diagram_names[idx] if idx < len(diagram_names) else f'diagram_{idx+1}'
    png_path = os.path.join(OUTPUT_DIR, f'{name}.png')

    if os.path.exists(png_path) and os.path.getsize(png_path) > 1000:
        print(f'  [{idx+1}] {name}.png 已存在，跳过')
        diagram_files.append((idx, name, png_path))
        continue

    # Kroki API: POST mermaid code, get PNG back
    # URL encode the mermaid code
    encoded = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('ascii').rstrip('=')
    url = f'https://kroki.io/mermaid/png/{encoded}'

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            with open(png_path, 'wb') as pf:
                pf.write(data)
            size_kb = len(data) / 1024
            print(f'  [{idx+1}] {name}.png 渲染成功 ({size_kb:.1f} KB)')
            diagram_files.append((idx, name, png_path))
    except Exception as e:
        print(f'  [{idx+1}] {name} 渲染失败: {e}')
        # 尝试用备用方法
        try:
            # 备用：用 Mermaid Ink API
            mermaid_json = json.dumps({"code": mermaid_code, "mermaid": {"theme": "default"}})
            data = json.dumps({"definition": mermaid_code, "config": '{"theme": "default"}'}).encode('utf-8')
            req = urllib.request.Request('https://mermaid.ink/img', data=data,
                                        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                img_b64 = resp.read().decode('utf-8')
                img_data = base64.b64decode(img_b64)
                with open(png_path, 'wb') as pf:
                    pf.write(img_data)
                print(f'  [{idx+1}] {name}.png 备用渲染成功 ({len(img_data)/1024:.1f} KB)')
                diagram_files.append((idx, name, png_path))
        except Exception as e2:
            print(f'  [{idx+1}] {name} 备用渲染也失败: {e2}')
            diagram_files.append((idx, name, None))

print(f'\n共处理 {len(diagram_files)} 个图表，输出目录: {OUTPUT_DIR}')

# ============ 现在生成带图的 Word 文档 ============
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
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        run = cell.paragraphs[0].add_run(h)
        set_font(run, size=10, bold=True, font_name='黑体')
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = ''
            run = cell.paragraphs[0].add_run(str(val))
            set_font(run, size=10)
    return table

def add_diagram(doc, img_path, caption):
    """添加图片 + 图注"""
    if img_path and os.path.exists(img_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(img_path, width=Inches(5.8))
    # 图注
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cp.add_run(caption)
    set_font(run, size=10, bold=True)

# 重新解析 Markdown，这次把 mermaid 块替换为图片
lines = md_content.split('\n')
i = 0
mermaid_idx = 0

# 图表标题映射（用于图注）
diagram_captions = {
    0: '图1  系统总体架构图',
    1: '图2  系统模块划分图',
    2: '图3  用户登录时序图',
    3: '图4  JWT鉴权拦截器时序图',
    4: '图5  预约创建校验流程图',
    5: '图6  预约状态机（状态流转图）',
    6: '图7  数据库ER图',
    7: '图8  审批通过时序图',
    8: '图9  签到/签退时序图',
    9: '图10 JWT认证拦截器流程图',
    10: '图11 预约状态流转流程图',
}

doc = Document()

# 设置默认字体
doc.styles['Normal'].font.name = '宋体'
doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
doc.styles['Normal'].font.size = Pt(11)

# 页面边距
section = doc.sections[0]
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)
section.left_margin = Inches(1.2)
section.right_margin = Inches(1.2)

# === 标题页 ===
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

doc.add_paragraph()
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

# === 正文 ===
while i < len(lines):
    line = lines[i]

    if not line.strip():
        i += 1
        continue

    # 跳过文档首行 #
    if line.startswith('# ') and i == 0:
        i += 1
        continue

    # 标题
    h_match = re.match(r'^(#{1,4})\s+(.+)$', line)
    if h_match:
        level = len(h_match.group(1))
        text = h_match.group(2).strip()
        if text.startswith('=') or text.startswith('-'):
            i += 1
            continue
        add_heading(doc, text, min(level, 4))
        i += 1
        continue

    # Mermaid 代码块 → 插入图片
    if line.startswith('```mermaid'):
        mermaid_idx += 1
        # 找到结束 ```
        j = i + 1
        while j < len(lines) and not lines[j].startswith('```'):
            j += 1
        # 获取图表图片路径
        diagram_name = diagram_names[mermaid_idx - 1] if (mermaid_idx - 1) < len(diagram_names) else f'diagram_{mermaid_idx}'
        png_path = os.path.join(OUTPUT_DIR, f'{diagram_name}.png')
        caption = diagram_captions.get(mermaid_idx - 1, f'图{mermaid_idx}')
        add_diagram(doc, png_path, caption)
        i = j + 1
        continue

    # 其他代码块（非 mermaid）
    if line.startswith('```'):
        code_lines = []
        i += 1
        while i < len(lines) and not lines[i].startswith('```'):
            code_lines.append(lines[i])
            i += 1
        i += 1
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Pt(12)
        code_text = '\n'.join(code_lines)
        # 截断过长的代码
        if len(code_text) > 2000:
            code_text = code_text[:2000] + '\n...（代码过长已截断，完整内容见 Markdown 文件）'
        for cl in code_text.split('\n'):
            run = p.add_run(cl + '\n')
            run.font.name = 'Consolas'
            run.font.size = Pt(9)
        continue

    # 表格
    if line.startswith('|') and line.endswith('|'):
        table_lines = []
        while i < len(lines) and lines[i].startswith('|'):
            table_lines.append(lines[i])
            i += 1
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
        text = list_match.group(3)
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        p = doc.add_paragraph(style='List Bullet')
        run = p.add_run(text)
        set_font(run, size=11)
        i += 1
        continue

    # 普通段落
    text = line.strip()
    if text:
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
        if line.startswith('>'):
            text = text.lstrip('> ').strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Pt(24)
            run = p.add_run(text)
            set_font(run, size=10, color=(107, 114, 128))
        else:
            add_paragraph(doc, text, indent=True)
    i += 1

# 保存
doc.save(DOCX_PATH)
print(f'\n✓ Word 文档已生成: {DOCX_PATH}')
print(f'✓ 文档大小: {os.path.getsize(DOCX_PATH) / 1024:.1f} KB')
