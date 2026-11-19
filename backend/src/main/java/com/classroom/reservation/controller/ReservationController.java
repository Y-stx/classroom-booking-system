package com.classroom.reservation.controller;

import com.classroom.reservation.common.PageResult;
import com.classroom.reservation.common.Result;
import com.classroom.reservation.dto.BatchReserveDTO;
import com.classroom.reservation.dto.ReservationCreateDTO;
import com.classroom.reservation.dto.ReservationQueryDTO;
import com.classroom.reservation.entity.Reservation;
import com.classroom.reservation.service.ReservationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@Tag(name = "预约管理", description = "创建预约、我的预约、取消预约")
@RestController
@RequestMapping("/api/reservations")
public class ReservationController {

    private final ReservationService reservationService;

    public ReservationController(ReservationService reservationService) {
        this.reservationService = reservationService;
    }

    @Operation(summary = "创建预约")
    @PostMapping
    public Result<Reservation> create(@Valid @RequestBody ReservationCreateDTO dto, HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        return Result.success("预约提交成功，等待审批", reservationService.create(dto, userId));
    }

    @Operation(summary = "我的预约列表")
    @GetMapping("/my")
    public Result<PageResult<Reservation>> myReservations(ReservationQueryDTO query, HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        return Result.success(reservationService.findMyReservations(query, userId));
    }

    @Operation(summary = "预约列表（管理员查看全部）")
    @GetMapping
    public Result<PageResult<Reservation>> findAll(ReservationQueryDTO query, HttpServletRequest request) {
        String role = (String) request.getAttribute("role");
        if (!"ADMIN".equals(role)) {
            // 非管理员只能看自己的
            Long userId = (Long) request.getAttribute("userId");
            return Result.success(reservationService.findMyReservations(query, userId));
        }
        return Result.success(reservationService.findAll(query));
    }

    @Operation(summary = "预约详情")
    @GetMapping("/{id}")
    public Result<Reservation> findById(@PathVariable Long id) {
        return Result.success(reservationService.findById(id));
    }

    @Operation(summary = "取消预约")
    @PutMapping("/{id}/cancel")
    public Result<Void> cancel(@PathVariable Long id, @RequestBody(required = false) Map<String, String> body, HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        String reason = body != null ? body.get("reason") : null;
        reservationService.cancel(id, userId, reason);
        return Result.success();
    }

    @Operation(summary = "批量预约（按周次生成）")
    @PostMapping("/batch")
    public Result<Map<String, Object>> batchReserve(@Valid @RequestBody BatchReserveDTO dto, HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        Map<String, Object> result = reservationService.batchReserve(dto, userId);
        String msg = String.format("成功预约 %d 条，失败 %d 条", result.get("successCount"), result.get("failedCount"));
        return Result.success(msg, result);
    }

    @Operation(summary = "爽约预约列表（管理员）")
    @GetMapping("/no-shows")
    public Result<List<Reservation>> noShows(HttpServletRequest request) {
        String role = (String) request.getAttribute("role");
        if (!"ADMIN".equals(role)) {
            throw new com.classroom.reservation.exception.BusinessException(403, "只有管理员才能查看爽约记录");
        }
        return Result.success(reservationService.findNoShows());
    }
}
