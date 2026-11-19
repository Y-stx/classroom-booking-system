package com.classroom.reservation.dto;

import lombok.Data;

/**
 * 按周预约次数统计 DTO
 */
@Data
public class WeeklyUsageDTO {

    private String weekLabel;   // 周标签，如 2026-W37
    private Integer reservationCount;
}
