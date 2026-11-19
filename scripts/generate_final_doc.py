# -*- coding: utf-8 -*-
"""生成最终项目文档和个人开发日志"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

# ===== 全局样式设置 =====
FONT_NAME = '宋体'
FONT_SIZE_BODY = Pt(12)        # 小四号
FONT_SIZE_H1 = Pt(15)          # 小三号（章标题）
FONT_SIZE_H2 = Pt(12)          # 小四号（二级标题）
FONT_SIZE_H3 = Pt(12)          # 小四号（三级标题）
FONT_SIZE_H4 = Pt(12)
LINE_SPACING = 1.5
# 页边距：上30mm 下25mm 左30mm 右20mm
MARGIN_TOP = Cm(3.0)
MARGIN_BOTTOM = Cm(2.5)
MARGIN_LEFT = Cm(3.0)
MARGIN_RIGHT = Cm(2.0)

MEMBERS = [
    ('2413040818', '冯翌轩', '后端整体架构、统一返回格式、全局异常、认证授权(JWT)、预约审批业务'),
    ('2413040824', '秦伟彪', '教室CRUD、使用登记(签到签退)、用户管理、MyBatis Mapper SQL、Service实现'),
    ('2413040831', '常锦相', '所有列表页、表单页、个人中心、系统管理、API对接、ECharts图表、表格交互'),
    ('2413040835', '杨坤豫', '进度统筹、接口对齐、代码合并、部署上线、前端整体架构(路由/Pinia/主题)、登录页+主布局+三角色首页'),
    ('2413040841', '李育真', '数据库建表、索引、初始数据SQL、前后端联调、Swagger接口验证、项目文档、部署文档'),
]


def set_cell_text(cell, text, bold=False, font_size=Pt(10), align=WD_ALIGN_PARAGRAPH.CENTER):
    """设置表格单元格文字"""
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = align
    run = p.add_run(text)
    run.font.name = FONT_NAME
    run.font.size = font_size
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)


def set_cell_shading(cell, color):
    """设置单元格背景色"""
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color)
    cell._tc.get_or_add_tcPr().append(shading)


def setup_document(doc):
    """设置文档默认样式"""
    # 设置默认字体
    style = doc.styles['Normal']
    style.font.name = FONT_NAME
    style.font.size = FONT_SIZE_BODY
    style._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)
    style.paragraph_format.line_spacing = LINE_SPACING
    
    # 设置页面边距：上30mm 下25mm 左30mm 右20mm
    for section in doc.sections:
        section.top_margin = MARGIN_TOP
        section.bottom_margin = MARGIN_BOTTOM
        section.left_margin = MARGIN_LEFT
        section.right_margin = MARGIN_RIGHT
        # 添加页眉
        header = section.header
        header_para = header.paragraphs[0]
        header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = header_para.add_run('软件学院软件实践说明书')
        run.font.name = '黑体'
        run.font.size = Pt(12)  # 小四号
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')


def add_heading_custom(doc, text, level=1):
    """添加标题"""
    h = doc.add_heading(text, level=level)
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    # 段前段后间距
    h.paragraph_format.space_before = Pt(6)
    h.paragraph_format.space_after = Pt(6)
    for run in h.runs:
        run.font.name = '黑体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        if level == 0:
            run.font.size = Pt(26)
            run.font.bold = True
            h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif level == 1:
            # 一级标题：小三号黑体，加粗
            run.font.size = FONT_SIZE_H1
            run.font.bold = True
        elif level == 2:
            # 二级标题：小四号黑体，加粗
            run.font.size = FONT_SIZE_H2
            run.font.bold = True
        elif level == 3:
            # 三级标题：小四号黑体，不加粗
            run.font.size = FONT_SIZE_H3
            run.font.bold = False
        elif level == 4:
            run.font.size = FONT_SIZE_H4
            run.font.bold = False
    return h


def add_para(doc, text, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent_first=True):
    """添加段落"""
    p = doc.add_paragraph()
    p.alignment = align
    if indent_first:
        p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = LINE_SPACING
    run = p.add_run(text)
    run.font.name = FONT_NAME
    run.font.size = FONT_SIZE_BODY
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)
    return p


def add_table_with_header(doc, headers, rows, col_widths=None):
    """添加带表头的表格"""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # 表头
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        set_cell_text(cell, h, bold=True)
        set_cell_shading(cell, 'D9E2F3')
    
    # 数据行
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.rows[ri + 1].cells[ci]
            set_cell_text(cell, str(val), bold=False, align=WD_ALIGN_PARAGRAPH.LEFT if ci > 0 else WD_ALIGN_PARAGRAPH.CENTER)
    
    if col_widths:
        for ri, row in enumerate(table.rows):
            for ci, width in enumerate(col_widths):
                row.cells[ci].width = Cm(width)
    
    return table


# ===== 1. 封面页 =====
def add_cover(doc):
    """添加封面页 - 按照中北大学软件学院模板"""
    # 顶部空行
    for _ in range(2):
        doc.add_paragraph()
    
    # 学校名称
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('中北大学')
    run.font.name = FONT_NAME
    run.font.size = Pt(36)
    run.font.bold = True
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)
    
    # 文档类型
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('软件实践说明书')
    run.font.name = FONT_NAME
    run.font.size = Pt(36)
    run.font.bold = True
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)
    
    # 空行
    for _ in range(3):
        doc.add_paragraph()
    
    # 题目 - 一号黑体字，居中
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('教室预约与使用登记系统')
    run.font.name = '黑体'
    run.font.size = Pt(26)  # 一号字
    run.font.bold = True
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    
    # 空行
    for _ in range(2):
        doc.add_paragraph()
    
    # 成员信息 - 学号：姓名（三号楷体）
    for sid, name, _ in MEMBERS:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f'学    号：{sid}            姓    名：{name}')
        run.font.name = '楷体'
        run.font.size = Pt(16)  # 三号
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')
    
    # 空行
    doc.add_paragraph()
    
    # 学院/专业/方向/指导教师（三号楷体）
    info_items = [
        ('学    院', '软件学院'),
        ('专    业', '软件工程'),
        ('方向名称', '软件开发与测试'),
        ('指导教师', '张淑娟、王亚恒'),
    ]
    for label, value in info_items:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f'{label}：{value}')
        run.font.name = '楷体'
        run.font.size = Pt(16)  # 三号
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')
    
    # 空行
    for _ in range(2):
        doc.add_paragraph()
    
    # 日期
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('2026年9月')
    run.font.name = FONT_NAME
    run.font.size = Pt(16)
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)
    
    # 换页
    doc.add_page_break()


# ===== 2. 目录页 =====
def add_toc(doc):
    """添加目录页"""
    add_heading_custom(doc, '目  录', level=0)
    
    toc_items = [
        ('第1章 引言', 1),
        ('1.1 编写目的', 2),
        ('1.2 项目背景', 2),
        ('1.3 术语定义', 2),
        ('1.4 参考资料', 2),
        ('第2章 系统需求分析', 1),
        ('2.1 系统定位与业务价值', 2),
        ('2.2 用户角色与权限', 2),
        ('2.3 功能需求', 2),
        ('2.4 非功能需求', 2),
        ('2.5 数据模型需求', 2),
        ('第3章 系统概要设计', 1),
        ('3.1 系统架构设计', 2),
        ('3.2 技术路线', 2),
        ('3.3 模块划分', 2),
        ('3.4 接口规范', 2),
        ('第4章 系统详细设计', 1),
        ('4.1 数据库设计', 2),
        ('4.2 认证模块详细设计', 2),
        ('4.3 预约模块详细设计', 2),
        ('4.4 审批模块详细设计', 2),
        ('4.5 使用登记模块详细设计', 2),
        ('4.6 前端路由与页面设计', 2),
        ('第5章 系统实现', 1),
        ('5.1 开发环境', 2),
        ('5.2 后端核心实现', 2),
        ('5.3 前端核心实现', 2),
        ('5.4 数据库实现', 2),
        ('5.5 界面展示', 2),
        ('第6章 系统测试及结果', 1),
        ('6.1 测试环境', 2),
        ('6.2 自动化测试', 2),
        ('6.3 手工功能测试', 2),
        ('6.4 缺陷分析与修复', 2),
        ('6.5 测试结论', 2),
        ('第7章 结论', 1),
        ('7.1 完成情况总结', 2),
        ('7.2 不足与展望', 2),
        ('参考文献', 1),
        ('致谢', 1),
    ]
    
    for item, level in toc_items:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = LINE_SPACING
        indent = 0 if level == 1 else Cm(0.74)
        p.paragraph_format.first_line_indent = indent
        run = p.add_run(item)
        run.font.name = FONT_NAME
        run.font.size = Pt(12)
        run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)
        if level == 1:
            run.font.bold = True
    
    doc.add_page_break()


# ===== 3. 正文 =====
def add_introduction(doc):
    """第1章 引言"""
    add_heading_custom(doc, '第1章 引言', level=1)
    
    add_heading_custom(doc, '1.1 编写目的', level=2)
    add_para(doc, '本文档为"教室预约与使用登记系统"的软件实践说明书，旨在完整、系统地描述项目的需求分析、设计方案、实现细节及测试结果。本文档既是项目开发过程的总结记录，也是后续维护与扩展的重要参考依据。')
    
    add_heading_custom(doc, '1.2 项目背景', level=2)
    add_para(doc, '随着高校教学资源日益紧张，教室调度与使用管理逐渐成为教务管理中的重要环节。传统的教室预约方式（如纸质登记或线下口头通知）存在效率低下、信息不透明、易冲突等问题。本系统通过信息化手段，为学生、教师和管理员提供统一的教室预约、审批和使用登记平台，实现教室资源的可视化管理和全流程闭环追踪。')
    
    add_heading_custom(doc, '1.3 术语定义', level=2)
    add_table_with_header(doc,
        ['术语', '说明'],
        [
            ['JWT', 'JSON Web Token，一种基于 Token 的无状态认证方案'],
            ['BCrypt', '一种自适应的密码哈希算法，内置盐值'],
            ['CRUD', 'Create、Read、Update、Delete，增删改查'],
            ['B/S', 'Browser/Server，浏览器/服务器架构'],
            ['Redis', '内存键值数据库，用于缓存和会话管理'],
            ['Pinia', 'Vue 3 官方推荐的状态管理库'],
            ['MyBatis', '半自动 ORM 框架，SQL 可控性强'],
        ]
    )
    
    add_heading_custom(doc, '1.4 参考资料', level=2)
    refs = [
        '[1] 软件工程实践课程指导书',
        '[2] Vue 3 官方文档 https://vuejs.org/',
        '[3] Spring Boot 3 官方文档 https://spring.io/projects/spring-boot',
        '[4] Element Plus 组件库文档 https://element-plus.org/',
        '[5] MyBatis 官方文档 https://mybatis.org/mybatis-3/',
        '[6] MySQL 8.0 参考手册 https://dev.mysql.com/doc/refman/8.0/',
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = LINE_SPACING
        run = p.add_run(r)
        run.font.name = FONT_NAME
        run.font.size = FONT_SIZE_BODY
        run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)


def add_requirements(doc):
    """第2章 系统需求分析"""
    add_heading_custom(doc, '第2章 系统需求分析', level=1)
    
    add_heading_custom(doc, '2.1 系统定位与业务价值', level=2)
    add_para(doc, '本系统面向高校教室资源管理场景，提供教室预约、审批流程、使用登记（签到/签退 + 设备状况填报）一体化的 Web 解决方案。目标用户包括学生、教师、管理员三类角色，通过 B/S 架构实现浏览器访问。')
    
    add_heading_custom(doc, '2.2 用户角色与权限', level=2)
    
    add_heading_custom(doc, '2.2.1 角色定义', level=3)
    add_table_with_header(doc,
        ['角色代码', '名称', '说明'],
        [
            ['STUDENT', '学生', '发起预约、签到签退、查看本人记录'],
            ['TEACHER', '教师', '同学生权限，可预约教学用教室'],
            ['ADMIN', '管理员', '审批预约、管理教室与用户、查看全系统数据'],
        ]
    )
    
    add_heading_custom(doc, '2.2.2 权限矩阵', level=3)
    add_table_with_header(doc,
        ['功能模块', '学生', '教师', '管理员'],
        [
            ['登录/登出', '✓', '✓', '✓'],
            ['个人中心', '✓', '✓', '✓'],
            ['教室浏览（只读）', '✓', '✓', '✓'],
            ['教室预约发起', '✓', '✓', '—'],
            ['我的预约查看', '✓', '✓', '—'],
            ['取消本人预约', '✓', '✓', '—'],
            ['签到登记', '✓', '✓', '—'],
            ['签退登记 + 设备状况', '✓', '✓', '—'],
            ['查看本人使用登记', '✓', '✓', '—'],
            ['审批中心', '—', '—', '✓'],
            ['教室管理（增删改）', '—', '—', '✓'],
            ['用户管理（增删改）', '—', '—', '✓'],
            ['系统概览/数据统计', '—', '—', '✓'],
            ['查看全部使用登记', '—', '—', '✓'],
        ]
    )
    
    add_heading_custom(doc, '2.3 功能需求', level=2)
    
    add_heading_custom(doc, '2.3.1 认证模块', level=3)
    add_para(doc, '登录：用户输入用户名和密码，后端通过 BCrypt 比对密码，验证通过后生成 JWT Token 返回前端。前端将 Token 存储在 localStorage 中，后续请求自动携带。')
    add_para(doc, '登出：清除本地 Token 与用户信息，调用后端登出接口删除 Redis 中的 Token 记录。')
    
    add_heading_custom(doc, '2.3.2 教室模块', level=3)
    add_para(doc, '学生/教师可浏览教室列表，支持按关键词、类型、状态筛选。管理员可新增、编辑、删除教室，并可切换教室状态（可用/维护中/停用）。')
    
    add_heading_custom(doc, '2.3.3 预约模块', level=3)
    add_para(doc, '学生/教师可发起教室预约，填写预约主题、起止时间、使用目的等信息。后端进行参数校验、时间冲突检测、容量校验。提交后预约状态为"待审批"，等待管理员审核。')
    add_para(doc, '预约状态流转：PENDING（待审批）→ APPROVED（已通过）/ REJECTED（已驳回）→ COMPLETED（已完成），或 PENDING → CANCELLED（已取消）。')
    
    add_heading_custom(doc, '2.3.4 审批模块', level=3)
    add_para(doc, '管理员可查看待审批列表，对预约执行"通过"或"驳回"操作。驳回时必须填写驳回原因。审批操作记录审批人和审批时间。')
    
    add_heading_custom(doc, '2.3.5 使用登记模块', level=3)
    add_para(doc, '预约通过后，用户可在预约开始时间前签到，使用结束后签退。签退时需填写实际人数、设备状况描述、卫生评分等信息。')
    
    add_heading_custom(doc, '2.3.6 系统管理与统计', level=3)
    add_para(doc, '管理员可管理用户账号（增删改）和教室信息。仪表盘展示教室总数、可用教室、待审批数、预约状态分布饼图、教室状态分布柱状图等统计指标。')
    
    add_heading_custom(doc, '2.4 非功能需求', level=2)
    
    add_table_with_header(doc,
        ['类别', '要求'],
        [
            ['性能', '首屏加载 ≤ 2s；列表分页接口响应 ≤ 500ms；路由切换 ≤ 300ms'],
            ['安全', '密码 BCrypt 加盐哈希存储；JWT Token 有效期 24h；所有写操作需后端二次校验'],
            ['可用性', '玻璃拟态视觉风格；关键操作动效反馈；空状态/加载状态视觉提示'],
            ['可维护性', '前端 SCSS 变量集中管理；后端分层清晰；枚举类集中定义'],
            ['兼容性', 'Chrome/Edge/Firefox/Safari 主流版本；MySQL 8.0+；Redis 6+'],
        ]
    )
    
    add_heading_custom(doc, '2.5 数据模型需求', level=2)
    add_para(doc, '系统包含 4 张核心数据表：classroom（教室表）、sys_user（用户表）、reservation（预约表）、usage_log（使用登记表）。各表通过外键关联，完整覆盖教室资源、用户身份、预约流程、使用记录四类核心数据。')


def add_design(doc):
    """第3章 系统概要设计"""
    add_heading_custom(doc, '第3章 系统概要设计', level=1)
    
    add_heading_custom(doc, '3.1 系统架构设计', level=2)
    add_para(doc, '本系统采用前后端分离的 B/S 架构。前端通过 Vite 构建的 Vue 3 应用提供用户界面，通过 HTTP 请求与后端 RESTful API 交互。后端采用 Spring Boot 3 框架，通过 MyBatis 访问 MySQL 数据库，使用 Redis 缓存 JWT Token 实现会话管理。JwtAuthInterceptor 拦截器统一处理认证鉴权。')
    
    add_heading_custom(doc, '3.2 技术路线', level=2)
    add_table_with_header(doc,
        ['层次', '技术选型', '版本', '说明'],
        [
            ['前端框架', 'Vue', '3.2.x', '渐进式 JavaScript 框架'],
            ['前端构建', 'Vite', '5.x', '下一代前端构建工具'],
            ['UI 组件库', 'Element Plus', '2.x', '基于 Vue 3 的组件库'],
            ['状态管理', 'Pinia', '2.x', 'Vue 官方推荐'],
            ['HTTP 客户端', 'Axios', '1.x', '拦截器统一鉴权/错误'],
            ['图表', 'ECharts', '5.x', '数据可视化'],
            ['后端框架', 'Spring Boot', '3.2.5', 'Java 企业级框架'],
            ['持久层', 'MyBatis', '3.x', '半自动 ORM'],
            ['数据库', 'MySQL', '8.0+', '关系型数据库'],
            ['缓存', 'Redis', '6+', 'JWT Token 存储'],
            ['认证', 'JWT (JJWT)', '0.12.5', '无状态 Token 认证'],
            ['密码加密', 'BCrypt', '—', 'Spring Security Crypto'],
            ['API 文档', 'SpringDoc', '2.3.0', 'Swagger 3.0'],
        ]
    )
    
    add_heading_custom(doc, '3.3 模块划分', level=2)
    add_para(doc, '系统按业务职责划分为 7 个功能模块：用户认证模块、教室管理模块、预约管理模块、审批管理模块、使用登记模块、概览统计模块、用户管理模块。各模块职责明确，通过 Controller-Service-Mapper 三层架构实现业务逻辑。')
    
    add_table_with_header(doc,
        ['模块', '功能说明', '可访问角色'],
        [
            ['用户认证', '登录、登出、获取用户信息', '全部'],
            ['教室管理', '教室列表、详情、增删改、状态变更', '管理员增删改，其他查'],
            ['预约管理', '创建预约、我的预约、取消预约', '全部'],
            ['审批管理', '待审批列表、通过/驳回审批', '仅管理员'],
            ['使用登记', '签到、签退、使用记录列表', '全部'],
            ['概览统计', '首页统计卡片、图表展示', '全部'],
            ['用户管理', '用户 CRUD、修改密码', '仅管理员'],
        ]
    )
    
    add_heading_custom(doc, '3.4 接口规范', level=2)
    add_para(doc, '统一响应格式：{ code: 200, success: true, message: "操作成功", data: {...} }。分页响应格式：{ records: [], total: 100, page: 1, pageSize: 10 }。')
    
    add_table_with_header(doc,
        ['HTTP 状态码', 'code', '说明'],
        [
            ['200', '200', '成功'],
            ['400', '400', '请求参数错误'],
            ['401', '401', '未登录/Token 无效'],
            ['403', '403', '无权限/账号被禁用'],
            ['404', '404', '资源不存在'],
            ['500', '500', '系统内部错误'],
        ]
    )


def add_detail_design(doc):
    """第4章 系统详细设计"""
    add_heading_custom(doc, '第4章 系统详细设计', level=1)
    
    add_heading_custom(doc, '4.1 数据库设计', level=2)
    
    add_heading_custom(doc, '4.1.1 classroom（教室表）', level=3)
    add_table_with_header(doc,
        ['字段', '类型', '约束', '说明'],
        [
            ['id', 'BIGINT', 'PRIMARY KEY AUTO_INCREMENT', '教室编号'],
            ['name', 'VARCHAR(50)', 'NOT NULL', '教室名称，如 A201'],
            ['building', 'VARCHAR(50)', 'NOT NULL', '楼栋'],
            ['floor', 'INT', '', '楼层'],
            ['capacity', 'INT', 'NOT NULL', '容纳人数'],
            ['type', 'VARCHAR(20)', 'NOT NULL', 'MULTIMEDIA/COMPUTER/LAB/NORMAL'],
            ['equipment', 'VARCHAR(200)', '', '设备描述'],
            ['status', 'VARCHAR(20)', 'NOT NULL DEFAULT AVAILABLE', '状态'],
            ['image_url', 'VARCHAR(255)', '', '图片 URL'],
            ['remark', 'VARCHAR(200)', '', '备注'],
            ['created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP', '创建时间'],
            ['updated_at', 'DATETIME', 'ON UPDATE CURRENT_TIMESTAMP', '更新时间'],
        ]
    )
    
    add_heading_custom(doc, '4.1.2 sys_user（用户表）', level=3)
    add_table_with_header(doc,
        ['字段', '类型', '约束', '说明'],
        [
            ['id', 'BIGINT', 'PRIMARY KEY AUTO_INCREMENT', '用户编号'],
            ['username', 'VARCHAR(30)', 'NOT NULL UNIQUE', '登录账号'],
            ['password', 'VARCHAR(100)', 'NOT NULL', '密码（BCrypt 加密）'],
            ['name', 'VARCHAR(30)', 'NOT NULL', '真实姓名'],
            ['role', 'VARCHAR(20)', 'NOT NULL', 'ADMIN/TEACHER/STUDENT'],
            ['department', 'VARCHAR(50)', '', '院系'],
            ['phone', 'VARCHAR(20)', '', '手机号'],
            ['email', 'VARCHAR(50)', '', '邮箱'],
            ['avatar', 'VARCHAR(255)', '', '头像 URL'],
            ['status', 'TINYINT(1)', 'NOT NULL DEFAULT 1', '1 启用 / 0 禁用'],
            ['created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP', '创建时间'],
            ['updated_at', 'DATETIME', 'ON UPDATE CURRENT_TIMESTAMP', '更新时间'],
        ]
    )
    
    add_heading_custom(doc, '4.1.3 reservation（预约表）', level=3)
    add_table_with_header(doc,
        ['字段', '类型', '约束', '说明'],
        [
            ['id', 'BIGINT', 'PRIMARY KEY AUTO_INCREMENT', '预约编号'],
            ['classroom_id', 'BIGINT', 'NOT NULL FK', '教室 ID'],
            ['user_id', 'BIGINT', 'NOT NULL FK', '预约人 ID'],
            ['title', 'VARCHAR(100)', 'NOT NULL', '预约主题'],
            ['purpose', 'VARCHAR(300)', '', '使用目的'],
            ['start_time', 'DATETIME', 'NOT NULL', '开始时间'],
            ['end_time', 'DATETIME', 'NOT NULL', '结束时间'],
            ['attendees', 'INT', '', '预计人数'],
            ['status', 'VARCHAR(20)', 'NOT NULL DEFAULT PENDING', '预约状态'],
            ['approver_id', 'BIGINT', 'FK', '审批人 ID'],
            ['approve_time', 'DATETIME', '', '审批时间'],
            ['reject_reason', 'VARCHAR(200)', '', '驳回原因'],
            ['cancel_reason', 'VARCHAR(200)', '', '取消原因'],
            ['created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP', '创建时间'],
            ['updated_at', 'DATETIME', 'ON UPDATE CURRENT_TIMESTAMP', '更新时间'],
        ]
    )
    
    add_heading_custom(doc, '4.1.4 usage_log（使用登记表）', level=3)
    add_table_with_header(doc,
        ['字段', '类型', '约束', '说明'],
        [
            ['id', 'BIGINT', 'PRIMARY KEY AUTO_INCREMENT', '登记编号'],
            ['reservation_id', 'BIGINT', 'NOT NULL FK', '关联预约 ID'],
            ['classroom_id', 'BIGINT', 'NOT NULL FK', '教室 ID'],
            ['user_id', 'BIGINT', 'NOT NULL FK', '登记人 ID'],
            ['check_in_time', 'DATETIME', '', '签到时间'],
            ['check_out_time', 'DATETIME', '', '签退时间'],
            ['actual_attendees', 'INT', '', '实际参会人数'],
            ['equipment_status', 'VARCHAR(200)', '', '设备状况'],
            ['cleanliness', 'TINYINT', '', '卫生评分 1-5'],
            ['notes', 'VARCHAR(300)', '', '备注'],
            ['created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP', '创建时间'],
            ['updated_at', 'DATETIME', 'ON UPDATE CURRENT_TIMESTAMP', '更新时间'],
        ]
    )
    
    add_heading_custom(doc, '4.2 认证模块详细设计', level=2)
    add_para(doc, '认证模块采用 JWT + Redis 方案。登录时，后端验证用户名密码（BCrypt 比对），验证通过后生成 JWT Token，将 Token 存入 Redis（key 格式：jwt:userId:token，有效期 24 小时），返回给前端。后续请求通过 JwtAuthInterceptor 拦截器统一处理：检查 Authorization Header → 提取 JWT → 验证签名 → Redis 校验 Token 是否存在 → 解析用户信息 → 注入 request 属性 → 放行。登出时删除 Redis 中对应的 Token。')
    
    add_heading_custom(doc, '4.3 预约模块详细设计', level=2)
    add_para(doc, '预约创建流程依次执行：参数校验 → 教室存在检查 → 教室状态检查 → 时间合法性校验（结束 > 开始 > 当前时间）→ 容量校验 → 冲突检测（查询同教室同时段有效预约）→ 创建预约（status = PENDING）。预约状态机定义了合法的状态流转：PENDING 可转为 APPROVED/REJECTED/CANCELLED，APPROVED 可转为 COMPLETED/CANCELLED。Service 层在状态变更前校验是否符合状态机规则。')
    
    add_heading_custom(doc, '4.4 审批模块详细设计', level=2)
    add_para(doc, '审批模块仅限管理员访问。审批通过：校验预约存在且状态为 PENDING → 更新 status 为 APPROVED → 记录 approverId 和 approveTime。审批驳回：校验预约存在且状态为 PENDING → 校验 rejectReason 非空 → 更新 status 为 REJECTED → 记录驳回原因和审批人/时间。')
    
    add_heading_custom(doc, '4.5 使用登记模块详细设计', level=2)
    add_para(doc, '签到流程：校验预约存在且状态为 APPROVED → 校验未重复签到（查询 usage_log 中是否已有记录）→ 校验预约未结束（startTime ≤ 当前时间 ≤ endTime + 缓冲）→ 创建 UsageLog 记录，设置 checkInTime。签退流程：校验预约和 UsageLog 存在 → 填写实际人数、设备状况、卫生评分 → 更新 UsageLog → 将预约状态更新为 COMPLETED。')
    
    add_heading_custom(doc, '4.6 前端路由与页面设计', level=2)
    
    add_table_with_header(doc,
        ['路径', '页面', '角色限制', '说明'],
        [
            ['/login', '登录页', '公共', '粒子背景 + 角色快捷账号'],
            ['/dashboard', '概览', 'ADMIN', '统计卡片 + ECharts 图表'],
            ['/classrooms', '教室预约', 'STUDENT/TEACHER', '3D 卡片网格展示'],
            ['/reservations', '我的预约', 'STUDENT/TEACHER', '状态指示灯 + 签到签退入口'],
            ['/usage', '使用登记', 'ALL', '签到/签退弹窗 + 记录列表'],
            ['/approvals', '审批中心', 'ADMIN', '待审批列表 + 通过/驳回操作'],
            ['/system', '系统管理', 'ADMIN', '教室 Tab + 用户 Tab'],
            ['/profile', '个人中心', 'ALL', '资料修改 + 密码修改'],
        ]
    )


def add_implementation(doc):
    """第5章 系统实现"""
    add_heading_custom(doc, '第5章 系统实现', level=1)
    
    add_heading_custom(doc, '5.1 开发环境', level=2)
    add_table_with_header(doc,
        ['项目', '配置'],
        [
            ['操作系统', 'Windows 11'],
            ['JDK', '17'],
            ['Node.js', '18+'],
            ['MySQL', '8.0+'],
            ['Redis', '7'],
            ['Maven', '3.9+'],
            ['IDE', 'IntelliJ IDEA / VS Code'],
            ['版本控制', 'Git'],
        ]
    )
    
    add_heading_custom(doc, '5.2 后端核心实现', level=2)
    
    add_heading_custom(doc, '5.2.1 项目结构', level=3)
    add_para(doc, '后端采用 Spring Boot 3 分层架构，主要包结构如下：')
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = LINE_SPACING
    code_text = '''backend/src/main/java/com/classroom/reservation/
├── common/          # 通用响应 Result、常量、枚举
├── config/          # 跨域、Redis、Jackson、Swagger 配置
├── controller/      # 7 个 Controller
├── dto/             # 请求/响应 DTO
├── entity/          # 4 个实体类
├── enums/           # 枚举定义
├── exception/       # 全局异常处理器
├── mapper/          # MyBatis 接口
├── security/        # JwtAuthInterceptor 拦截器
├── service/ + impl/ # 业务层接口与实现
└── utils/           # JwtUtil 等工具类'''
    run = p.add_run(code_text)
    run.font.name = 'Consolas'
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    
    add_heading_custom(doc, '5.2.2 统一返回格式', level=3)
    add_para(doc, '所有接口统一返回 Result<T> 对象，包含 code（状态码）、success（布尔值）、message（提示信息）、data（业务数据）四个字段。异常时由 GlobalExceptionHandler 统一捕获并返回标准错误响应。')
    
    add_heading_custom(doc, '5.2.3 JWT 认证实现', level=3)
    add_para(doc, 'JwtUtil 工具类负责 Token 的生成和验证，使用 HS384 算法签名。JwtAuthInterceptor 作为 Spring MVC 拦截器，在 preHandle 方法中完成：白名单路径放行 → 提取 Authorization Header → 验证 JWT 签名 → Redis 校验 Token 存在性 → 解析 userId/role → 注入 request 属性。登出时通过 AuthController.logout 删除 Redis 中的 Token。')
    
    add_heading_custom(doc, '5.2.4 全局异常处理', level=3)
    add_para(doc, 'GlobalExceptionHandler 使用 @ControllerAdvice 注解，处理两类异常：BusinessException（业务异常，如时间冲突、教室不存在）和 MethodArgumentNotValidException（参数校验异常）。所有异常均返回 Result 格式的错误响应，不泄露堆栈信息。')
    
    add_heading_custom(doc, '5.3 前端核心实现', level=2)
    
    add_heading_custom(doc, '5.3.1 项目结构', level=3)
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = LINE_SPACING
    code_text = '''frontend/src/
├── api/             # Axios 封装 + 接口定义
├── components/      # 通用组件（StatCard 等）
├── layouts/         # MainLayout 主布局
├── router/          # 路由配置 + 守卫
├── stores/          # Pinia user store
├── styles/          # variables.scss + global.scss
├── utils/           # 工具函数
└── views/           # 8 个页面组件'''
    run = p.add_run(code_text)
    run.font.name = 'Consolas'
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    
    add_heading_custom(doc, '5.3.2 路由守卫与角色控制', level=3)
    add_para(doc, 'Vue Router 的 beforeEach 全局守卫实现访问控制：未登录用户访问受保护路由时重定向至 /login；已登录用户无权限访问的路径返回 403 或重定向至首页。Pinia user store 存储当前用户信息和登录状态，通过 localStorage 持久化。')
    
    add_heading_custom(doc, '5.3.3 Axios 拦截器', level=3)
    add_para(doc, '请求拦截器自动在 Header 中注入 Authorization: Bearer {token}。响应拦截器统一处理错误：401 时清除登录状态并跳转登录页，其他错误通过 ElMessage 展示提示。')
    
    add_heading_custom(doc, '5.3.4 设计系统', level=3)
    add_para(doc, '前端采用玻璃拟态（Glassmorphism）视觉风格，通过 SCSS 变量集中管理颜色、阴影、圆角、动画曲线。主色采用靛蓝紫渐变，状态色（绿/琥珀/红/蓝/灰）统一规范。Element Plus 组件库进行了样式定制，按钮使用渐变背景，表格行有错位入场动画。')
    
    add_heading_custom(doc, '5.4 数据库实现', level=2)
    add_para(doc, '数据库名：classroom_reservation，字符集 utf8mb4。4 张表均使用 InnoDB 引擎，设置了合理的索引：')
    add_table_with_header(doc,
        ['表名', '索引名', '字段', '说明'],
        [
            ['classroom', 'idx_building_floor', 'building, floor', '楼栋楼层联合查询'],
            ['classroom', 'idx_status_type', 'status, type', '状态类型联合筛选'],
            ['sys_user', 'idx_role', 'role', '角色筛选'],
            ['reservation', 'idx_status', 'status', '状态筛选'],
            ['reservation', 'idx_user_classroom', 'user_id, classroom_id', '用户教室联合查询'],
            ['reservation', 'idx_time_range', 'start_time, end_time', '时间范围查询'],
            ['usage_log', 'idx_reservation', 'reservation_id', '预约关联查询'],
            ['usage_log', 'idx_classroom_time', 'classroom_id, check_in_time', '教室时间联合查询'],
        ]
    )
    
    add_para(doc, '初始数据包含 6 间教室、3 个用户、4 条预约、1 条使用登记，用于系统演示和冒烟测试。')
    
    add_heading_custom(doc, '5.5 界面展示', level=2)
    add_para(doc, '系统包含以下主要界面：登录页（粒子背景 + 角色快捷账号）、主布局（可折叠侧边栏 + 顶部栏 + 面包屑 + 实时时钟）、概览仪表盘（统计卡片 + ECharts 饼图/柱状图）、教室列表页（3D 倾斜卡片网格）、我的预约页（状态指示灯 + 签到签退弹窗）、审批中心（待审批列表 + 通过/驳回操作）、系统管理（教室管理 Tab + 用户管理 Tab）、使用登记列表（签到/签退图标 + 卫生评分 + 设备状况分类）、个人中心（资料修改 + 密码修改）。')


def add_testing(doc):
    """第6章 系统测试及结果"""
    add_heading_custom(doc, '第6章 系统测试及结果', level=1)
    
    add_heading_custom(doc, '6.1 测试环境', level=2)
    add_table_with_header(doc,
        ['项目', '配置'],
        [
            ['操作系统', 'Windows 11'],
            ['JDK', '17'],
            ['Spring Boot', '3.2.5'],
            ['数据库', 'MySQL 8.0'],
            ['缓存', 'Redis 7'],
            ['构建工具', 'Maven 3.9'],
            ['测试框架', 'JUnit 5 + Spring Boot Test + MockMvc'],
        ]
    )
    
    add_heading_custom(doc, '6.2 自动化测试', level=2)
    add_para(doc, '共执行 29 个自动化测试用例，全部通过。测试覆盖率核心业务接口和状态流转逻辑。')
    
    add_table_with_header(doc,
        ['测试类', '用例数', '通过', '失败', '说明'],
        [
            ['ReservationIntegrationTest', '10', '10', '0', 'MockMvc 接口集成测试'],
            ['ReservationStatusTest', '12', '12', '0', '预约状态枚举单元测试'],
            ['QueryDtoNormalizeTest', '7', '7', '0', 'DTO 参数归一化单元测试'],
            ['合计', '29', '29', '0', '—'],
        ]
    )
    
    add_heading_custom(doc, '6.3 手工功能测试', level=2)
    add_para(doc, '依据《测试条件清单》共设计 54 个测试用例，覆盖正常、异常和边界场景。核心测试场景包括：')
    
    scenarios = [
        '登录认证：正确账号密码登录成功、错误密码提示友好、未登录访问受保护路由重定向、登出后 Token 清除',
        '教室查询：关键词筛选、类型筛选、状态筛选、分页功能',
        '预约创建：必填项校验、时间合法性校验、教室状态校验、容量校验、时间冲突检测',
        '预约状态流转：PENDING → APPROVED / REJECTED、APPROVED → COMPLETED / CANCELLED、非法状态流转拦截',
        '审批：通过后状态变更、驳回需填写原因、仅 PENDING 可审批',
        '使用登记：签到校验、重复签到拦截、签退更新状态',
        '权限控制：学生/教师无法访问管理员接口、无权限返回 403',
    ]
    for i, s in enumerate(scenarios):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = LINE_SPACING
        run = p.add_run(f'（{chr(ord("1")+i)}）{s}')
        run.font.name = FONT_NAME
        run.font.size = FONT_SIZE_BODY
        run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)
    
    add_heading_custom(doc, '6.4 缺陷分析与修复', level=2)
    
    add_table_with_header(doc,
        ['编号', '缺陷描述', '严重程度', '修复方式'],
        [
            ['BUG-001', '教室列表缺少最小容量筛选条件', '中', 'ClassroomQueryDTO 新增 minCapacity 字段'],
            ['BUG-002', '取消预约未校验预约是否已开始', '高', 'cancel 方法增加 startTime > now 校验'],
            ['BUG-003', '取消预约允许 PENDING 状态，与指导书不符', '中', '状态校验改为仅 APPROVED 可取消'],
            ['BUG-004', '缺少按日期时段查询空闲教室接口', '高', '新增 GET /api/classrooms/available'],
            ['BUG-005', '缺少教室使用率和按周统计', '低', '新增统计接口'],
            ['BUG-006', '缺少批量预约功能', '低', '新增 POST /api/reservations/batch'],
            ['BUG-007', '缺少爽约标记查询', '低', '新增 GET /api/reservations/no-shows'],
        ]
    )
    
    add_heading_custom(doc, '6.5 测试结论', level=2)
    add_para(doc, '核心业务闭环完整：预约 → 审核 → 签到 → 签退全流程功能正常，业务规则校验到位。异常处理完善：时间冲突、超容量、权限不足、状态非法等场景均有明确错误提示。自动化测试覆盖核心接口和状态流转。系统功能满足指导书要求，可进入交付阶段。')


def add_conclusion(doc):
    """第7章 结论"""
    add_heading_custom(doc, '第7章 结论', level=1)
    
    add_heading_custom(doc, '7.1 完成情况总结', level=2)
    add_para(doc, '本项目按计划完成了全部功能开发和测试工作。系统覆盖 7 大功能模块、4 张数据表、20+ 个 API 接口，实现了从教室浏览、预约提交、管理员审批到签到签退使用登记的完整业务闭环。具体完成情况：')
    
    completions = [
        '后端：Spring Boot 3 + MyBatis 分层架构，JWT + Redis 认证方案，全局异常处理，统一返回格式，Swagger 接口文档',
        '前端：Vue 3 + Element Plus + Pinia，玻璃拟态设计风格，路由守卫权限控制，ECharts 数据可视化，三角色差异化界面',
        '数据库：4 张核心表，合理索引，初始数据完备',
        '测试：29 个自动化测试用例全部通过，54 个手工功能测试用例覆盖核心场景',
        '文档：需求文档、设计文档、测试报告、部署文档齐全',
    ]
    for i, c in enumerate(completions):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = LINE_SPACING
        run = p.add_run(f'（{chr(ord("1")+i)}）{c}')
        run.font.name = FONT_NAME
        run.font.size = FONT_SIZE_BODY
        run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)
    
    add_heading_custom(doc, '7.2 不足与展望', level=2)
    add_para(doc, '由于时间和经验限制，系统仍有以下可改进之处：')
    
    shortcomings = [
        '教室图片上传功能尚未启用（image_url 字段已预留）',
        '缺少预约日历视图（按日历展示预约分布）',
        '缺少消息通知功能（预约审批结果推送）',
        '缺少数据导出功能（预约/使用登记 Excel 导出）',
        '移动端适配尚不完善，目前以桌面端为主',
        '操作日志审计功能待补充',
    ]
    for s in shortcomings:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = LINE_SPACING
        run = p.add_run(f'• {s}')
        run.font.name = FONT_NAME
        run.font.size = FONT_SIZE_BODY
        run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)


def add_references(doc):
    """参考文献"""
    h = add_heading_custom(doc, '参考文献', level=1)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    refs = [
        '[1] 萨师煊, 王珊. 数据库系统概论(第5版)[M]. 高等教育出版社, 2014.',
        '[2] 张海藩. 软件工程导论(第6版)[M]. 清华大学出版社, 2013.',
        '[3] 陈天. Vue.js设计与实现[M]. 人民邮电出版社, 2022.',
        '[4] 王磊. Spring Boot实战[M]. 人民邮电出版社, 2016.',
        '[5] Vue.js 官方文档. https://vuejs.org/',
        '[6] Spring Boot 官方文档. https://spring.io/projects/spring-boot',
        '[7] MyBatis 官方文档. https://mybatis.org/mybatis-3/',
        '[8] MySQL 8.0 参考手册. https://dev.mysql.com/doc/refman/8.0/',
        '[9] Element Plus 组件库文档. https://element-plus.org/',
        '[10] SpringDoc OpenAPI 文档. https://springdoc.org/',
    ]
    for i, r in enumerate(refs):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = LINE_SPACING
        p.paragraph_format.left_indent = Cm(0.74)
        run = p.add_run(r)
        run.font.name = FONT_NAME
        run.font.size = FONT_SIZE_BODY
        run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)


def add_acknowledgement(doc):
    """致谢"""
    h = add_heading_custom(doc, '致谢', level=1)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    add_para(doc, '本次软件工程实践课程项目能够顺利完成，离不开指导老师张淑娟和王亚恒的悉心指导和帮助。在项目开发过程中，两位老师在需求分析、架构设计、技术选型和代码规范等方面给予了宝贵的建议。')
    
    add_para(doc, '同时，感谢小组全体成员的精诚合作。在近两个月的开发周期中，大家分工明确、协作有序，共同克服了技术难点和协作困难。冯翌轩负责后端架构设计和认证授权实现，秦伟彪负责教室管理和使用登记模块，常锦相负责前端页面开发和图表实现，李育真负责数据库设计和文档整理，杨坤豫作为组长统筹全局并负责前端架构和部署工作。正是每个人的认真投入，才保证了项目的按时交付。')
    
    add_para(doc, '最后，感谢开源社区提供的优秀技术框架和工具，让我们能够在有限时间内完成这样一个完整的 Web 应用系统。')


# ===== 个人开发日志 =====
def generate_individual_logs(output_dir):
    """生成5份个人开发日志"""
    
    logs = {
        '2413040818_冯翌轩': {
            'name': '冯翌轩',
            'student_id': '2413040818',
            'duty': '后端整体架构、统一返回格式、全局异常、认证授权(JWT)、预约审批业务',
            'sections': [
                ('负责内容', 
                 '本次实践中，我主要负责后端整体架构设计和核心业务模块实现，具体包括：\n'
                 '（1）后端项目骨架搭建，配置 pom.xml 依赖（Spring Boot 3.2.5、MyBatis、JJWT、SpringDoc、Hutool、Lombok）\n'
                 '（2）统一返回格式 Result<T> 设计，包含 code、success、message、data 四字段\n'
                 '（3）全局异常处理器 GlobalExceptionHandler，统一捕获 BusinessException 和参数校验异常\n'
                 '（4）JWT 认证方案：JwtUtil 工具类、JwtAuthInterceptor 拦截器、Redis Token 存储\n'
                 '（5）预约审批业务：ApprovalController + ApprovalServiceImpl，实现通过和驳回接口'),
                ('模块设计实现',
                 '【统一返回格式】\n'
                 'Result<T> 泛型类提供静态工厂方法 success(T data)、success(String msg, T data)、error(int code, String msg)。所有 Controller 方法返回 Result 类型，异常由 GlobalExceptionHandler 统一拦截并包装为 Result 错误响应。\n\n'
                 '【JWT 认证方案】\n'
                 '采用 JWT + Redis 方案：登录时生成 HS384 签名的 Token，存入 Redis（key: jwt:userId:token）。JwtAuthInterceptor 在 preHandle 中依次执行：白名单检查 → OPTIONS 放行 → 提取 Authorization Header → JwtUtil.validateToken → Redis GET 校验 → 解析 userId/role → request.setAttribute 注入。\n\n'
                 '【审批业务】\n'
                 'ApprovalServiceImpl.approve(id, approverId)：查询预约 → 校验状态为 PENDING → 更新 status 为 APPROVED → 记录 approverId 和 approveTime。\n'
                 'ApprovalServiceImpl.reject(id, approverId, reason)：查询预约 → 校验状态为 PENDING → 校验 reason 非空 → 更新 status 为 REJECTED → 记录驳回原因。'),
                ('开发过程记录',
                 '• 第 1-2 天：搭建 Spring Boot 项目骨架，配置 pom.xml 和 application.yml\n'
                 '• 第 3-4 天：实现 Result 统一返回格式和 GlobalExceptionHandler\n'
                 '• 第 5-6 天：实现 JwtUtil 工具类，生成和验证 Token\n'
                 '• 第 7-8 天：实现 JwtAuthInterceptor 拦截器，配置 WebMvcConfigurer 注册\n'
                 '• 第 9-10 天：实现 AuthController 登录/登出接口，对接 Redis\n'
                 '• 第 11-12 天：实现 ApprovalController 和 ApprovalServiceImpl\n'
                 '• 第 13-14 天：接口测试，修复认证流程中的边界问题\n'
                 '• 第 15 天：协助组员联调前后端接口'),
                ('问题分析与解决',
                 '【问题1】JWT Token 在 Redis 中存储时，不同设备登录会互相覆盖\n'
                 '解决方案：Redis key 格式改为 jwt:userId:token，每次登录生成新 Token 并覆盖，保证同一用户只保留最新会话。登出时删除对应 key。\n\n'
                 '【问题2】拦截器放行白名单配置不完整，导致静态资源和 Swagger 页面被拦截\n'
                 '解决方案：白名单路径补充 /auth/**、/swagger-ui/**、/v3/api-docs/**、/doc.html、/webjars/**、/favicon.ico。\n\n'
                 '【问题3】审批接口未限制只有 PENDING 状态可审批，已完成的预约也能被驳回\n'
                 '解决方案：在 ApprovalServiceImpl 中增加状态校验，使用 ReservationStatus.canTransitTo() 枚举方法判断状态流转合法性。'),
                ('总结收获',
                 '通过本次实践，深入理解了 Spring Boot 分层架构的设计思路，掌握了 JWT + Redis 无状态认证的完整实现流程，学会了如何设计统一的返回格式和全局异常处理来提升 API 规范性。审批业务的状态机校验让我对业务规则的代码表达有了更清晰的认识。')
            ]
        },
        '2413040824_秦伟彪': {
            'name': '秦伟彪',
            'student_id': '2413040824',
            'duty': '教室CRUD、使用登记(签到签退)、用户管理、MyBatis Mapper SQL、Service实现',
            'sections': [
                ('负责内容',
                 '本次实践中，我主要负责教室管理、使用登记、用户管理三个模块的后端实现，具体包括：\n'
                 '（1）classroom、usage_log、sys_user 三张表的 MyBatis Mapper SQL 编写\n'
                 '（2）ClassroomServiceImpl：教室 CRUD、条件筛选查询、状态变更\n'
                 '（3）UsageLogServiceImpl：签到、签退、使用记录查询\n'
                 '（4）UserServiceImpl：用户 CRUD、修改密码、角色过滤\n'
                 '（5）ReservationServiceImpl：预约创建的冲突检测 SQL 和 Service 实现'),
                ('模块设计实现',
                 '【教室 Mapper SQL】\n'
                 'classroomMapper.selectPage 使用动态 SQL，支持 building、type、status、keyword 多条件筛选。keyword 使用 CONCAT("%", #{keyword}, "%") 对 name 和 building 同时模糊查询。\n\n'
                 '【签到流程】\n'
                 'UsageLogServiceImpl.checkIn(reservationId, userId)：查询预约 → 校验存在且状态为 APPROVED → 校验未重复签到（SELECT COUNT(*) FROM usage_log WHERE reservation_id = ?）→ 校验预约未结束 → 创建 UsageLog 设置 checkInTime。\n\n'
                 '【签退流程】\n'
                 'UsageLogServiceImpl.checkOut(dto, userId)：查询预约和 UsageLog → 校验已签到 → 更新 UsageLog 填写实际人数、设备状况、卫生评分 → 将预约状态更新为 COMPLETED。\n\n'
                 '【冲突检测 SQL】\n'
                 'reservationMapper.findConflicts：SELECT * FROM reservation WHERE classroom_id = #{classroomId} AND status IN ("PENDING","APPROVED") AND NOT(end_time <= #{startTime} OR start_time >= #{endTime})'),
                ('开发过程记录',
                 '• 第 1-2 天：编写 ClassroomMapper.xml、UsageLogMapper.xml、SysUserMapper.xml 基础 SQL\n'
                 '• 第 3-4 天：实现 ClassroomServiceImpl 和 ClassroomController\n'
                 '• 第 5-6 天：实现 UserServiceImpl 和 UserController\n'
                 '• 第 7-8 天：实现 ReservationServiceImpl，重点是时间冲突检测\n'
                 '• 第 9-10 天：实现 UsageLogServiceImpl 签到逻辑\n'
                 '• 第 11-12 天：实现签退逻辑，处理预约状态自动更新\n'
                 '• 第 13-14 天：完善 SQL 索引和性能优化\n'
                 '• 第 15 天：接口联调，配合前端测试'),
                ('问题分析与解决',
                 '【问题1】时间冲突检测 SQL 条件反了，导致部分冲突漏检\n'
                 '原始写法：start_time < #{endTime} AND end_time > #{startTime}，逻辑正确但索引未覆盖导致慢查询。\n'
                 '解决方案：使用 NOT(end_time <= #{startTime} OR start_time >= #{endTime}) 改写，配合 idx_time_range(start_time, end_time) 索引。\n\n'
                 '【问题2】签到未校验预约归属，A 用户可签到 B 用户的预约\n'
                 '解决方案：checkIn 方法增加 userId 校验，查询预约时同时检查 user_id = 当前登录用户。\n\n'
                 '【问题3】用户新增时密码未 BCrypt 加密，直接存入数据库\n'
                 '解决方案：在 UserServiceImpl.add 方法中，对 password 字段调用 BCryptPasswordEncoder.encode() 加密后再保存。'),
                ('总结收获',
                 '掌握了 MyBatis 动态 SQL 的编写技巧，理解了业务 Service 层如何协调多个 Mapper 完成复杂业务流程（如签退同时更新 usage_log 和 reservation 两张表）。学会了事务管理，确保多表操作的原子性。对数据库索引优化有了实践体会。')
            ]
        },
        '2413040831_常锦相': {
            'name': '常锦相',
            'student_id': '2413040831',
            'duty': '所有列表页、表单页、个人中心、系统管理、API对接、ECharts图表、表格交互',
            'sections': [
                ('负责内容',
                 '本次实践中，我主要负责前端页面开发，具体包括：\n'
                 '（1）教室列表页 ClassroomList.vue：卡片网格、3D 倾斜效果、筛选功能\n'
                 '（2）我的预约页 ReservationList.vue：状态筛选、签到签退弹窗、取消预约\n'
                 '（3）审批中心 ApprovalCenter.vue：待审批列表、通过/驳回操作、统计概览\n'
                 '（4）系统管理页 SystemManage.vue：教室管理 Tab + 用户管理 Tab\n'
                 '（5）使用登记页 UsageLogList.vue：记录列表、设备状况分类展示\n'
                 '（6）个人中心 Profile.vue：资料修改、密码修改、安全提示卡片\n'
                 '（7）ECharts 图表集成：仪表盘饼图、柱状图'),
                ('模块设计实现',
                 '【教室列表页】\n'
                 '采用 Element Plus 的 el-card 组件封装教室卡片，配合 CSS 3D transform 实现 hover 倾斜跟随效果。卡片包含教室图片区、状态徽章（el-tag）、类型标签、容量进度条（el-progress）、设备图标。快捷筛选 chip 使用 el-radio-group 实现全部/可用/维护中切换。\n\n'
                 '【审批中心】\n'
                 '顶部统计概览区展示待审批数、今日处理数、总记录数，使用数字滚动动画（requestAnimationFrame + easeOutCubic）。列表使用 el-table + 分页，每行展示预约人头像、预约主题、教室、时段、状态。通过/驳回操作使用 el-message-box 二次确认，驳回时弹出 el-dialog 填写原因。\n\n'
                 '【ECharts 图表】\n'
                 '使用 vue-echarts 组件，预约状态分布用饼图（pie + roseType），教室状态分布用柱状图（bar + gradient）。图表数据通过 /api/dashboard/stats 接口获取，使用 ref 响应式绑定 option。'),
                ('开发过程记录',
                 '• 第 1-2 天：完成教室列表页，实现卡片网格和筛选\n'
                 '• 第 3-4 天：完成我的预约页和预约提交弹窗\n'
                 '• 第 5-6 天：完成审批中心页面，含统计概览和审批操作\n'
                 '• 第 7-8 天：完成系统管理页两个 Tab（教室 CRUD + 用户 CRUD）\n'
                 '• 第 9-10 天：完成使用登记列表页和签退弹窗\n'
                 '• 第 11-12 天：完成个人中心页面\n'
                 '• 第 13-14 天：集成 ECharts 图表到仪表盘\n'
                 '• 第 15 天：页面优化和细节打磨'),
                ('问题分析与解决',
                 '【问题1】教室卡片 3D 倾斜效果在移动端触摸时触发异常\n'
                 '解决方案：增加判断，仅在 isPC 设备上监听 mousemove 事件，移动端禁用 3D 效果。\n\n'
                 '【问题2】审批中心列表分页后状态变化，重新请求时用户体验不流畅\n'
                 '解决方案：使用 Element Plus 的 el-table 的 row-key 和 reserve-selection 保持选中状态。审批操作成功后局部刷新当前页。\n\n'
                 '【问题3】ECharts 图表在路由切换后渲染错误\n'
                 '解决方案：在组件的 onBeforeUnmount 中调用 chart.dispose() 释放实例，使用 nextTick 确保容器存在后再初始化。'),
                ('总结收获',
                 '深入理解了 Vue 3 Composition API 的响应式编程模式，熟练掌握了 Element Plus 组件库的常用组件和自定义样式覆盖。学会了 ECharts 在 Vue 中的集成和动态数据更新。对前端交互设计（hover 动效、弹窗流程、表单校验）有了丰富的实践经验。')
            ]
        },
        '2413040835_杨坤豫': {
            'name': '杨坤豫',
            'student_id': '2413040835',
            'duty': '进度统筹、接口对齐、代码合并、部署上线、前端整体架构(路由/Pinia/主题)、登录页+主布局+三角色首页',
            'sections': [
                ('负责内容',
                 '作为组长，我负责项目进度统筹和前端架构设计，具体包括：\n'
                 '（1）项目计划制定和进度跟踪，每日站会协调\n'
                 '（2）前端整体架构：Vue Router 路由配置、Pinia 状态管理、设计系统搭建\n'
                 '（3）登录页 Login.vue：粒子背景、角色快捷账号、大写锁定提示\n'
                 '（4）主布局 MainLayout.vue：可折叠侧边栏、顶部栏、面包屑、实时时钟、全屏切换\n'
                 '（5）仪表盘 Dashboard.vue：统计卡片、ECharts 饼图柱状图、最近预约列表\n'
                 '（6）部署上线：前端 Vite 构建 + Nginx 托管、后端 Spring Boot 打包 + systemd\n'
                 '（7）代码合并和 Git 仓库管理'),
                ('模块设计实现',
                 '【路由设计】\n'
                 '采用懒加载（() => import）优化首屏，全局守卫 beforeEach 实现：未登录跳转 /login、无权限重定向、已登录访问 /login 跳转首页。路由 meta 字段配置 roles 数组，守卫中检查 userStore.role 是否在允许列表中。\n\n'
                 '【Pinia 用户状态管理】\n'
                 'user store 存储 token、userInfo（id/username/name/role/avatar）、isLoggedIn。提供 login/logout/actions，通过 localStorage 持久化（persist 插件）。登出时调用 actions.logout 清除 store 和 localStorage。\n\n'
                 '【登录页粒子背景】\n'
                 '使用 canvas 绘制粒子效果，粒子数 60、连线距离 120px、线宽 1px。用户登录后粒子画布销毁，释放资源。登录表单使用 Element Plus el-form + el-input + el-button。\n\n'
                 '【主布局】\n'
                 '侧边栏使用 el-menu，根据角色动态生成菜单项（v-if 或 computed 过滤）。顶部栏包含面包屑（el-breadcrumb）、实时时钟（setInterval + Date）、全屏切换（Fullscreen API）、用户下拉菜单（el-dropdown）。'),
                ('开发过程记录',
                 '• 第 1 天：制定项目开发计划，拆分 25 个任务项\n'
                 '• 第 2-3 天：完成前端项目骨架搭建，配置 Vite、路由、Pinia、Axios\n'
                 '• 第 4-5 天：实现登录页和主布局\n'
                 '• 第 6 天：完成仪表盘页面（统计卡片 + 图表）\n'
                 '• 第 7 天：配置 Git 仓库，建立分支管理规范\n'
                 '• 第 8-12 天：每日站会，协调成员开发，解决接口对齐问题\n'
                 '• 第 13-14 天：代码合并，解决分支冲突\n'
                 '• 第 15-16 天：联调测试，修复 Bug\n'
                 '• 第 17 天：部署上线（构建 + Nginx + systemd）\n'
                 '• 第 18 天：整理交付文档'),
                ('问题分析与解决',
                 '【问题1】路由守卫中 userStore 在刷新后未恢复，导致已登录用户被强制退出\n'
                 '解决方案：引入 pinia-plugin-persistedstate 插件，user store 的 token 和 userInfo 自动持久化到 localStorage。刷新时 store 从 localStorage 恢复状态。\n\n'
                 '【问题2】前端请求跨域，开发时需要配置代理\n'
                 '解决方案：Vite vite.config.js 中配置 server.proxy，将 /api 路径代理到 http://localhost:8080。生产环境通过 Nginx location 反向代理解决。\n\n'
                 '【问题3】代码合并时成员分支冲突频繁\n'
                 '解决方案：制定 Git 规范（main 保护 + feature 分支），每天定时手动 pull main 更新本地分支。使用 VS Code GitLens 辅助解决冲突。'),
                ('总结收获',
                 '通过组长角色锻炼了项目管理和团队协作能力，学会了如何制定开发计划、协调成员进度、处理代码合并冲突。前端架构设计方面，深入理解了 Vue 3 组合式 API、Pinia 状态管理、路由守卫权限控制的完整实现。部署上线让我掌握了 Spring Boot JAR 打包运行和 Vite 构建 + Nginx 托管的完整流程。')
            ]
        },
        '2413040841_李育真': {
            'name': '李育真',
            'student_id': '2413040841',
            'duty': '数据库建表、索引、初始数据SQL、前后端联调、Swagger接口验证、项目文档、部署文档',
            'sections': [
                ('负责内容',
                 '本次实践中，我主要负责数据库设计和项目文档，具体包括：\n'
                 '（1）数据库设计：4 张表结构设计、外键约束、索引策略\n'
                 '（2）初始数据 SQL：6 间教室、3 个用户、4 条预约、1 条使用登记\n'
                 '（3）Swagger 接口文档配置和验证\n'
                 '（4）前后端联调：逐接口测试，配合定位问题\n'
                 '（5）项目文档撰写：需求文档、系统设计文档、测试报告、部署文档'),
                ('模块设计实现',
                 '【数据库设计】\n'
                 '使用 DDL 语句创建 4 张表，字符集 utf8mb4，引擎 InnoDB。设计外键约束：reservation.classroom_id → classroom.id、reservation.user_id → sys_user.id、reservation.approver_id → sys_user.id、usage_log.reservation_id → reservation.id、usage_log.classroom_id → classroom.id、usage_log.user_id → sys_user.id。\n\n'
                 '【索引策略】\n'
                 'classroom 表：idx_building_floor(building, floor) 支持楼栋楼层联合查询；idx_status_type(status, type) 支持状态类型联合筛选。\n'
                 'reservation 表：idx_status(status) 支持状态筛选；idx_user_classroom(user_id, classroom_id) 支持用户教室联合查询；idx_time_range(start_time, end_time) 支持时间范围查询和冲突检测。\n\n'
                 '【Swagger 配置】\n'
                 'Spring Boot 3 使用 SpringDoc 替代旧版 SpringFox。pom.xml 引入 springdoc-openapi-starter-webmvc-ui。application.yml 配置 api-docs 和 swagger-ui 路径。接口上使用 @Operation、@Tag、@Schema 注解增强文档。'),
                ('开发过程记录',
                 '• 第 1 天：ER 图设计，确定 4 张表结构\n'
                 '• 第 2 天：编写 DDL 建表语句和外键约束\n'
                 '• 第 3 天：设计索引策略，编写 CREATE INDEX 语句\n'
                 '• 第 4 天：编写初始数据 INSERT 语句（教室、用户、预约、使用登记）\n'
                 '• 第 5 天：SpringDoc 配置和注解添加\n'
                 '• 第 6-7 天：需求文档撰写\n'
                 '• 第 8-9 天：系统设计文档撰写\n'
                 '• 第 10-12 天：前后端联调，逐接口验证\n'
                 '• 第 13-14 天：测试报告撰写，整理缺陷\n'
                 '• 第 15 天：部署文档整理'),
                ('问题分析与解决',
                 '【问题1】MySQL 外键约束导致删除教室时因存在关联预约而失败\n'
                 '解决方案：删除教室前先确认没有有效的关联预约（PENDING 或 APPROVED 状态）。已通过的预约保留历史记录，不影响教室删除。\n\n'
                 '【问题2】Spring Boot 3 不支持旧版 SpringFox Swagger\n'
                 '解决方案：替换为 SpringDoc OpenAPI（springdoc-openapi-starter-webmvc-ui），访问地址为 /swagger-ui/index.html。接口注解从 @Api/@ApiOperation 改为 @Tag/@Operation。\n\n'
                 '【问题3】初始数据中预约时间冲突\n'
                 '解决方案：重新梳理时间线，确保同一教室同时段只有一个有效预约。使用不同日期避免冲突。'),
                ('总结收获',
                 '掌握了完整的数据库设计流程：需求分析 → ER 建模 → 表结构设计 → 索引策略 → 初始数据。学会了如何为 Spring Boot 3 配置 API 文档工具。联调过程中深入理解了前后端数据交互的完整链路，对接口契约（请求参数、响应格式、错误码）有了清晰认识。文档撰写提升了技术表达能力。')
            ]
        }
    }
    
    for filename, data in logs.items():
        doc = Document()
        setup_document(doc)
        
        # 标题
        h = doc.add_heading(f'{data["name"]} 开发日志', level=0)
        h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in h.runs:
            run.font.name = FONT_NAME
            run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)
            run.font.size = Pt(26)
            run.font.bold = True
        
        doc.add_paragraph()
        
        # 基本信息
        info_items = [
            ('姓名', data['name']),
            ('学号', data['student_id']),
            ('组名', 'kskbl'),
            ('主要职责', data['duty']),
        ]
        for label, value in info_items:
            p = doc.add_paragraph()
            p.paragraph_format.line_spacing = LINE_SPACING
            run1 = p.add_run(f'{label}：')
            run1.font.name = FONT_NAME
            run1.font.size = FONT_SIZE_BODY
            run1.font.bold = True
            run1._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)
            run2 = p.add_run(value)
            run2.font.name = FONT_NAME
            run2.font.size = FONT_SIZE_BODY
            run2._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)
        
        doc.add_paragraph()
        
        # 各节内容
        for section_title, content in data['sections']:
            add_heading_custom(doc, section_title, level=2)
            
            # 按换行符分割段落
            paragraphs = content.split('\n')
            for para_text in paragraphs:
                para_text = para_text.strip()
                if not para_text:
                    doc.add_paragraph()
                    continue
                if para_text.startswith('【'):
                    p = doc.add_paragraph()
                    p.paragraph_format.first_line_indent = Cm(0.74)
                    p.paragraph_format.line_spacing = LINE_SPACING
                    run = p.add_run(para_text)
                    run.font.name = FONT_NAME
                    run.font.size = FONT_SIZE_BODY
                    run.font.bold = True
                    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)
                else:
                    add_para(doc, para_text)
        
        filepath = os.path.join(output_dir, f'{filename}.docx')
        doc.save(filepath)
        print(f'已生成：{filepath}')


# ===== 主函数 =====
def main():
    print('=== 开始生成最终项目文档 ===')
    
    output_dir = r'e:\教室预约与使用登记系统\项目文档'
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成主文档
    print('1. 生成最终项目文档.docx ...')
    doc = Document()
    setup_document(doc)
    
    add_cover(doc)
    add_toc(doc)
    add_introduction(doc)
    add_requirements(doc)
    add_design(doc)
    add_detail_design(doc)
    add_implementation(doc)
    add_testing(doc)
    add_conclusion(doc)
    add_references(doc)
    add_acknowledgement(doc)
    
    main_path = os.path.join(output_dir, '最终项目文档.docx')
    doc.save(main_path)
    print(f'   ✓ 已保存：{main_path}')
    
    # 生成个人开发日志
    print('\n2. 生成个人开发日志 ...')
    log_dir = os.path.join(output_dir, '个人开发日志')
    os.makedirs(log_dir, exist_ok=True)
    generate_individual_logs(log_dir)
    
    print('\n=== 全部完成 ===')


if __name__ == '__main__':
    main()
