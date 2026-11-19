# -*- coding: utf-8 -*-
"""渲染 Mermaid 图表为 SVG"""
import re, json, os, urllib.request

OUTPUT_DIR = r'e:\教室预约与使用登记系统\项目文档\diagrams'
MD_PATH = r'e:\教室预约与使用登记系统\项目文档\系统设计文档.md'
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
        payload = json.dumps({'diagram': code, 'options': {'theme': 'default'}}).encode('utf-8')
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
        diagram_files[idx] = None

# 输出 JSON 供后续步骤使用
import json as j
with open(os.path.join(OUTPUT_DIR, '_index.json'), 'w', encoding='utf-8') as f:
    j.dump(diagram_files, f)
print(f'\n图表索引已保存，共 {sum(1 for v in diagram_files.values() if v)} 个成功')
