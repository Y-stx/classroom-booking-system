package com.classroom.reservation.controller;

import com.classroom.reservation.common.PageResult;
import com.classroom.reservation.common.Result;
import com.classroom.reservation.dto.ApprovalDTO;
import com.classroom.reservation.dto.ReservationQueryDTO;
import com.classroom.reservation.entity.Reservation;
import com.classroom.reservation.exception.BusinessException;
import com.classroom.reservation.service.ApprovalService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.*;

@Tag(name = "审批管理", description = "待审批列表、通过、驳回")
@RestController
@RequestMapping("/api/approvals")
public class ApprovalController {

    private final ApprovalService approvalService;

    public ApprovalController(ApprovalService approvalService) {
        this.approvalService = approvalService;
    }

    @Operation(summary = "待审批列表（管理员）")
    @GetMapping("/pending")
    public Result<PageResult<Reservation>> pending(ReservationQueryDTO query, HttpServletRequest request) {
        checkAdmin(request);
        return Result.success(approvalService.findPending(query));
    }

    @Operation(summary = "通过审批（管理员）")
    @PostMapping("/{id}/approve")
    public Result<Void> approve(@PathVariable Long id, HttpServletRequest request) {
        Long approverId = (Long) request.getAttribute("userId");
        checkAdmin(request);
        approvalService.approve(id, approverId);
        return Result.success();
    }

    @Operation(summary = "驳回审批（管理员）")
    @PostMapping("/{id}/reject")
    public Result<Void> reject(@PathVariable Long id, @RequestBody ApprovalDTO dto, HttpServletRequest request) {
        Long approverId = (Long) request.getAttribute("userId");
        checkAdmin(request);
        approvalService.reject(id, approverId, dto.getRejectReason());
        return Result.success();
    }

    private void checkAdmin(HttpServletRequest request) {
        String role = (String) request.getAttribute("role");
        if (!"ADMIN".equals(role)) {
            throw new BusinessException(403, "只有管理员才能执行审批操作");
        }
    }
}
