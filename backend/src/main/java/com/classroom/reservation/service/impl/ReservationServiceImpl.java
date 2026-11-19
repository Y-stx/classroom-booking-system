package com.classroom.reservation.service.impl;

import com.classroom.reservation.common.PageResult;
import com.classroom.reservation.dto.BatchReserveDTO;
import com.classroom.reservation.dto.ReservationCreateDTO;
import com.classroom.reservation.dto.ReservationQueryDTO;
import com.classroom.reservation.entity.Classroom;
import com.classroom.reservation.entity.Reservation;
import com.classroom.reservation.enums.ReservationStatus;
import com.classroom.reservation.exception.BusinessException;
import com.classroom.reservation.mapper.ClassroomMapper;
import com.classroom.reservation.mapper.ReservationMapper;
import com.classroom.reservation.service.ReservationService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class ReservationServiceImpl implements ReservationService {

    private final ReservationMapper reservationMapper;
    private final ClassroomMapper classroomMapper;

    public ReservationServiceImpl(ReservationMapper reservationMapper, ClassroomMapper classroomMapper) {
        this.reservationMapper = reservationMapper;
        this.classroomMapper = classroomMapper;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Reservation create(ReservationCreateDTO dto, Long userId) {
        // 校验教室存在且可用
        Classroom classroom = classroomMapper.findById(dto.getClassroomId());
        if (classroom == null) {
            throw new BusinessException(404, "教室不存在");
        }
        if (!"AVAILABLE".equals(classroom.getStatus())) {
            throw new BusinessException("该教室当前不可预约（" + classroom.getStatus() + "）");
        }

        // 校验时间
        if (dto.getStartTime().isAfter(dto.getEndTime()) || dto.getStartTime().isBefore(LocalDateTime.now())) {
            throw new BusinessException("预约时间不合法");
        }

        // 容量校验：预约人数不能超过教室容量
        if (dto.getAttendees() != null && dto.getAttendees() > classroom.getCapacity()) {
            throw new BusinessException("预约人数(" + dto.getAttendees() + ")超过教室容量(" + classroom.getCapacity() + ")");
        }

        // 时间冲突检测
        List<Reservation> conflicts = reservationMapper.findConflicts(
                dto.getClassroomId(), dto.getStartTime(), dto.getEndTime(), null);
        if (!conflicts.isEmpty()) {
            Reservation c = conflicts.get(0);
            throw new BusinessException(String.format(
                    "该教室在指定时间段内已有预约冲突（冲突预约：%s ~ %s，预约主题：%s）",
                    c.getStartTime(), c.getEndTime(), c.getTitle()));
        }

        // 构建实体并插入
        Reservation reservation = new Reservation();
        reservation.setClassroomId(dto.getClassroomId());
        reservation.setUserId(userId);
        reservation.setTitle(dto.getTitle());
        reservation.setPurpose(dto.getPurpose());
        reservation.setStartTime(dto.getStartTime());
        reservation.setEndTime(dto.getEndTime());
        reservation.setAttendees(dto.getAttendees());
        reservation.setStatus(ReservationStatus.PENDING);
        reservationMapper.insert(reservation);
        return reservationMapper.findById(reservation.getId());
    }

    @Override
    public PageResult<Reservation> findMyReservations(ReservationQueryDTO query, Long userId) {
        int offset = (query.getNormalizedPage() - 1) * query.getNormalizedPageSize();
        List<Reservation> list = reservationMapper.findPageWithJoin(
                userId, null, query.getStatus(), query.getNormalizedKeyword(),
                offset, query.getNormalizedPageSize());
        long total = reservationMapper.count(userId, null, query.getStatus(), query.getNormalizedKeyword());
        return PageResult.of(list, total, query.getNormalizedPage(), query.getNormalizedPageSize());
    }

    @Override
    public PageResult<Reservation> findAll(ReservationQueryDTO query) {
        int offset = (query.getNormalizedPage() - 1) * query.getNormalizedPageSize();
        List<Reservation> list = reservationMapper.findPageWithJoin(
                query.getUserId(), query.getClassroomId(), query.getStatus(),
                query.getNormalizedKeyword(), offset, query.getNormalizedPageSize());
        long total = reservationMapper.count(query.getUserId(), query.getClassroomId(),
                query.getStatus(), query.getNormalizedKeyword());
        return PageResult.of(list, total, query.getNormalizedPage(), query.getNormalizedPageSize());
    }

    @Override
    public Reservation findById(Long id) {
        Reservation reservation = reservationMapper.findById(id);
        if (reservation == null) {
            throw new BusinessException(404, "预约记录不存在");
        }
        // 获取关联信息
        var list = reservationMapper.findPageWithJoin(null, null, null, null, 0, Integer.MAX_VALUE);
        return list.stream().filter(r -> r.getId().equals(id)).findFirst().orElse(reservation);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void cancel(Long id, Long userId, String reason) {
        Reservation reservation = reservationMapper.findById(id);
        if (reservation == null) {
            throw new BusinessException(404, "预约记录不存在");
        }
        // 权限校验：只能取消自己的预约
        if (!reservation.getUserId().equals(userId)) {
            throw new BusinessException(403, "只能取消自己的预约");
        }
        // 状态校验：只有"已通过"的预约可取消
        ReservationStatus current = reservation.getStatus();
        if (current != ReservationStatus.APPROVED) {
            throw new BusinessException("只有已通过的预约才能取消，当前状态(" + current.getDescription() + ")不允许取消");
        }
        // 时间校验：预约已开始则不允许取消
        if (reservation.getStartTime() != null && !reservation.getStartTime().isAfter(LocalDateTime.now())) {
            throw new BusinessException("预约已开始或已结束，无法取消");
        }
        // 取消原因必填
        if (reason == null || reason.isBlank()) {
            throw new BusinessException("请填写取消原因");
        }
        reservationMapper.cancel(id, ReservationStatus.CANCELLED, reason);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Map<String, Object> batchReserve(BatchReserveDTO dto, Long userId) {
        // 校验教室存在且可用
        Classroom classroom = classroomMapper.findById(dto.getClassroomId());
        if (classroom == null) {
            throw new BusinessException(404, "教室不存在");
        }
        if (!"AVAILABLE".equals(classroom.getStatus())) {
            throw new BusinessException("该教室当前不可预约");
        }
        // 校验首个时段时间
        if (dto.getStartTime().isAfter(dto.getEndTime()) || dto.getStartTime().isBefore(LocalDateTime.now())) {
            throw new BusinessException("预约时间不合法");
        }
        // 容量校验
        if (dto.getAttendees() != null && dto.getAttendees() > classroom.getCapacity()) {
            throw new BusinessException("预约人数超过教室容量");
        }

        int weekCount = dto.getWeekCount() == null ? 1 : dto.getWeekCount();
        int successCount = 0;
        List<String> failedSlots = new ArrayList<>();

        for (int i = 0; i < weekCount; i++) {
            LocalDateTime slotStart = dto.getStartTime().plusWeeks(i);
            LocalDateTime slotEnd = dto.getEndTime().plusWeeks(i);

            // 冲突检测
            List<Reservation> conflicts = reservationMapper.findConflicts(
                    dto.getClassroomId(), slotStart, slotEnd, null);
            if (!conflicts.isEmpty()) {
                failedSlots.add(slotStart + " ~ " + slotEnd + "（时段冲突）");
                continue;
            }

            Reservation reservation = new Reservation();
            reservation.setClassroomId(dto.getClassroomId());
            reservation.setUserId(userId);
            reservation.setTitle(dto.getTitle());
            reservation.setPurpose(dto.getPurpose());
            reservation.setStartTime(slotStart);
            reservation.setEndTime(slotEnd);
            reservation.setAttendees(dto.getAttendees());
            reservation.setStatus(ReservationStatus.PENDING);
            reservationMapper.insert(reservation);
            successCount++;
        }

        Map<String, Object> result = new HashMap<>();
        result.put("successCount", successCount);
        result.put("failedCount", failedSlots.size());
        result.put("failedSlots", failedSlots);
        result.put("totalRequested", weekCount);
        return result;
    }

    @Override
    public List<Reservation> findNoShows() {
        return reservationMapper.findNoShows();
    }
}
