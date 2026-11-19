package com.classroom.reservation.enums;

/**
 * 预约状态枚举 - 状态机
 *
 * 状态流转规则：
 * PENDING  → APPROVED（管理员审批通过）
 * PENDING  → REJECTED（管理员驳回）
 * APPROVED → COMPLETED（签退后自动完成）
 * APPROVED → CANCELLED（用户取消）
 * PENDING  → CANCELLED（用户取消未审批的预约）
 */
public enum ReservationStatus {

    PENDING("待审批"),
    APPROVED("已通过"),
    REJECTED("已驳回"),
    COMPLETED("已完成"),
    CANCELLED("已取消");

    private final String description;

    ReservationStatus(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }

    /**
     * 判断当前状态是否可以流转到目标状态
     */
    public boolean canTransitTo(ReservationStatus target) {
        if (target == null) return false;
        return switch (this) {
            case PENDING -> target == APPROVED || target == REJECTED || target == CANCELLED;
            case APPROVED -> target == COMPLETED || target == CANCELLED;
            case REJECTED, COMPLETED, CANCELLED -> false;
        };
    }

    /**
     * 根据 code 获取枚举，找不到抛异常
     */
    public static ReservationStatus fromCode(String code) {
        if (code == null || code.isBlank()) {
            throw new IllegalArgumentException("预约状态不能为空");
        }
        for (ReservationStatus status : values()) {
            if (status.name().equalsIgnoreCase(code.trim())) {
                return status;
            }
        }
        throw new IllegalArgumentException("未知的预约状态: " + code);
    }
}
