package com.classroom.reservation.entity;

import lombok.Data;
import java.time.LocalDateTime;

/**
 * 用户实体类
 */
@Data
public class SysUser {

    private Long id;
    private String username;
    private String password;
    private String name;
    private String role;
    private String department;
    private String phone;
    private String email;
    private String avatar;
    private Integer status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
