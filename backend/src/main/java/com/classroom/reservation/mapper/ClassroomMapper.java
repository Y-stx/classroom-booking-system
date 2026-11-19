package com.classroom.reservation.mapper;

import com.classroom.reservation.entity.Classroom;
import org.apache.ibatis.annotations.*;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 教室 Mapper
 */
@Mapper
public interface ClassroomMapper {

    @Insert("INSERT INTO classroom(name, building, floor, capacity, type, equipment, status, image_url, remark) " +
            "VALUES(#{name}, #{building}, #{floor}, #{capacity}, #{type}, #{equipment}, #{status}, #{imageUrl}, #{remark})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(Classroom classroom);

    @Update("UPDATE classroom SET name=#{name}, building=#{building}, floor=#{floor}, capacity=#{capacity}, " +
            "type=#{type}, equipment=#{equipment}, status=#{status}, image_url=#{imageUrl}, remark=#{remark} WHERE id=#{id}")
    int update(Classroom classroom);

    @Update("UPDATE classroom SET status=#{status} WHERE id=#{id}")
    int updateStatus(@Param("id") Long id, @Param("status") String status);

    @Delete("DELETE FROM classroom WHERE id=#{id}")
    int deleteById(@Param("id") Long id);

    @Select("SELECT * FROM classroom WHERE id=#{id}")
    Classroom findById(@Param("id") Long id);

    @Select("SELECT * FROM classroom ORDER BY building, name")
    List<Classroom> findAll();

    /**
     * 分页查询（带条件筛选）
     */
    @Select("<script>" +
            "SELECT * FROM classroom" +
            "<where>" +
            "  <if test='building != null and building != \"\"'> AND building = #{building}</if>" +
            "  <if test='type != null and type != \"\"'> AND type = #{type}</if>" +
            "  <if test='status != null and status != \"\"'> AND status = #{status}</if>" +
            "  <if test='minCapacity != null'> AND capacity >= #{minCapacity}</if>" +
            "  <if test='keyword != null and keyword != \"\"'> AND (name LIKE CONCAT('%',#{keyword},'%') OR building LIKE CONCAT('%',#{keyword},'%'))</if>" +
            "</where>" +
            " ORDER BY building, name" +
            " LIMIT #{offset}, #{limit}" +
            "</script>")
    List<Classroom> findPage(@Param("building") String building, @Param("type") String type,
                             @Param("status") String status, @Param("keyword") String keyword,
                             @Param("minCapacity") Integer minCapacity,
                             @Param("offset") int offset, @Param("limit") int limit);

    @Select("<script>" +
            "SELECT COUNT(*) FROM classroom" +
            "<where>" +
            "  <if test='building != null and building != \"\"'> AND building = #{building}</if>" +
            "  <if test='type != null and type != \"\"'> AND type = #{type}</if>" +
            "  <if test='status != null and status != \"\"'> AND status = #{status}</if>" +
            "  <if test='minCapacity != null'> AND capacity >= #{minCapacity}</if>" +
            "  <if test='keyword != null and keyword != \"\"'> AND (name LIKE CONCAT('%',#{keyword},'%') OR building LIKE CONCAT('%',#{keyword},'%'))</if>" +
            "</where>" +
            "</script>")
    long count(@Param("building") String building, @Param("type") String type,
               @Param("status") String status, @Param("keyword") String keyword,
               @Param("minCapacity") Integer minCapacity);

    @Select("SELECT COUNT(*) FROM classroom")
    long countAll();

    @Select("SELECT COUNT(*) FROM classroom WHERE status=#{status}")
    long countByStatus(@Param("status") String status);

    /**
     * 查询指定时段内空闲（可用且无冲突预约）的教室
     * 排除条件：状态为 AVAILABLE，且该时段内没有 APPROVED 状态的预约
     */
    @Select("SELECT c.* FROM classroom c " +
            "WHERE c.status = 'AVAILABLE' " +
            "AND NOT EXISTS (" +
            "  SELECT 1 FROM reservation r " +
            "  WHERE r.classroom_id = c.id " +
            "  AND r.status = 'APPROVED' " +
            "  AND r.start_time < #{endTime} " +
            "  AND r.end_time > #{startTime}" +
            ") " +
            "ORDER BY c.building, c.name")
    List<Classroom> selectAvailableClassrooms(@Param("startTime") LocalDateTime startTime,
                                              @Param("endTime") LocalDateTime endTime);
}
