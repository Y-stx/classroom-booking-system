package com.classroom.reservation.enums;

/**
 * 教室状态枚举
 */
public enum ClassroomStatus {

    AVAILABLE("可用"),
    MAINTENANCE("维护中"),
    DISABLED("已停用");

    private final String description;

    ClassroomStatus(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }

    public static ClassroomStatus fromCode(String code) {
        if (code == null || code.isBlank()) {
            throw new IllegalArgumentException("教室状态不能为空");
        }
        for (ClassroomStatus status : values()) {
            if (status.name().equalsIgnoreCase(code.trim())) {
                return status;
            }
        }
        throw new IllegalArgumentException("未知的教室状态: " + code);
    }
}
