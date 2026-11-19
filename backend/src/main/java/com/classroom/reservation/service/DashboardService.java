package com.classroom.reservation.service;

import com.classroom.reservation.dto.ClassroomUsageDTO;
import com.classroom.reservation.dto.WeeklyUsageDTO;

import java.util.List;
import java.util.Map;

public interface DashboardService {

    Map<String, Object> getStats();

    /**
     * 按教室统计预约次数与使用率
     */
    List<ClassroomUsageDTO> getClassroomUsage();

    /**
     * 按周统计预约次数
     * @param weeks 最近多少周
     */
    List<WeeklyUsageDTO> getWeeklyUsage(int weeks);
}
