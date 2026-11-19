# 教室预约与使用登记系统

面向学校场景的教室预约与使用登记平台，采用前后端分离架构。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Vite + Element Plus + Pinia + ECharts + SCSS |
| 后端 | Spring Boot 3.2 + MyBatis + JWT + SpringDoc OpenAPI |
| 数据库 | MySQL 8.0 |
| 缓存 | Redis 7 |
| 构建 | Maven / npm |

## 核心功能

- 三种角色：学生 / 教师 / 管理员，登录入口与主题配色区分
- 教室管理：列表查询、条件筛选（楼栋/类型/状态/最小容量）、按时段查空闲教室
- 预约申请：创建预约、时段冲突检测、容量校验、本人预约查询
- 审核流程：管理员通过/驳回、驳回原因
- 取消预约：仅已通过且未开始的预约可取消
- 使用登记：签到、签退、设备状态记录
- 统计概览：教室使用率统计、按周预约趋势、爽约标记
- 批量预约：按周次批量生成预约

## 快速启动

### 环境要求

- JDK 17+
- Maven 3.8+
- Node.js 18+
- MySQL 8.0
- Redis 6+

### 1. 初始化数据库

```bash
mysql -u root -p < 阶段1-数据库/schema-and-data.sql
```

### 2. 配置后端

复制 `application-example.yml` 为 `application.yml`，修改数据库密码：

```bash
cp backend/src/main/resources/application-example.yml backend/src/main/resources/application.yml
```

### 3. 启动 Redis

```bash
# Windows 服务
net start Redis
# 或直接运行
redis-server.exe
```

### 4. 启动后端

```bash
cd backend
mvn spring-boot:run
```

后端运行在 http://localhost:8080

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:5173

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 学生 | student01 | 123456 |
| 教师 | teacher01 | 123456 |
| 管理员 | admin | admin123 |

## 接口文档

启动后端后访问 Swagger UI：http://localhost:8080/swagger-ui.html

## 目录结构

```
教室预约与使用登记系统/
├── backend/                    # Spring Boot 后端
│   ├── src/main/java/com/classroom/reservation/
│   │   ├── controller/         # 控制器
│   │   ├── service/            # 业务逻辑
│   │   ├── mapper/             # MyBatis 数据访问
│   │   ├── entity/             # 实体类
│   │   ├── dto/                # 数据传输对象
│   │   ├── enums/              # 枚举
│   │   ├── exception/          # 异常处理
│   │   └── security/           # JWT 认证
│   └── src/main/resources/
│       ├── application.yml     # 配置文件
│       └── application-example.yml
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── views/              # 页面
│   │   ├── api/                # 接口封装
│   │   ├── router/             # 路由
│   │   ├── stores/             # Pinia 状态
│   │   └── styles/             # 全局样式
│   └── public/images/classrooms/
├── 阶段1-数据库/                # 建库脚本
├── scripts/                    # 工具脚本
└── 项目文档/                    # 设计与说明文档
```

## 运行测试

```bash
cd backend
mvn test
```

包含单元测试（枚举状态流转、DTO 归一化）和 MockMvc 集成测试（登录、预约、使用登记等接口）。
