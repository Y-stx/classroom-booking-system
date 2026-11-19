package com.classroom.reservation.entity;

import lombok.Data;
import java.time.LocalDateTime;

/**
 * 使用登记实体类
 */
@Data
public class UsageLog {

    private Long id;
    private Long reservationId;
    private Long classroomId;
    private Long userId;
    private LocalDateTime checkInTime;
    private LocalDateTime checkOutTime;
    private Integer actualAttendees;
    private String equipmentStatus;
    private Integer cleanliness;
    private String notes;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    /** 关联字段（非数据库列，用于联表查询结果） */
    private String classroomName;
    private String userName;
    private String title;
}
