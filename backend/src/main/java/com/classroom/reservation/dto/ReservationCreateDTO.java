package com.classroom.reservation.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDateTime;

@Data
public class ReservationCreateDTO {

    @NotNull(message = "教室ID不能为空")
    private Long classroomId;

    @NotBlank(message = "预约主题不能为空")
    private String title;

    private String purpose;

    @NotNull(message = "开始时间不能为空")
    private LocalDateTime startTime;

    @NotNull(message = "结束时间不能为空")
    private LocalDateTime endTime;

    private Integer attendees;
}
