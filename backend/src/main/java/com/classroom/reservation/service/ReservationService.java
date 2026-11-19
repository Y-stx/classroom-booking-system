package com.classroom.reservation.service;

import com.classroom.reservation.common.PageResult;
import com.classroom.reservation.dto.BatchReserveDTO;
import com.classroom.reservation.dto.ReservationCreateDTO;
import com.classroom.reservation.dto.ReservationQueryDTO;
import com.classroom.reservation.entity.Reservation;

import java.util.List;
import java.util.Map;

public interface ReservationService {

    Reservation create(ReservationCreateDTO dto, Long userId);

    PageResult<Reservation> findMyReservations(ReservationQueryDTO query, Long userId);

    PageResult<Reservation> findAll(ReservationQueryDTO query);

    Reservation findById(Long id);

    void cancel(Long id, Long userId, String reason);

    /**
     * 批量预约（按周次生成）
     * @return 包含 successCount 和 failedSlots 的结果
     */
    Map<String, Object> batchReserve(BatchReserveDTO dto, Long userId);

    /**
     * 查询爽约预约列表
     */
    List<Reservation> findNoShows();
}
