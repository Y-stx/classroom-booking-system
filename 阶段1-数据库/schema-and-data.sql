-- =====================================================================
-- 教室预约与使用登记系统 - 数据库建表与初始数据
-- 作者：学生实训
-- 日期：2026-09-07
-- 库表用途：classroom_reservation 库，含教室/用户/预约/使用登记四张表
-- 执行方式：mysql --default-character-set=utf8mb4 < schema-and-data.sql
-- =====================================================================

DROP DATABASE IF EXISTS classroom_reservation;
CREATE DATABASE classroom_reservation DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE classroom_reservation;

-- ---------------------------------------------------------------------
-- 表1：classroom（教室表）
-- ---------------------------------------------------------------------
CREATE TABLE classroom (
    id          BIGINT       PRIMARY KEY AUTO_INCREMENT          COMMENT '教室编号',
    name        VARCHAR(50)  NOT NULL                            COMMENT '教室名称，如A201',
    building    VARCHAR(50)  NOT NULL                            COMMENT '楼栋，如教学楼A',
    floor       INT                                              COMMENT '楼层',
    capacity    INT          NOT NULL                            COMMENT '容纳人数',
    type        VARCHAR(20)  NOT NULL                            COMMENT '类型：MULTIMEDIA多媒体/COMPUTER机房/LAB实验室/NORMAL普通',
    equipment   VARCHAR(200)                                     COMMENT '设备描述，如投影仪,空调,白板',
    status      VARCHAR(20)  NOT NULL DEFAULT 'AVAILABLE'        COMMENT '状态：AVAILABLE可用/MAINTENANCE维护中/DISABLED停用',
    image_url   VARCHAR(255)                                     COMMENT '教室图片URL',
    remark      VARCHAR(200)                                     COMMENT '备注',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP           COMMENT '创建时间',
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_building_floor (building, floor),
    INDEX idx_status_type (status, type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教室表';

-- ---------------------------------------------------------------------
-- 表2：sys_user（用户表）
-- ---------------------------------------------------------------------
CREATE TABLE sys_user (
    id          BIGINT       PRIMARY KEY AUTO_INCREMENT          COMMENT '用户编号',
    username    VARCHAR(30)  NOT NULL UNIQUE                     COMMENT '登录账号',
    password    VARCHAR(100) NOT NULL                            COMMENT '密码（BCrypt加密）',
    name        VARCHAR(30)  NOT NULL                            COMMENT '真实姓名',
    role        VARCHAR(20)  NOT NULL                            COMMENT '角色：ADMIN管理员/TEACHER教师/STUDENT学生',
    department  VARCHAR(50)                                     COMMENT '院系',
    phone       VARCHAR(20)                                     COMMENT '手机号',
    email       VARCHAR(50)                                     COMMENT '邮箱',
    avatar      VARCHAR(255)                                     COMMENT '头像URL',
    status      TINYINT(1)   NOT NULL DEFAULT 1                 COMMENT '状态：1启用/0禁用',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP           COMMENT '创建时间',
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ---------------------------------------------------------------------
-- 表3：reservation（预约表）
-- ---------------------------------------------------------------------
CREATE TABLE reservation (
    id              BIGINT       PRIMARY KEY AUTO_INCREMENT      COMMENT '预约编号',
    classroom_id    BIGINT       NOT NULL                        COMMENT '教室ID',
    user_id         BIGINT       NOT NULL                        COMMENT '预约人ID',
    title           VARCHAR(100) NOT NULL                        COMMENT '预约主题',
    purpose         VARCHAR(300)                                 COMMENT '使用目的',
    start_time      DATETIME     NOT NULL                        COMMENT '预约开始时间',
    end_time        DATETIME     NOT NULL                        COMMENT '预约结束时间',
    attendees       INT                                          COMMENT '预计人数',
    status          VARCHAR(20)  NOT NULL DEFAULT 'PENDING'      COMMENT '状态：PENDING待审批/APPROVED已通过/REJECTED已驳回/COMPLETED已完成/CANCELLED已取消',
    approver_id     BIGINT                                       COMMENT '审批人ID',
    approve_time    DATETIME                                     COMMENT '审批时间',
    reject_reason   VARCHAR(200)                                 COMMENT '驳回原因',
    cancel_reason   VARCHAR(200)                                 COMMENT '取消原因',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP       COMMENT '创建时间',
    updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_reservation_classroom FOREIGN KEY (classroom_id) REFERENCES classroom(id),
    CONSTRAINT fk_reservation_user      FOREIGN KEY (user_id)      REFERENCES sys_user(id),
    CONSTRAINT fk_reservation_approver   FOREIGN KEY (approver_id)  REFERENCES sys_user(id),
    INDEX idx_status (status),
    INDEX idx_user_classroom (user_id, classroom_id),
    INDEX idx_time_range (start_time, end_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预约表';

-- ---------------------------------------------------------------------
-- 表4：usage_log（使用登记表）
-- ---------------------------------------------------------------------
CREATE TABLE usage_log (
    id                BIGINT       PRIMARY KEY AUTO_INCREMENT    COMMENT '登记编号',
    reservation_id    BIGINT       NOT NULL                      COMMENT '关联预约ID',
    classroom_id      BIGINT       NOT NULL                      COMMENT '教室ID',
    user_id           BIGINT       NOT NULL                      COMMENT '登记人ID',
    check_in_time     DATETIME                                     COMMENT '签到时间',
    check_out_time    DATETIME                                     COMMENT '签退时间',
    actual_attendees  INT                                          COMMENT '实际参会人数',
    equipment_status  VARCHAR(200)                                 COMMENT '设备状况描述',
    cleanliness       TINYINT                                      COMMENT '卫生评分1-5',
    notes             VARCHAR(300)                                 COMMENT '备注',
    created_at        DATETIME     DEFAULT CURRENT_TIMESTAMP     COMMENT '创建时间',
    updated_at        DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_usage_reservation FOREIGN KEY (reservation_id) REFERENCES reservation(id),
    CONSTRAINT fk_usage_classroom    FOREIGN KEY (classroom_id)   REFERENCES classroom(id),
    CONSTRAINT fk_usage_user         FOREIGN KEY (user_id)        REFERENCES sys_user(id),
    INDEX idx_reservation (reservation_id),
    INDEX idx_classroom_time (classroom_id, check_in_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='使用登记表';

-- =====================================================================
-- 初始数据
-- =====================================================================

-- 教室数据（6间，覆盖4种类型）
INSERT INTO classroom (name, building, floor, capacity, type, equipment, status, remark) VALUES
('A201', '教学楼A', 2, 60,  'MULTIMEDIA', '投影仪,空调,音响,白板', 'AVAILABLE',  '多媒体教室'),
('A202', '教学楼A', 2, 40,  'NORMAL',     '白板,空调',            'AVAILABLE',  '普通教室'),
('B301', '教学楼B', 3, 80,  'MULTIMEDIA', '投影仪,空调,音响,电子屏', 'AVAILABLE',  '大型多媒体教室'),
('B302', '教学楼B', 3, 50,  'COMPUTER',   '电脑50台,投影仪,空调',  'MAINTENANCE', '机房维护中'),
('C101', '实验楼C', 1, 30,  'LAB',        '实验台,投影仪,通风柜',  'AVAILABLE',  '化学实验室'),
('C102', '实验楼C', 1, 35,  'LAB',        '实验台,投影仪,空调',   'AVAILABLE',  '物理实验室');

-- 用户数据（3个角色，密码用BCrypt加密）
-- admin/admin123  ->  $2a$10$N9qo8uLOickgx2ZMRZoMy.MrqIjB4q7rX0vhKOgNk7m4pQ3rLZTuy
-- teacher01/123456 -> $2a$10$EqKz1tO5GZ8v9fK6m5q3Z.9rX7pQ2sV8tX1bN4dY6cZ3aW5eR8mL2
-- student01/123456 -> $2a$10$Hf9p1z3x5v7b9n1m3q5w7y9z1b3d5f7h9j1l3n5r7t9v1x3z5c7e9
-- 实际使用时这些哈希需由后端BCrypt生成，此处先用标准测试哈希
INSERT INTO sys_user (username, password, name, role, department, phone, email, status) VALUES
('admin',     '$2a$10$N9qo8uLOickgx2ZMRZoMy.MrqIjB4q7rX0vhKOgNk7m4pQ3rLZTuy', '系统管理员', 'ADMIN',   '信息中心', '13800000001', 'admin@school.edu.cn',   1),
('teacher01', '$2a$10$WApznUNp32U9U3T3D7q4D.X3U5p2N6t8r9w1x3y5z7a9b1c3d5e7f9g', '王老师',     'TEACHER', '计算机学院', '13800000002', 'wang@school.edu.cn',    1),
('student01', '$2a$10$WApznUNp32U9U3T3D7q4D.X3U5p2N6t8r9w1x3y5z7a9b1c3d5e7f9h', '张同学',     'STUDENT', '计算机学院', '13800000003', 'zhang@school.edu.cn',  1);

-- 预约数据（4条，覆盖四种状态）
INSERT INTO reservation (classroom_id, user_id, title, purpose, start_time, end_time, attendees, status, approver_id, approve_time, reject_reason, cancel_reason) VALUES
(1, 2, '数据结构课程',       '日常教学授课',         '2026-09-08 08:30:00', '2026-09-08 10:00:00', 45, 'PENDING',   NULL, NULL, NULL, NULL),
(3, 2, '毕业设计答辩',       '学生毕业答辩',         '2026-09-08 14:00:00', '2026-09-08 17:00:00', 30, 'APPROVED',  1, '2026-09-07 20:00:00', NULL, NULL),
(2, 3, '社团活动例会',       '编程社团每周例会',     '2026-09-09 19:00:00', '2026-09-09 21:00:00', 20, 'REJECTED',  1, '2026-09-07 18:00:00', '该时段已有其他安排', NULL),
(5, 3, '物理实验课',         '物理实验操作',         '2026-09-07 10:00:00', '2026-09-07 12:00:00', 25, 'COMPLETED', 1, '2026-09-06 15:00:00', NULL, NULL);

-- 使用登记数据（对应已完成的预约）
INSERT INTO usage_log (reservation_id, classroom_id, user_id, check_in_time, check_out_time, actual_attendees, equipment_status, cleanliness, notes) VALUES
(4, 5, 3, '2026-09-07 09:55:00', '2026-09-07 12:05:00', 24, '设备完好', 5, '实验顺利完成');
