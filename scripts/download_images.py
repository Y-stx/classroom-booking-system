# -*- coding: utf-8 -*-
"""下载教室类型图片"""
import urllib.request
import os

OUT_DIR = r'e:\教室预约与使用登记系统\frontend\public\images\classrooms'
os.makedirs(OUT_DIR, exist_ok=True)

# Unsplash 免费图片 URL（按教室类型）
images = {
    # 实验室：科学实验室、带实验台的教室
    'lab.jpg': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=800&auto=format&fit=crop',
    # 多媒体教室：带投影仪/屏幕的教室
    'multimedia.jpg': 'https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=800&auto=format&fit=crop',
    # 机房：电脑机房
    'computer.jpg': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop',
    # 普通教室：普通桌椅的教室
    'normal.jpg': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&auto=format&fit=crop',
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for fname, url in images.items():
    fpath = os.path.join(OUT_DIR, fname)
    if os.path.exists(fpath) and os.path.getsize(fpath) > 10000:
        print(f'  {fname} 已存在')
        continue
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        with open(fpath, 'wb') as f:
            f.write(data)
        print(f'  {fname} 下载成功 ({len(data)/1024:.1f} KB)')
    except Exception as e:
        print(f'  {fname} 下载失败: {e}')

# 检查结果
print('\n=== 下载结果 ===')
for f in os.listdir(OUT_DIR):
    fpath = os.path.join(OUT_DIR, f)
    print(f'  {f}: {os.path.getsize(fpath)/1024:.1f} KB')
