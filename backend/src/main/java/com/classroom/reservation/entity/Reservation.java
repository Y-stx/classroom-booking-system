package com.classroom.reservation.entity;

import com.classroom.reservation.enums.ReservationStatus;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 预约实体类
 */
@Data
public class Reservation {

    private Long id;
    private Long classroomId;
    private Long userId;
    private String title;
    private String purpose;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private Integer attendees;
    private ReservationStatus status;
    private Long approverId;
    private LocalDateTime approveTime;
    private String rejectReason;
    private String cancelReason;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    /** 关联字段（非数据库列，用于联表查询结果） */
    private String classroomName;
    private String building;
    private String userName;
    private String approverName;
}
