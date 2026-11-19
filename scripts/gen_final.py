# -*- coding: utf-8 -*-
"""渲染 Mermaid 图表为 SVG - 使用正确字段名"""
import re, json, os, urllib.request

OUTPUT_DIR = r'e:\教室预约与使用登记系统\项目文档\diagrams'
MD_PATH = r'e:\教室预约与使用登记系统\项目文档\系统设计文档.md'
DOCX_PATH = r'e:\教室预约与使用登记系统\项目文档\系统设计文档.docx'
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(MD_PATH, 'r', encoding='utf-8') as f:
    md_content = f.read()

pattern = re.compile(r'```mermaid\n(.*?)```', re.DOTALL)
matches = pattern.findall(md_content)
print(f'找到 {len(matches)} 个 Mermaid 图表')

diagram_names = [
    '01_系统架构图', '02_模块划分图', '03_登录时序图', '04_JWT鉴权时序图',
    '05_预约创建流程图', '06_预约状态机', '07_ER图', '08_审批通过时序图',
    '09_签到签退时序图', '10_JWT拦截器流程图', '11_预约状态机流程图',
]

diagram_files = {}
for idx, code in enumerate(matches):
    name = diagram_names[idx] if idx < len(diagram_names) else f'diagram_{idx+1}'
    svg_path = os.path.join(OUTPUT_DIR, f'{name}.svg')

    if os.path.exists(svg_path) and os.path.getsize(svg_path) > 1000:
        print(f'  [{idx+1}] {name}.svg 已存在')
        diagram_files[idx] = svg_path
        continue

    try:
        # 关键：字段名是 diagram_source
        payload = json.dumps({'diagram_source': code}).encode('utf-8')
        req = urllib.request.Request('https://kroki.io/mermaid/svg', data=payload,
                    headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, method='POST')
        with urllib.request.urlopen(req, timeout=30) as resp:
            svg = resp.read()
        with open(svg_path, 'wb') as pf:
            pf.write(svg)
        print(f'  [{idx+1}] {name}.svg OK ({len(svg)/1024:.1f} KB)')
        diagram_files[idx] = svg_path
    except Exception as e:
        print(f'  [{idx+1}] {name} FAIL: {e}')
        # 打印响应体帮助调试
        if hasattr(e, 'read'):
            try: print('    响应:', e.read().decode()[:300])
            except: pass
        diagram_files[idx] = None

success = sum(1 for v in diagram_files.values() if v)
print(f'\n渲染成功: {success}/{len(matches)}')

# ============ 生成带图的 Word 文档 ============
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

def set_font(run, size=None, bold=None, color=None, font_name='宋体'):
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    if size: run.font.size = Pt(size)
    if bold is not None: run.bold = bold
    if color: run.font.color.rgb = RGBColor(*color)

def add_table(doc, headers, rows):
    table = doc.add_table(rows=1+len(rows), cols=len(headers))
    table.style = 'Table Grid'
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        set_font(cell.paragraphs[0].add_run(h), size=10, bold=True, font_name='黑体')
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = table.rows[r+1].cells[c]
            cell.text = ''
            set_font(cell.paragraphs[0].add_run(str(val)), size=10)

diagram_captions = {
    0: '图1  系统总体架构图', 1: '图2  系统模块划分图',
    2: '图3  用户登录时序图', 3: '图4  JWT鉴权拦截器时序图',
    4: '图5  预约创建校验流程图', 5: '图6  预约状态机（状态流转图）',
    6: '图7  数据库ER图', 7: '图8  审批通过时序图',
    8: '图9  签到/签退时序图', 9: '图10 JWT认证拦截器流程图',
    10: '图11 预约状态流转流程图',
}

doc = Document()
doc.styles['Normal'].font.name = '宋体'
doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
doc.styles['Normal'].font.size = Pt(11)
for s in doc.sections:
    s.top_margin = Inches(1); s.bottom_margin = Inches(1)
    s.left_margin = Inches(1.2); s.right_margin = Inches(1.2)

# 标题页
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(6)
run = p.add_run('教室预约与使用登记系统'); run.font.name = '黑体'
run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体'); run.font.size = Pt(28); run.bold = True
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('系统设计文档'); run.font.name = '黑体'
run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体'); run.font.size = Pt(22); run.bold = True
doc.add_paragraph()
for il in ['版本：v1.0', '日期：2026-09-14', '项目：教室预约与使用登记系统', '技术栈：Vue 3 + Spring Boot 3 + MySQL 8 + Redis 7']:
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; set_font(p.add_run(il), size=12)
doc.add_page_break()

# 正文
lines = md_content.split('\n')
i = 0; mm_idx = 0
while i < len(lines):
    line = lines[i]
    if not line.strip(): i += 1; continue
    if line.startswith('# ') and i == 0: i += 1; continue

    h = re.match(r'^(#{1,4})\s+(.+)$', line)
    if h:
        lv, text = len(h.group(1)), h.group(2).strip()
        if text.startswith('=') or text.startswith('-'): i += 1; continue
        hdr = doc.add_heading(text, level=min(lv, 4))
        for r in hdr.runs:
            r.font.name = '黑体'; r._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
            if lv == 1: r.font.size = Pt(22)
            elif lv == 2: r.font.size = Pt(16)
            elif lv == 3: r.font.size = Pt(14)
            else: r.font.size = Pt(12)
        i += 1; continue

    if line.startswith('```mermaid'):
        mm_idx += 1
        j = i + 1
        while j < len(lines) and not lines[j].startswith('```'): j += 1
        svg_path = diagram_files.get(mm_idx - 1)
        caption = diagram_captions.get(mm_idx - 1, f'图{mm_idx}')
        if svg_path and os.path.exists(svg_path):
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            try: p.add_run().add_picture(svg_path, width=Inches(5.8))
            except Exception as e:
                set_font(doc.add_paragraph().add_run(f'[图片插入失败: {e}]'), size=9, color=(200,0,0))
        else:
            set_font(doc.add_paragraph().add_run('[图未能渲染，请查看 Markdown 源文件]'), size=10, color=(200,0,0))
        cp = doc.add_paragraph(); cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_font(cp.add_run(caption), size=10, bold=True)
        i = j + 1; continue

    if line.startswith('```'):
        cls = line[3:].strip()
        code_lines = []; i += 1
        while i < len(lines) and not lines[i].startswith('```'):
            code_lines.append(lines[i]); i += 1
        i += 1
        if cls == 'mermaid': i = 0  # 不会到这里
        p = doc.add_paragraph(); p.paragraph_format.left_indent = Pt(12)
        for cl in code_lines:
            r = p.add_run(cl + '\n'); r.font.name = 'Consolas'; r.font.size = Pt(9)
        continue

    if line.startswith('|') and line.endswith('|'):
        tls = []
        while i < len(lines) and lines[i].startswith('|'):
            tls.append(lines[i]); i += 1
        dls = [t for t in tls if not re.match(r'^\|[\s\-|:]+\|$', t)]
        if not dls: continue
        hs = [c.strip() for c in dls[0].split('|')[1:-1]]
        rows = [[c.strip() for c in dl.split('|')[1:-1]] for dl in dls[1:]]
        add_table(doc, hs, rows); continue

    lm = re.match(r'^\s*[-*]\s+(.+)$', line)
    if lm:
        t = re.sub(r'\*\*(.+?)\*\*', r'\1', lm.group(1))
        t = re.sub(r'`(.+?)`', r'\1', t)
        p = doc.add_paragraph(style='List Bullet'); set_font(p.add_run(t), size=11)
        i += 1; continue

    t = line.strip()
    if t:
        t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
        t = re.sub(r'`(.+?)`', r'\1', t)
        t = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', t)
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Pt(24)
        set_font(p.add_run(t), size=11)
    i += 1

doc.save(DOCX_PATH)
print(f'\n✓ Word 文档: {DOCX_PATH} ({os.path.getsize(DOCX_PATH)/1024:.1f} KB)')
print(f'✓ SVG 图片: {OUTPUT_DIR}')
