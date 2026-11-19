# -*- coding: utf-8 -*-
"""渲染 Mermaid 图表 - 使用 POST 方式调用 Kroki API"""

import re
import json
import os
import urllib.request

OUTPUT_DIR = r'e:\教室预约与使用登记系统\项目文档\diagrams'
MD_PATH = r'e:\教室预约与使用登记系统\项目文档\系统设计文档.md'
DOCX_PATH = r'e:\教室预约与使用登记系统\项目文档\系统设计文档.docx'

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(MD_PATH, 'r', encoding='utf-8') as f:
    md_content = f.read()

mermaid_pattern = re.compile(r'```mermaid\n(.*?)```', re.DOTALL)
matches = mermaid_pattern.findall(md_content)
print(f'找到 {len(matches)} 个 Mermaid 图表')

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

def render_kroki(mermaid_code, output_path):
    """用 Kroki POST 方式渲染"""
    url = 'https://kroki.io/mermaid/svg'
    payload = json.dumps({
        "diagram": mermaid_code,
        "options": {"theme": "default"}
    }).encode('utf-8')
    req = urllib.request.Request(url, data=payload,
                                headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'},
                                method='POST')
    with urllib.request.urlopen(req, timeout=30) as resp:
        svg_data = resp.read()
    # SVG 也能用，保存
    with open(output_path.replace('.png', '.svg'), 'wb') as f:
        f.write(svg_data)
    return svg_data

import cairosvg  # 尝试转 PNG if available

diagram_files = []
for idx, mermaid_code in enumerate(matches):
    name = diagram_names[idx] if idx < len(diagram_names) else f'diagram_{idx+1}'
    svg_path = os.path.join(OUTPUT_DIR, f'{name}.svg')
    png_path = os.path.join(OUTPUT_DIR, f'{name}.png')

    if os.path.exists(svg_path) and os.path.getsize(svg_path) > 1000:
        print(f'  [{idx+1}] {name}.svg 已存在，跳过')
        diagram_files.append((idx, name, svg_path, png_path))
        continue

    try:
        svg_data = render_kroki(mermaid_code, svg_path)
        size_kb = len(svg_data) / 1024
        print(f'  [{idx+1}] {name}.svg 渲染成功 ({size_kb:.1f} KB)')

        # 尝试转 PNG
        try:
            import cairosvg
            cairosvg.svg2png(bytestring=svg_data, write_to=png_path, output_width=1600)
            print(f'  [{idx+1}] {name}.png 转换成功')
        except ImportError:
            print(f'  [{idx+1}] cairosvg 未安装，保留 SVG 格式')
        except Exception as e:
            print(f'  [{idx+1}] PNG 转换失败: {e}')

        diagram_files.append((idx, name, svg_path, png_path))
    except Exception as e:
        print(f'  [{idx+1}] {name} 渲染失败: {e}')
        diagram_files.append((idx, name, None, None))

print(f'\n共处理 {len(diagram_files)} 个图表')

# ============ 生成 Word 文档 ============
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
        if level == 1: run.font.size = Pt(22)
        elif level == 2: run.font.size = Pt(16)
        elif level == 3: run.font.size = Pt(14)
        else: run.font.size = Pt(12)
    return h

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

# 构建 mermaid_idx → svg_path/png_path 映射
idx_to_svg = {}
idx_to_png = {}
for f_idx, name, svg, png in diagram_files:
    idx_to_svg[f_idx] = svg
    idx_to_png[f_idx] = png

doc = Document()
doc.styles['Normal'].font.name = '宋体'
doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
doc.styles['Normal'].font.size = Pt(11)
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
run.font.size = Pt(28); run.bold = True

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run('系统设计文档')
run.font.name = '黑体'
run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
run.font.size = Pt(22); run.bold = True

doc.add_paragraph()
for il in ['版本：v1.0', '日期：2026-09-14', '项目：教室预约与使用登记系统', '技术栈：Vue 3 + Spring Boot 3 + MySQL 8 + Redis 7']:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(p.add_run(il), size=12)
doc.add_page_break()

# 正文
lines = md_content.split('\n')
i = 0; mermaid_idx = 0

while i < len(lines):
    line = lines[i]
    if not line.strip(): i += 1; continue
    if line.startswith('# ') and i == 0: i += 1; continue

    h_match = re.match(r'^(#{1,4})\s+(.+)$', line)
    if h_match:
        level = len(h_match.group(1))
        text = h_match.group(2).strip()
        if text.startswith('=') or text.startswith('-'): i += 1; continue
        add_heading(doc, text, min(level, 4))
        i += 1; continue

    if line.startswith('```mermaid'):
        mermaid_idx += 1
        j = i + 1
        while j < len(lines) and not lines[j].startswith('```'): j += 1

        svg_path = idx_to_svg.get(mermaid_idx - 1)
        png_path = idx_to_png.get(mermaid_idx - 1)
        caption = diagram_captions.get(mermaid_idx - 1, f'图{mermaid_idx}')

        # 优先用 PNG，其次 SVG
        img_path = None
        if png_path and os.path.exists(png_path) and os.path.getsize(png_path) > 500:
            img_path = png_path
        elif svg_path and os.path.exists(svg_path) and os.path.getsize(svg_path) > 500:
            img_path = svg_path

        if img_path:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            try:
                run.add_picture(img_path, width=Inches(5.8))
            except Exception as e:
                print(f'  插入图片失败 {img_path}: {e}')
                p2 = doc.add_paragraph()
                set_font(p2.add_run(f'[图片文件: {os.path.basename(img_path)}]'), size=10, color=(128,128,128))
        else:
            p2 = doc.add_paragraph()
            set_font(p2.add_run(f'[图未能渲染，请查看 Markdown 源文件中的 Mermaid 代码]'), size=10, color=(200,0,0))

        # 图注
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_font(cp.add_run(caption), size=10, bold=True)

        i = j + 1; continue

    if line.startswith('```'):
        code_lines = []
        i += 1
        while i < len(lines) and not lines[i].startswith('```'):
            code_lines.append(lines[i]); i += 1
        i += 1
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Pt(12)
        for cl in code_lines:
            run = p.add_run(cl + '\n')
            run.font.name = 'Consolas'; run.font.size = Pt(9)
        continue

    if line.startswith('|') and line.endswith('|'):
        table_lines = []
        while i < len(lines) and lines[i].startswith('|'):
            table_lines.append(lines[i]); i += 1
        data_lines = [tl for tl in table_lines if not re.match(r'^\|[\s\-|:]+\|$', tl)]
        if not data_lines: continue
        headers = [c.strip() for c in data_lines[0].split('|')[1:-1]]
        rows = []
        for dl in data_lines[1:]:
            cells = [c.strip() for c in dl.split('|')[1:-1]]
            rows.append(cells)
        add_table_from_data(doc, headers, rows)
        continue

    list_match = re.match(r'^(\s*)([-*]|\d+\.)\s+(.+)$', line)
    if list_match:
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', list_match.group(3))
        p = doc.add_paragraph(style='List Bullet')
        set_font(p.add_run(text), size=11)
        i += 1; continue

    text = line.strip()
    if text:
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
        if line.startswith('>'):
            text = text.lstrip('> ').strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Pt(24)
            set_font(p.add_run(text), size=10, color=(107,114,128))
        else:
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Pt(24)
            set_font(p.add_run(text), size=11)
    i += 1

doc.save(DOCX_PATH)
size_kb = os.path.getsize(DOCX_PATH) / 1024
print(f'\n✓ Word 文档已生成: {DOCX_PATH}')
print(f'✓ 文档大小: {size_kb:.1f} KB')
print(f'✓ SVG 图片目录: {OUTPUT_DIR}')
