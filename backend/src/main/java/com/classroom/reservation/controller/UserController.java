package com.classroom.reservation.controller;

import com.classroom.reservation.common.PageResult;
import com.classroom.reservation.common.Result;
import com.classroom.reservation.entity.SysUser;
import com.classroom.reservation.exception.BusinessException;
import com.classroom.reservation.mapper.SysUserMapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;

@Tag(name = "用户管理", description = "用户CRUD（管理员）")
@RestController
@RequestMapping("/api/users")
public class UserController {

    private final SysUserMapper userMapper;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    public UserController(SysUserMapper userMapper) {
        this.userMapper = userMapper;
    }

    @Operation(summary = "分页查询用户（管理员）")
    @GetMapping
    public Result<PageResult<SysUser>> findPage(
            @RequestParam(required = false) String role,
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int pageSize,
            HttpServletRequest request) {
        checkAdmin(request);
        page = Math.max(page, 1);
        pageSize = Math.max(1, Math.min(pageSize, 100));
        int offset = (page - 1) * pageSize;
        var list = userMapper.findPage(role, keyword, offset, pageSize);
        list.forEach(u -> u.setPassword(null));
        long total = userMapper.count(role, keyword);
        return Result.success(PageResult.of(list, total, page, pageSize));
    }

    @Operation(summary = "新增用户（管理员）")
    @PostMapping
    public Result<SysUser> create(@RequestBody SysUser user, HttpServletRequest request) {
        checkAdmin(request);
        if (user.getUsername() == null || user.getUsername().isBlank()) {
            throw new BusinessException("用户名不能为空");
        }
        if (user.getPassword() == null || user.getPassword().isBlank()) {
            throw new BusinessException("请设置初始密码");
        }
        if (user.getName() == null || user.getName().isBlank()) {
            throw new BusinessException("姓名不能为空");
        }
        if (userMapper.findByUsername(user.getUsername()) != null) {
            throw new BusinessException("用户名已存在");
        }
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        if (user.getStatus() == null) user.setStatus(1);
        userMapper.insert(user);
        user.setPassword(null);
        return Result.success("创建成功", user);
    }

    @Operation(summary = "修改用户（管理员）")
    @PutMapping("/{id}")
    public Result<SysUser> update(@PathVariable Long id, @RequestBody SysUser user, HttpServletRequest request) {
        checkAdmin(request);
        user.setId(id);
        userMapper.update(user);
        SysUser updated = userMapper.findById(id);
        updated.setPassword(null);
        return Result.success("修改成功", updated);
    }

    @Operation(summary = "删除用户（管理员）")
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id, HttpServletRequest request) {
        checkAdmin(request);
        userMapper.deleteById(id);
        return Result.success();
    }

    @Operation(summary = "修改密码")
    @PutMapping("/password")
    public Result<Void> updatePassword(@RequestParam String oldPassword, @RequestParam String newPassword, HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        SysUser user = userMapper.findById(userId);
        if (!passwordEncoder.matches(oldPassword, user.getPassword())) {
            throw new BusinessException("旧密码错误");
        }
        userMapper.updatePassword(userId, passwordEncoder.encode(newPassword));
        return Result.success();
    }

    private void checkAdmin(HttpServletRequest request) {
        String role = (String) request.getAttribute("role");
        if (!"ADMIN".equals(role)) {
            throw new BusinessException(403, "只有管理员才能执行此操作");
        }
    }
}
