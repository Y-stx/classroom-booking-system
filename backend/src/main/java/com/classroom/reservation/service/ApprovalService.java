package com.classroom.reservation.service;

import com.classroom.reservation.common.PageResult;
import com.classroom.reservation.dto.ReservationQueryDTO;
import com.classroom.reservation.entity.Reservation;

public interface ApprovalService {

    PageResult<Reservation> findPending(ReservationQueryDTO query);

    void approve(Long id, Long approverId);

    void reject(Long id, Long approverId, String reason);
}
