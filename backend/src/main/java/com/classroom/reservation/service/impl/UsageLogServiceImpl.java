package com.classroom.reservation.service.impl;

import com.classroom.reservation.common.PageResult;
import com.classroom.reservation.dto.CheckOutDTO;
import com.classroom.reservation.entity.Reservation;
import com.classroom.reservation.entity.UsageLog;
import com.classroom.reservation.enums.ReservationStatus;
import com.classroom.reservation.exception.BusinessException;
import com.classroom.reservation.mapper.ReservationMapper;
import com.classroom.reservation.mapper.UsageLogMapper;
import com.classroom.reservation.service.UsageLogService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class UsageLogServiceImpl implements UsageLogService {

    private final UsageLogMapper usageLogMapper;
    private final ReservationMapper reservationMapper;

    public UsageLogServiceImpl(UsageLogMapper usageLogMapper, ReservationMapper reservationMapper) {
        this.usageLogMapper = usageLogMapper;
        this.reservationMapper = reservationMapper;
    }

    @Override
    public UsageLog checkIn(Long reservationId, Long userId) {
        Reservation reservation = reservationMapper.findById(reservationId);
        if (reservation == null) {
            throw new BusinessException(404, "预约记录不存在");
        }
        // 只有 APPROVED 状态可以签到
        if (reservation.getStatus() != ReservationStatus.APPROVED) {
            throw new BusinessException("只有已通过的预约才能签到，当前状态: " + reservation.getStatus().getDescription());
        }
        // 检查是否已签到
        UsageLog existing = usageLogMapper.findByReservationId(reservationId);
        if (existing != null && existing.getCheckInTime() != null) {
            throw new BusinessException("该预约已签到，不能重复签到");
        }

        // 已结束预约拦截：预约结束时间早于当前时间则不允许签到
        if (reservation.getEndTime().isBefore(LocalDateTime.now())) {
            throw new BusinessException("预约已结束，无法签到使用");
        }

        if (existing == null) {
            UsageLog log = new UsageLog();
            log.setReservationId(reservationId);
            log.setClassroomId(reservation.getClassroomId());
            log.setUserId(userId);
            log.setCheckInTime(LocalDateTime.now());
            usageLogMapper.insert(log);
            return usageLogMapper.findById(log.getId());
        } else {
            // 已有记录但未签到（理论上不会出现）
            throw new BusinessException("签到失败，请稍后重试");
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public UsageLog checkOut(CheckOutDTO dto, Long userId) {
        Reservation reservation = reservationMapper.findById(dto.getReservationId());
        if (reservation == null) {
            throw new BusinessException(404, "预约记录不存在");
        }
        UsageLog usageLog = usageLogMapper.findByReservationId(dto.getReservationId());
        if (usageLog == null) {
            throw new BusinessException("该预约尚未签到，不能签退");
        }
        if (usageLog.getCheckOutTime() != null) {
            throw new BusinessException("该预约已签退，不能重复签退");
        }

        // 卫生评分默认 5 星（未填写时）
        Integer cleanliness = dto.getCleanliness() != null ? dto.getCleanliness() : 5;

        usageLogMapper.checkOut(usageLog.getId(), LocalDateTime.now(),
                dto.getActualAttendees(), dto.getEquipmentStatus(),
                cleanliness, dto.getNotes());

        // 签退后自动完成预约
        reservationMapper.updateStatus(reservation.getId(), ReservationStatus.COMPLETED);

        return usageLogMapper.findById(usageLog.getId());
    }

    @Override
    public PageResult<UsageLog> findPage(Long userId, Long classroomId, String keyword, int page, int pageSize) {
        page = Math.max(page, 1);
        pageSize = Math.max(1, Math.min(pageSize, 100));
        int offset = (page - 1) * pageSize;
        List<UsageLog> list = usageLogMapper.findPageWithJoin(userId, classroomId, keyword, offset, pageSize);
        long total = usageLogMapper.count(userId, classroomId, keyword);
        return PageResult.of(list, total, page, pageSize);
    }
}
