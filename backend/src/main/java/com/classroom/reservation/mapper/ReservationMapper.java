package com.classroom.reservation.mapper;

import com.classroom.reservation.dto.ClassroomUsageDTO;
import com.classroom.reservation.dto.WeeklyUsageDTO;
import com.classroom.reservation.entity.Reservation;
import com.classroom.reservation.enums.ReservationStatus;
import com.classroom.reservation.enums.ReservationStatusTypeHandler;
import org.apache.ibatis.annotations.*;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 预约 Mapper
 */
@Mapper
public interface ReservationMapper {

    @Insert("INSERT INTO reservation(classroom_id, user_id, title, purpose, start_time, end_time, attendees, status) " +
            "VALUES(#{classroomId}, #{userId}, #{title}, #{purpose}, #{startTime}, #{endTime}, #{attendees}, #{status})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(Reservation reservation);

    @Update("UPDATE reservation SET status=#{status} WHERE id=#{id}")
    int updateStatus(@Param("id") Long id, @Param("status") ReservationStatus status);

    @Update("UPDATE reservation SET status=#{status}, approver_id=#{approverId}, approve_time=#{approveTime}, " +
            "reject_reason=#{rejectReason} WHERE id=#{id}")
    int approve(@Param("id") Long id, @Param("status") ReservationStatus status,
                @Param("approverId") Long approverId, @Param("approveTime") LocalDateTime approveTime,
                @Param("rejectReason") String rejectReason);

    @Update("UPDATE reservation SET status=#{status}, cancel_reason=#{cancelReason} WHERE id=#{id}")
    int cancel(@Param("id") Long id, @Param("status") ReservationStatus status,
               @Param("cancelReason") String cancelReason);

    @Select("SELECT * FROM reservation WHERE id=#{id}")
    @Results(id = "reservationResult", value = {
            @Result(column = "status", property = "status", typeHandler = ReservationStatusTypeHandler.class)
    })
    Reservation findById(@Param("id") Long id);

    /**
     * 联表查询（带教室名、用户名等关联字段）
     */
    @Select("<script>" +
            "SELECT r.*, c.name AS classroom_name, c.building AS building, " +
            "u.name AS user_name, a.name AS approver_name " +
            "FROM reservation r " +
            "LEFT JOIN classroom c ON r.classroom_id = c.id " +
            "LEFT JOIN sys_user u ON r.user_id = u.id " +
            "LEFT JOIN sys_user a ON r.approver_id = a.id" +
            "<where>" +
            "  <if test='userId != null'> AND r.user_id = #{userId}</if>" +
            "  <if test='classroomId != null'> AND r.classroom_id = #{classroomId}</if>" +
            "  <if test='status != null and status != \"\"'> AND r.status = #{status}</if>" +
            "  <if test='keyword != null and keyword != \"\"'> AND r.title LIKE CONCAT('%',#{keyword},'%')</if>" +
            "</where>" +
            " ORDER BY r.created_at DESC" +
            " LIMIT #{offset}, #{limit}" +
            "</script>")
    @ResultMap("reservationResult")
    List<Reservation> findPageWithJoin(@Param("userId") Long userId, @Param("classroomId") Long classroomId,
                                        @Param("status") String status, @Param("keyword") String keyword,
                                        @Param("offset") int offset, @Param("limit") int limit);

    @Select("<script>" +
            "SELECT COUNT(*) FROM reservation r" +
            "<where>" +
            "  <if test='userId != null'> AND r.user_id = #{userId}</if>" +
            "  <if test='classroomId != null'> AND r.classroom_id = #{classroomId}</if>" +
            "  <if test='status != null and status != \"\"'> AND r.status = #{status}</if>" +
            "  <if test='keyword != null and keyword != \"\"'> AND r.title LIKE CONCAT('%',#{keyword},'%')</if>" +
            "</where>" +
            "</script>")
    long count(@Param("userId") Long userId, @Param("classroomId") Long classroomId,
               @Param("status") String status, @Param("keyword") String keyword);

    /**
     * 时间冲突检测：查询同一教室在指定时间段内已有的有效预约（PENDING/APPROVED）
     */
    @Select("SELECT r.* FROM reservation r " +
            "WHERE r.classroom_id = #{classroomId} " +
            "AND r.status IN ('PENDING', 'APPROVED') " +
            "AND r.id != IFNULL(#{excludeId}, 0) " +
            "AND r.start_time < #{endTime} AND r.end_time > #{startTime}")
    @ResultMap("reservationResult")
    List<Reservation> findConflicts(@Param("classroomId") Long classroomId,
                                    @Param("startTime") LocalDateTime startTime,
                                    @Param("endTime") LocalDateTime endTime,
                                    @Param("excludeId") Long excludeId);

    @Select("SELECT COUNT(*) FROM reservation WHERE status=#{status}")
    long countByStatus(@Param("status") String status);

    @Select("SELECT COUNT(*) FROM reservation")
    long countAll();

    @Select("SELECT COUNT(*) FROM reservation WHERE DATE(created_at) = CURDATE()")
    long countToday();

    /**
     * 按教室统计预约次数（含已取消/已驳回，仅排除已删除；此处统计所有状态的预约记录数）
     */
    @Select("SELECT c.id AS classroom_id, c.name AS classroom_name, c.building, " +
            "COUNT(r.id) AS reservation_count " +
            "FROM classroom c " +
            "LEFT JOIN reservation r ON r.classroom_id = c.id " +
            "GROUP BY c.id, c.name, c.building " +
            "ORDER BY reservation_count DESC")
    @Results({
            @Result(column = "classroom_id", property = "classroomId"),
            @Result(column = "classroom_name", property = "classroomName"),
            @Result(column = "building", property = "building"),
            @Result(column = "reservation_count", property = "reservationCount")
    })
    List<ClassroomUsageDTO> countByClassroom();

    /**
     * 按周统计预约次数（最近 N 周）
     */
    @Select("SELECT CONCAT(YEAR(start_time), '-W', LPAD(WEEK(start_time, 1), 2, '0')) AS week_label, " +
            "COUNT(*) AS reservation_count " +
            "FROM reservation " +
            "WHERE start_time IS NOT NULL " +
            "AND start_time >= DATE_SUB(CURDATE(), INTERVAL #{weeks} WEEK) " +
            "GROUP BY YEAR(start_time), WEEK(start_time, 1) " +
            "ORDER BY week_label ASC")
    @Results({
            @Result(column = "week_label", property = "weekLabel"),
            @Result(column = "reservation_count", property = "reservationCount")
    })
    List<WeeklyUsageDTO> countByWeek(@Param("weeks") int weeks);

    /**
     * 查询爽约预约：状态为 APPROVED、已结束（end_time < NOW）且无签到记录
     */
    @Select("SELECT r.*, c.name AS classroom_name, c.building AS building, " +
            "u.name AS user_name " +
            "FROM reservation r " +
            "LEFT JOIN classroom c ON r.classroom_id = c.id " +
            "LEFT JOIN sys_user u ON r.user_id = u.id " +
            "WHERE r.status = 'APPROVED' " +
            "AND r.end_time < NOW() " +
            "AND NOT EXISTS (SELECT 1 FROM usage_log ul WHERE ul.reservation_id = r.id) " +
            "ORDER BY r.end_time DESC")
    @ResultMap("reservationResult")
    List<Reservation> findNoShows();
}
