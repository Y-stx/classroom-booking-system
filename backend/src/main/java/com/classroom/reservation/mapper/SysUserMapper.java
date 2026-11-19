package com.classroom.reservation.mapper;

import com.classroom.reservation.entity.SysUser;
import org.apache.ibatis.annotations.*;

import java.util.List;

/**
 * 用户 Mapper
 */
@Mapper
public interface SysUserMapper {

    @Insert("INSERT INTO sys_user(username, password, name, role, department, phone, email, avatar, status) " +
            "VALUES(#{username}, #{password}, #{name}, #{role}, #{department}, #{phone}, #{email}, #{avatar}, #{status})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(SysUser user);

    @Update("UPDATE sys_user SET name=#{name}, department=#{department}, phone=#{phone}, email=#{email}, " +
            "avatar=#{avatar}, status=#{status} WHERE id=#{id}")
    int update(SysUser user);

    @Update("UPDATE sys_user SET password=#{password} WHERE id=#{id}")
    int updatePassword(@Param("id") Long id, @Param("password") String password);

    @Select("SELECT * FROM sys_user WHERE id=#{id}")
    SysUser findById(@Param("id") Long id);

    @Select("SELECT * FROM sys_user WHERE username=#{username}")
    SysUser findByUsername(@Param("username") String username);

    @Select("<script>" +
            "SELECT * FROM sys_user" +
            "<where>" +
            "  <if test='role != null and role != \"\"'> AND role = #{role}</if>" +
            "  <if test='keyword != null and keyword != \"\"'> AND (name LIKE CONCAT('%',#{keyword},'%') OR username LIKE CONCAT('%',#{keyword},'%'))</if>" +
            "</where>" +
            " ORDER BY created_at DESC" +
            " LIMIT #{offset}, #{limit}" +
            "</script>")
    List<SysUser> findPage(@Param("role") String role, @Param("keyword") String keyword,
                           @Param("offset") int offset, @Param("limit") int limit);

    @Select("<script>" +
            "SELECT COUNT(*) FROM sys_user" +
            "<where>" +
            "  <if test='role != null and role != \"\"'> AND role = #{role}</if>" +
            "  <if test='keyword != null and keyword != \"\"'> AND (name LIKE CONCAT('%',#{keyword},'%') OR username LIKE CONCAT('%',#{keyword},'%'))</if>" +
            "</where>" +
            "</script>")
    long count(@Param("role") String role, @Param("keyword") String keyword);

    @Select("SELECT COUNT(*) FROM sys_user")
    long countAll();

    @Delete("DELETE FROM sys_user WHERE id=#{id}")
    int deleteById(@Param("id") Long id);
}
