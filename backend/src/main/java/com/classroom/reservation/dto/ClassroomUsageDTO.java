package com.classroom.reservation.dto;

import lombok.Data;

/**
 * 教室使用率统计 DTO
 */
@Data
public class ClassroomUsageDTO {

    private Long classroomId;
    private String classroomName;
    private String building;
    private Integer reservationCount;   // 预约次数
    private Double usageRate;           // 使用率（该教室预约次数 / 总预约次数）
}
