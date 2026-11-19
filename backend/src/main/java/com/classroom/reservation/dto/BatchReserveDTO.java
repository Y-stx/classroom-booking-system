package com.classroom.reservation.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 批量预约 DTO
 * 从首个开始时间起，每周同一时段生成预约，共 weekCount 条
 */
@Data
public class BatchReserveDTO {

    @NotNull(message = "教室ID不能为空")
    private Long classroomId;

    @NotBlank(message = "预约主题不能为空")
    private String title;

    private String purpose;

    private Integer attendees;

    @NotNull(message = "首个开始时间不能为空")
    private LocalDateTime startTime;

    @NotNull(message = "首个结束时间不能为空")
    private LocalDateTime endTime;

    @NotNull(message = "周次不能为空")
    @Min(value = 1, message = "周次至少为1")
    private Integer weekCount;
}
