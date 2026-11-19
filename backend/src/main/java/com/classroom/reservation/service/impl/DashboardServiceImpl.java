package com.classroom.reservation.service.impl;

import com.classroom.reservation.dto.ClassroomUsageDTO;
import com.classroom.reservation.dto.WeeklyUsageDTO;
import com.classroom.reservation.mapper.ClassroomMapper;
import com.classroom.reservation.mapper.ReservationMapper;
import com.classroom.reservation.mapper.SysUserMapper;
import com.classroom.reservation.mapper.UsageLogMapper;
import com.classroom.reservation.service.DashboardService;
import com.classroom.reservation.utils.RedisUtil;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class DashboardServiceImpl implements DashboardService {

    private final ClassroomMapper classroomMapper;
    private final ReservationMapper reservationMapper;
    private final SysUserMapper userMapper;
    private final UsageLogMapper usageLogMapper;
    private final RedisUtil redisUtil;

    public DashboardServiceImpl(ClassroomMapper classroomMapper, ReservationMapper reservationMapper,
                                 SysUserMapper userMapper, UsageLogMapper usageLogMapper, RedisUtil redisUtil) {
        this.classroomMapper = classroomMapper;
        this.reservationMapper = reservationMapper;
        this.userMapper = userMapper;
        this.usageLogMapper = usageLogMapper;
        this.redisUtil = redisUtil;
    }

    @Override
    public Map<String, Object> getStats() {
        // 尝试从缓存读取
        String cacheKey = "dashboard:stats";
        // 直接查询（缓存可选，这里保持简单）
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalClassrooms", classroomMapper.countAll());
        stats.put("availableClassrooms", classroomMapper.countByStatus("AVAILABLE"));
        stats.put("maintenanceClassrooms", classroomMapper.countByStatus("MAINTENANCE"));
        stats.put("totalUsers", userMapper.countAll());
        stats.put("totalReservations", reservationMapper.countAll());
        stats.put("pendingApprovals", reservationMapper.countByStatus("PENDING"));
        stats.put("approvedReservations", reservationMapper.countByStatus("APPROVED"));
        stats.put("completedReservations", reservationMapper.countByStatus("COMPLETED"));
        stats.put("todayReservations", reservationMapper.countToday());
        stats.put("rejectedReservations", reservationMapper.countByStatus("REJECTED"));
        stats.put("cancelledReservations", reservationMapper.countByStatus("CANCELLED"));

        return stats;
    }

    @Override
    public List<ClassroomUsageDTO> getClassroomUsage() {
        List<ClassroomUsageDTO> list = reservationMapper.countByClassroom();
        long total = list.stream().mapToLong(ClassroomUsageDTO::getReservationCount).sum();
        if (total > 0) {
            for (ClassroomUsageDTO dto : list) {
                double rate = Math.round(dto.getReservationCount() * 10000.0 / total) / 100.0;
                dto.setUsageRate(rate);
            }
        } else {
            for (ClassroomUsageDTO dto : list) {
                dto.setUsageRate(0.0);
            }
        }
        return list;
    }

    @Override
    public List<WeeklyUsageDTO> getWeeklyUsage(int weeks) {
        if (weeks <= 0) weeks = 8;
        return reservationMapper.countByWeek(weeks);
    }
}
