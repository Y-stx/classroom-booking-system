package com.classroom.reservation.controller;

import com.classroom.reservation.common.PageResult;
import com.classroom.reservation.common.Result;
import com.classroom.reservation.dto.ClassroomQueryDTO;
import com.classroom.reservation.entity.Classroom;
import com.classroom.reservation.service.ClassroomService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@Tag(name = "教室管理", description = "教室CRUD与查询")
@RestController
@RequestMapping("/api/classrooms")
public class ClassroomController {

    private final ClassroomService classroomService;

    public ClassroomController(ClassroomService classroomService) {
        this.classroomService = classroomService;
    }

    @Operation(summary = "分页查询教室")
    @GetMapping
    public Result<PageResult<Classroom>> findPage(ClassroomQueryDTO query) {
        return Result.success(classroomService.findPage(query));
    }

    @Operation(summary = "查询指定时段空闲教室")
    @GetMapping("/available")
    public Result<List<Classroom>> findAvailable(
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startTime,
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endTime) {
        return Result.success(classroomService.findAvailable(startTime, endTime));
    }

    @Operation(summary = "查询教室详情")
    @GetMapping("/{id}")
    public Result<Classroom> findById(@PathVariable Long id) {
        return Result.success(classroomService.findById(id));
    }

    @Operation(summary = "新增教室（管理员）")
    @PostMapping
    public Result<Classroom> create(@RequestBody Classroom classroom, HttpServletRequest request) {
        checkAdmin(request);
        return Result.success("创建成功", classroomService.create(classroom));
    }

    @Operation(summary = "修改教室（管理员）")
    @PutMapping("/{id}")
    public Result<Classroom> update(@PathVariable Long id, @RequestBody Classroom classroom, HttpServletRequest request) {
        checkAdmin(request);
        classroom.setId(id);
        return Result.success("修改成功", classroomService.update(classroom));
    }

    @Operation(summary = "删除教室（管理员）")
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id, HttpServletRequest request) {
        checkAdmin(request);
        classroomService.delete(id);
        return Result.success();
    }

    @Operation(summary = "更新教室状态（管理员）")
    @PatchMapping("/{id}/status")
    public Result<Void> updateStatus(@PathVariable Long id, @RequestParam String status, HttpServletRequest request) {
        checkAdmin(request);
        classroomService.updateStatus(id, status);
        return Result.success();
    }

    private void checkAdmin(HttpServletRequest request) {
        String role = (String) request.getAttribute("role");
        if (!"ADMIN".equals(role)) {
            throw new com.classroom.reservation.exception.BusinessException(403, "只有管理员才能执行此操作");
        }
    }
}
