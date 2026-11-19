package com.classroom.reservation.service;

import com.classroom.reservation.entity.SysUser;

import java.util.Map;

public interface AuthService {

    Map<String, Object> login(String username, String password);

    void logout(String token);

    SysUser getCurrentUser(Long userId);
}
