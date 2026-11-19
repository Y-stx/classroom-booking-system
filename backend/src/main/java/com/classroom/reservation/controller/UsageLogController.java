package com.classroom.reservation.controller;

import com.classroom.reservation.common.PageResult;
import com.classroom.reservation.common.Result;
import com.classroom.reservation.dto.CheckInDTO;
import com.classroom.reservation.dto.CheckOutDTO;
import com.classroom.reservation.entity.UsageLog;
import com.classroom.reservation.service.UsageLogService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@Tag(name = "使用登记", description = "签到、签退、使用记录")
@RestController
@RequestMapping("/api/usage")
public class UsageLogController {

    private final UsageLogService usageLogService;

    public UsageLogController(UsageLogService usageLogService) {
        this.usageLogService = usageLogService;
    }

    @Operation(summary = "签到")
    @PostMapping("/check-in")
    public Result<UsageLog> checkIn(@Valid @RequestBody CheckInDTO dto, HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        return Result.success("签到成功", usageLogService.checkIn(dto.getReservationId(), userId));
    }

    @Operation(summary = "签退（含设备状况填报）")
    @PostMapping("/check-out")
    public Result<UsageLog> checkOut(@Valid @RequestBody CheckOutDTO dto, HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        return Result.success("签退成功", usageLogService.checkOut(dto, userId));
    }

    @Operation(summary = "使用记录列表")
    @GetMapping("/list")
    public Result<PageResult<UsageLog>> list(
            @RequestParam(required = false) Long classroomId,
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int pageSize,
            HttpServletRequest request) {
        String role = (String) request.getAttribute("role");
        Long userId = (Long) request.getAttribute("userId");
        // 管理员可看全部，其他角色只看自己的
        Long queryUserId = "ADMIN".equals(role) ? null : userId;
        return Result.success(usageLogService.findPage(queryUserId, classroomId, keyword, page, pageSize));
    }
}
