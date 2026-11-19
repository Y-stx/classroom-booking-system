package com.classroom.reservation.mapper;

import com.classroom.reservation.entity.UsageLog;
import org.apache.ibatis.annotations.*;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 使用登记 Mapper
 */
@Mapper
public interface UsageLogMapper {

    @Insert("INSERT INTO usage_log(reservation_id, classroom_id, user_id, check_in_time) " +
            "VALUES(#{reservationId}, #{classroomId}, #{userId}, #{checkInTime})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(UsageLog usageLog);

    @Update("UPDATE usage_log SET check_out_time=#{checkOutTime}, actual_attendees=#{actualAttendees}, " +
            "equipment_status=#{equipmentStatus}, cleanliness=#{cleanliness}, notes=#{notes} " +
            "WHERE id=#{id}")
    int checkOut(@Param("id") Long id, @Param("checkOutTime") LocalDateTime checkOutTime,
                 @Param("actualAttendees") Integer actualAttendees,
                 @Param("equipmentStatus") String equipmentStatus,
                 @Param("cleanliness") Integer cleanliness,
                 @Param("notes") String notes);

    @Select("SELECT * FROM usage_log WHERE reservation_id=#{reservationId}")
    UsageLog findByReservationId(@Param("reservationId") Long reservationId);

    @Select("SELECT * FROM usage_log WHERE id=#{id}")
    UsageLog findById(@Param("id") Long id);

    /**
     * 联表查询（带教室名、用户名、预约主题）
     */
    @Select("<script>" +
            "SELECT ul.*, c.name AS classroom_name, u.name AS user_name, r.title AS title " +
            "FROM usage_log ul " +
            "LEFT JOIN classroom c ON ul.classroom_id = c.id " +
            "LEFT JOIN sys_user u ON ul.user_id = u.id " +
            "LEFT JOIN reservation r ON ul.reservation_id = r.id" +
            "<where>" +
            "  <if test='userId != null'> AND ul.user_id = #{userId}</if>" +
            "  <if test='classroomId != null'> AND ul.classroom_id = #{classroomId}</if>" +
            "  <if test='keyword != null and keyword != \"\"'> AND r.title LIKE CONCAT('%',#{keyword},'%')</if>" +
            "</where>" +
            " ORDER BY ul.created_at DESC" +
            " LIMIT #{offset}, #{limit}" +
            "</script>")
    List<UsageLog> findPageWithJoin(@Param("userId") Long userId, @Param("classroomId") Long classroomId,
                                    @Param("keyword") String keyword,
                                    @Param("offset") int offset, @Param("limit") int limit);

    @Select("<script>" +
            "SELECT COUNT(*) FROM usage_log ul" +
            "<where>" +
            "  <if test='userId != null'> AND ul.user_id = #{userId}</if>" +
            "  <if test='classroomId != null'> AND ul.classroom_id = #{classroomId}</if>" +
            "  <if test='keyword != null and keyword != \"\"'> AND EXISTS(SELECT 1 FROM reservation r WHERE r.id = ul.reservation_id AND r.title LIKE CONCAT('%',#{keyword},'%'))</if>" +
            "</where>" +
            "</script>")
    long count(@Param("userId") Long userId, @Param("classroomId") Long classroomId,
               @Param("keyword") String keyword);
}
