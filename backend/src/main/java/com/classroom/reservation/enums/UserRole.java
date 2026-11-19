package com.classroom.reservation.enums;

/**
 * 用户角色枚举
 */
public enum UserRole {

    ADMIN("管理员"),
    TEACHER("教师"),
    STUDENT("学生");

    private final String description;

    UserRole(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }

    public static UserRole fromCode(String code) {
        if (code == null || code.isBlank()) {
            throw new IllegalArgumentException("用户角色不能为空");
        }
        for (UserRole role : values()) {
            if (role.name().equalsIgnoreCase(code.trim())) {
                return role;
            }
        }
        throw new IllegalArgumentException("未知的用户角色: " + code);
    }
}
