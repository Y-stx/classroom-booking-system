package com.classroom.reservation.controller;

import com.classroom.reservation.common.Result;
import com.classroom.reservation.dto.ClassroomUsageDTO;
import com.classroom.reservation.dto.WeeklyUsageDTO;
import com.classroom.reservation.service.DashboardService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@Tag(name = "概览统计", description = "首页统计卡片数据")
@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    private final DashboardService dashboardService;

    public DashboardController(DashboardService dashboardService) {
        this.dashboardService = dashboardService;
    }

    @Operation(summary = "获取统计数据")
    @GetMapping("/stats")
    public Result<Map<String, Object>> getStats() {
        return Result.success(dashboardService.getStats());
    }

    @Operation(summary = "按教室统计预约次数与使用率")
    @GetMapping("/usage/classroom")
    public Result<List<ClassroomUsageDTO>> getClassroomUsage() {
        return Result.success(dashboardService.getClassroomUsage());
    }

    @Operation(summary = "按周统计预约次数")
    @GetMapping("/usage/weekly")
    public Result<List<WeeklyUsageDTO>> getWeeklyUsage(@RequestParam(defaultValue = "8") int weeks) {
        return Result.success(dashboardService.getWeeklyUsage(weeks));
    }
}
