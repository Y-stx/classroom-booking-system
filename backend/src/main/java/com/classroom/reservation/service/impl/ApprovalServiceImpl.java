package com.classroom.reservation.service.impl;

import com.classroom.reservation.common.PageResult;
import com.classroom.reservation.dto.ReservationQueryDTO;
import com.classroom.reservation.entity.Reservation;
import com.classroom.reservation.enums.ReservationStatus;
import com.classroom.reservation.exception.BusinessException;
import com.classroom.reservation.mapper.ReservationMapper;
import com.classroom.reservation.service.ApprovalService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class ApprovalServiceImpl implements ApprovalService {

    private final ReservationMapper reservationMapper;

    public ApprovalServiceImpl(ReservationMapper reservationMapper) {
        this.reservationMapper = reservationMapper;
    }

    @Override
    public PageResult<Reservation> findPending(ReservationQueryDTO query) {
        int offset = (query.getNormalizedPage() - 1) * query.getNormalizedPageSize();
        List<Reservation> list = reservationMapper.findPageWithJoin(
                null, null, "PENDING", query.getNormalizedKeyword(),
                offset, query.getNormalizedPageSize());
        long total = reservationMapper.count(null, null, "PENDING", query.getNormalizedKeyword());
        return PageResult.of(list, total, query.getNormalizedPage(), query.getNormalizedPageSize());
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void approve(Long id, Long approverId) {
        Reservation reservation = reservationMapper.findById(id);
        if (reservation == null) {
            throw new BusinessException(404, "预约记录不存在");
        }
        ReservationStatus current = reservation.getStatus();
        if (!current.canTransitTo(ReservationStatus.APPROVED)) {
            throw new BusinessException("只有待审批的预约才能通过，当前状态: " + current.getDescription());
        }
        reservationMapper.approve(id, ReservationStatus.APPROVED, approverId, LocalDateTime.now(), null);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void reject(Long id, Long approverId, String reason) {
        Reservation reservation = reservationMapper.findById(id);
        if (reservation == null) {
            throw new BusinessException(404, "预约记录不存在");
        }
        ReservationStatus current = reservation.getStatus();
        if (!current.canTransitTo(ReservationStatus.REJECTED)) {
            throw new BusinessException("只有待审批的预约才能驳回，当前状态: " + current.getDescription());
        }
        if (reason == null || reason.isBlank()) {
            throw new BusinessException("驳回原因不能为空");
        }
        reservationMapper.approve(id, ReservationStatus.REJECTED, approverId, LocalDateTime.now(), reason);
    }
}
