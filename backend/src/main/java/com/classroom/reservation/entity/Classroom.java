package com.classroom.reservation.entity;

import lombok.Data;
import java.time.LocalDateTime;

/**
 * 教室实体类
 */
@Data
public class Classroom {

    private Long id;
    private String name;
    private String building;
    private Integer floor;
    private Integer capacity;
    private String type;
    private String equipment;
    private String status;
    private String imageUrl;
    private String remark;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
