package com.classroom.reservation.enums;

/**
 * 教室类型枚举
 */
public enum ClassroomType {

    MULTIMEDIA("多媒体教室"),
    COMPUTER("机房"),
    LAB("实验室"),
    NORMAL("普通教室");

    private final String description;

    ClassroomType(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }

    public static ClassroomType fromCode(String code) {
        if (code == null || code.isBlank()) {
            throw new IllegalArgumentException("教室类型不能为空");
        }
        for (ClassroomType type : values()) {
            if (type.name().equalsIgnoreCase(code.trim())) {
                return type;
            }
        }
        throw new IllegalArgumentException("未知的教室类型: " + code);
    }
}
