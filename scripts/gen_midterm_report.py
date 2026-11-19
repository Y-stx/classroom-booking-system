# -*- coding: utf-8 -*-
"""生成中期检查说明文档"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

DOCX_PATH = r'e:\教室预约与使用登记系统\项目文档\中期检查说明文档.docx'
IMG_DIR = r'e:\教室预约与使用登记系统\项目文档\screenshots'

def sf(run, size=None, bold=None, color=None):
    run.font.name = '宋体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    if size: run.font.size = Pt(size)
    if bold is not None: run.bold = bold
    if color: run.font.color.rgb = RGBColor(*color)

def add_heading(doc, text, level):
    h = doc.add_heading(text, level=level)
    for r in h.runs:
        r.font.name = '黑体'; r._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        if level == 1: r.font.size = Pt(22)
        elif level == 2: r.font.size = Pt(16)
        elif level == 3: r.font.size = Pt(14)
        else: r.font.size = Pt(12)

def add_para(doc, text, indent=True):
    p = doc.add_paragraph()
    if indent: p.paragraph_format.first_line_indent = Pt(24)
    p.paragraph_format.line_spacing = 1.5
    sf(p.add_run(text), size=12)

def add_img(doc, img_path, caption, width=Inches(5.8)):
    import os
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(img_path, width=width)
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sf(cp.add_run(caption), size=10, bold=True)

doc = Document()
doc.styles['Normal'].font.name = '宋体'
doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
doc.styles['Normal'].font.size = Pt(12)
for s in doc.sections:
    s.top_margin = Inches(1); s.bottom_margin = Inches(1)
    s.left_margin = Inches(1.2); s.right_margin = Inches(1.2)

# 封面
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(6)
r = p.add_run('教室预约与使用登记系统'); r.font.name='黑体'; r._element.rPr.rFonts.set(qn('w:eastAsia'),'黑体'); r.font.size=Pt(28); r.bold=True
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(40)
r = p.add_run('中期检查说明文档'); r.font.name='黑体'; r._element.rPr.rFonts.set(qn('w:eastAsia'),'黑体'); r.font.size=Pt(22); r.bold=True
for il in ['姓名：杨坤豫', '学号：2413040835', '专业：软件工程', '日期：2026-09-17']:
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; sf(p.add_run(il), size=13)
doc.add_page_break()

# 一、本人在该设计中具体应完成的工作
add_heading(doc, '一、本人在该设计中具体应完成的工作', 1)
add_para(doc, '本人作为项目组长，负责教室预约与使用登记系统的整体设计与开发工作。'
              '本系统是一个面向高校场景的教室资源管理平台，核心解决"预约—审批—使用—登记"的完整业务闭环。'
              '本人具体应完成的工作包括：')
for item in [
    '（1）项目整体架构设计：技术选型、前后端分离架构、数据库设计、接口规范制定；',
    '（2）后端核心功能开发：包括用户认证、教室管理、预约申请、审批管理、使用登记、数据统计等模块的接口实现与业务逻辑编写；',
    '（3）前端界面开发：包括登录页、三角色工作台、教室列表、预约管理、审批中心、使用登记、系统管理等页面的实现与样式优化；',
    '（4）数据库设计与初始化：4张核心数据表的结构设计、索引优化、初始数据准备；',
    '（5）安全机制实现：JWT 鉴权、角色权限控制、BCrypt 密码加密；',
    '（6）项目联调与测试：前后端接口对接、功能验证、问题修复；',
    '（7）项目文档编写：需求分析、系统设计、数据库设计、启动说明等文档。'
]:
    p = doc.add_paragraph(style='List Bullet'); p.paragraph_format.line_spacing = 1.5; sf(p.add_run(item), size=12)

# 二、具体工作和取得的进展
add_heading(doc, '二、课程设计开始以来所做的具体工作和取得的进展', 1)
add_para(doc, '截至目前，项目已完成阶段1至阶段5的核心功能开发，系统主流程（预约→审批→签到→签退）已完整跑通。'
              '以下按模块详细说明已完成的工作。')

# 2.1
add_heading(doc, '2.1 项目基础搭建（阶段1）', 2)
add_para(doc, '（1）创建 Spring Boot 3 后端工程，配置 MySQL 8.0 数据库连接与 MyBatis ORM 框架，'
              '引入 Spring Security Crypto（BCrypt）、SpringDoc OpenAPI（Swagger）、Redis、JWT 等依赖。')
add_para(doc, '（2）设计并创建数据库 4 张核心表：classroom（教室）、sys_user（用户）、reservation（预约）、usage_log（使用登记），'
              '每张表均配置主键、外键约束和查询索引，编写完整的建表与初始数据 SQL 脚本。')
add_para(doc, '（3）创建实体类与 Mapper 接口，开启 MyBatis 驼峰映射，打通 Java 代码与数据库的映射关系。')

# 2.2
add_heading(doc, '2.2 教室查询模块（阶段2）', 2)
add_para(doc, '（1）实现教室列表分页查询接口，支持按楼栋、类型、状态、关键字等条件筛选，返回统一的 Result 响应格式。')
add_para(doc, '（2）前端教室列表页面采用卡片网格布局，每张卡片展示教室真实图片（按类型映射：实验室/多媒体/机房/普通教室）、'
              '容量进度条、设备设施标签，并支持条件筛选。')
add_para(doc, '（3）配置 CORS 跨域支持，前端通过 Axios 调用后端接口获取教室数据。')
add_img(doc, f'{IMG_DIR}\\03_classroom_list.png', '图2-1 教室列表页面')

# 2.3
add_heading(doc, '2.3 预约申请模块（阶段3）', 2)
add_para(doc, '（1）实现预约提交接口，使用 Jakarta Validation 对教室ID、主题、起止时间等参数进行校验，'
              '业务层校验教室是否存在、是否可用、时间是否合法、人数是否超出容量。')
add_para(doc, '（2）实现时段冲突检测：通过 SQL 查询该教室在请求时段内是否已有"待审批"或"已通过"的预约，'
              '若存在冲突则拒绝创建并提示用户。')
add_para(doc, '（3）实现本人预约查询接口，支持按状态筛选（待审批/已通过/已驳回/已取消/已完成）与分页，'
              '预约状态使用枚举类 + TypeHandler 实现数据库字符串与 Java 枚举的转换。')
add_para(doc, '（4）前端预约表单含主题、目的、起止时间、预计人数等字段，提交成功后预约状态默认为"待审批"。')
add_img(doc, f'{IMG_DIR}\\04_reservation.png', '图2-2 我的预约页面')

# 2.4
add_heading(doc, '2.4 审核与取消模块（阶段4）', 2)
add_para(doc, '（1）实现管理员审核接口：通过审批将预约状态改为 APPROVED 并记录审批人和审批时间；'
              '驳回审批需填写驳回原因，状态改为 REJECTED。只有 PENDING 状态的预约可被审核。')
add_para(doc, '（2）实现取消预约功能：用户只能取消自己的预约，取消时必须填写取消原因，'
              '支持 PENDING 和 APPROVED 状态的取消操作。')
add_para(doc, '（3）所有写操作均使用 @Transactional(rollbackFor = Exception.class) 注解，确保数据一致性。')
add_img(doc, f'{IMG_DIR}\\05_approval.png', '图2-3 审批中心页面')

# 2.5
add_heading(doc, '2.5 使用登记模块（阶段5）', 2)
add_para(doc, '（1）实现签到接口：校验预约必须为已通过状态、当前用户为预约人、预约未结束、未重复签到，'
              '签到成功后创建使用登记记录。')
add_para(doc, '（2）实现签退接口：填写实际参会人数、设备状况、卫生评分、备注，'
              '签退成功后自动将预约状态更新为 COMPLETED。')
add_para(doc, '（3）实现重复登记拦截与已结束预约拦截，防止脏数据产生。')
add_para(doc, '（4）前端使用登记列表支持查看备注（点击设备状况标签弹出备注详情）。')
add_img(doc, f'{IMG_DIR}\\06_usage_log.png', '图2-4 使用登记页面')

# 2.6
add_heading(doc, '2.6 认证与安全机制', 2)
add_para(doc, '（1）实现 JWT 登录认证：用户登录成功后生成 JWT Token 并存入 Redis，'
              '实现 Token 的主动失效（登出时删除 Redis Key）。')
add_para(doc, '（2）实现 JWT 拦截器：对所有 /api/** 路径进行鉴权，白名单放行登录、注册、Swagger 等路径。')
add_para(doc, '（3）实现角色权限控制：系统分为学生、教师、管理员三种角色，'
              '不同角色登录后跳转至对应的工作台，侧边栏菜单根据角色动态显示。')
add_para(doc, '（4）密码使用 BCrypt 加密存储，启动时自动修复 SQL 脚本中的明文密码。')
add_img(doc, f'{IMG_DIR}\\01_login.png', '图2-5 登录页面')

# 2.7
add_heading(doc, '2.7 管理员工作台', 2)
add_para(doc, '（1）实现统计数据接口：返回教室总数、可用教室数、维护中教室数、总用户数、'
              '各状态预约数等统计指标。')
add_para(doc, '（2）前端管理员工作台展示统计卡片（6项关键指标）、预约状态饼图（ECharts）、'
              '教室状态柱状图、待审批列表，数据实时从后端获取。')
add_img(doc, f'{IMG_DIR}\\02_admin_home.png', '图2-6 管理员工作台页面')

# 2.8
add_heading(doc, '2.8 前端界面优化', 2)
add_para(doc, '（1）三角色主题色机制：学生（青蓝）、教师（靛紫）、管理员（紫粉），'
              '通过 CSS 变量 --role-primary 统一控制全站配色，主题色随用户角色自动切换并持久化存储。')
add_para(doc, '（2）教室卡片使用真实图片（按类型从 Unsplash 下载），鼠标悬停时图片微放大，'
              '状态标签和类型徽章在半透明渐变遮罩上清晰可辨。')
add_para(doc, '（3）统一列表页四段式布局（筛选区→操作栏→表格→分页），状态标签颜色语义明确，'
              '空状态与加载态视觉友好。')

# 三、存在问题与下一步计划
add_heading(doc, '三、目前存在问题与下一步计划', 1)

add_heading(doc, '3.1 目前存在的问题', 2)
for item in [
    '（1）空闲教室查询接口尚未实现：指导书 2.2 要求的"按指定日期时段查询空闲教室"功能尚未开发，'
    '目前仅在预约提交时做冲突检测，未提供独立的空闲教室查询接口。',
    '（2）取消预约缺少时间校验：指导书 4.2 要求只有"未开始"的预约才能取消，'
    '目前代码未校验当前时间是否早于预约开始时间。',
    '（3）教室列表缺少容量筛选：指导书 2.1 要求支持按最小容量筛选，目前未实现。',
    '（4）测试文档不完整：阶段6要求的测试条件清单和测试报告文档尚未编写，'
    '仅有2个单元测试类（预约状态枚举测试、DTO参数归一化测试）。',
    '（5）选做功能未实现：使用率统计（7.1）、批量预约与爽约标记（7.3）、'
    'MockMvc 集成测试（7.2）等选做功能尚未开发。'
]:
    p = doc.add_paragraph(style='List Bullet'); p.paragraph_format.line_spacing = 1.5; sf(p.add_run(item), size=12)

add_heading(doc, '3.2 下一步主要设计任务与安排', 2)
add_para(doc, '针对上述问题，下一步的工作安排如下：')
for item in [
    '【高优先级】实现空闲教室查询接口（2.2）：在 ClassroomMapper 中新增查询方法，'
    '通过时段冲突 SQL 排除已被预约的教室，前端教室列表增加日期时段筛选条件。预计1天完成。',
    '【高优先级】完善取消预约的时间校验（4.2）：在 cancel 方法中增加"当前时间须早于预约开始时间"的校验，'
    '已开始的预约不允许取消。预计0.5天完成。',
    '【高优先级】增加教室容量筛选（2.1）：在教室查询接口增加 minCapacity 参数，前端筛选栏增加容量输入框。'
    '预计0.5天完成。',
    '【中优先级】编写测试文档（6.1/6.3）：整理测试条件清单（覆盖正常/异常场景），'
    '执行测试并记录结果，编写测试报告。预计1天完成。',
    '【低优先级】使用率统计功能（7.1）：实现按教室预约次数和按周统计的聚合查询接口，'
    '前端增加使用率展示。预留选做，时间充裕时开发。',
    '【低优先级】批量预约与爽约标记（7.3）：实现按周次批量生成预约接口和爽约标记查询（已通过+已过期+无登记）。'
    '预留选做，时间充裕时开发。'
]:
    p = doc.add_paragraph(style='List Bullet'); p.paragraph_format.line_spacing = 1.5; sf(p.add_run(item), size=12)

add_para(doc, '总体而言，项目核心业务功能（预约→审批→签到→签退闭环）已完整实现并经过验证，'
              '预计在剩余时间内补齐高优先级的3项功能和测试文档，确保系统功能完整、文档齐全。')

doc.save(DOCX_PATH)
print(f'Word 文档已生成: {DOCX_PATH}')
print(f'文件大小: {__import__("os").path.getsize(DOCX_PATH)/1024:.1f} KB')
