package com.classroom.reservation.service.impl;

import com.classroom.reservation.entity.SysUser;
import com.classroom.reservation.exception.BusinessException;
import com.classroom.reservation.mapper.SysUserMapper;
import com.classroom.reservation.security.JwtUtil;
import com.classroom.reservation.service.AuthService;
import com.classroom.reservation.utils.RedisUtil;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

@Service
public class AuthServiceImpl implements AuthService {

    private final SysUserMapper userMapper;
    private final JwtUtil jwtUtil;
    private final RedisUtil redisUtil;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    public AuthServiceImpl(SysUserMapper userMapper, JwtUtil jwtUtil, RedisUtil redisUtil) {
        this.userMapper = userMapper;
        this.jwtUtil = jwtUtil;
        this.redisUtil = redisUtil;
    }

    @Override
    public Map<String, Object> login(String username, String password) {
        SysUser user = userMapper.findByUsername(username);
        if (user == null) {
            throw new BusinessException(401, "用户名或密码错误");
        }
        if (user.getStatus() != null && user.getStatus() == 0) {
            throw new BusinessException(403, "账号已被禁用，请联系管理员");
        }
        if (!passwordEncoder.matches(password, user.getPassword())) {
            throw new BusinessException(401, "用户名或密码错误");
        }

        String token = jwtUtil.generateToken(user.getId(), user.getUsername(), user.getRole());
        redisUtil.set("jwt:" + user.getId() + ":" + token, "1", Duration.ofMillis(jwtUtil.getExpiration()));

        Map<String, Object> result = new HashMap<>();
        result.put("token", token);
        Map<String, Object> userInfo = new HashMap<>();
        userInfo.put("id", user.getId());
        userInfo.put("username", user.getUsername());
        userInfo.put("name", user.getName());
        userInfo.put("role", user.getRole());
        userInfo.put("department", user.getDepartment());
        userInfo.put("avatar", user.getAvatar());
        result.put("user", userInfo);
        return result;
    }

    @Override
    public void logout(String token) {
        Long userId = jwtUtil.getUserId(token);
        redisUtil.delete("jwt:" + userId + ":" + token);
    }

    @Override
    public SysUser getCurrentUser(Long userId) {
        SysUser user = userMapper.findById(userId);
        if (user == null) {
            throw new BusinessException(404, "用户不存在");
        }
        user.setPassword(null);
        return user;
    }
}
