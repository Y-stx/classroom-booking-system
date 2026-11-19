package com.classroom.reservation.service;

import com.classroom.reservation.common.PageResult;
import com.classroom.reservation.dto.CheckOutDTO;
import com.classroom.reservation.entity.UsageLog;

public interface UsageLogService {

    UsageLog checkIn(Long reservationId, Long userId);

    UsageLog checkOut(CheckOutDTO dto, Long userId);

    PageResult<UsageLog> findPage(Long userId, Long classroomId, String keyword, int page, int pageSize);
}
