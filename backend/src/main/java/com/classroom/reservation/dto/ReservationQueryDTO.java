package com.classroom.reservation.dto;

import lombok.Data;

@Data
public class ReservationQueryDTO {

    private Long userId;
    private Long classroomId;
    private String status;
    private String keyword;
    private Integer page = 1;
    private Integer pageSize = 10;

    public int getNormalizedPage() {
        return page == null || page < 1 ? 1 : page;
    }

    public int getNormalizedPageSize() {
        if (pageSize == null || pageSize < 1) return 10;
        return Math.min(pageSize, 100);
    }

    public String getNormalizedKeyword() {
        return keyword == null ? null : keyword.trim();
    }
}
