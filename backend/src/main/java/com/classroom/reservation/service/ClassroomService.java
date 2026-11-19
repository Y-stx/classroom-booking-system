package com.classroom.reservation.service;

import com.classroom.reservation.common.PageResult;
import com.classroom.reservation.dto.ClassroomQueryDTO;
import com.classroom.reservation.entity.Classroom;

import java.time.LocalDateTime;
import java.util.List;

public interface ClassroomService {

    PageResult<Classroom> findPage(ClassroomQueryDTO query);

    Classroom findById(Long id);

    Classroom create(Classroom classroom);

    Classroom update(Classroom classroom);

    void delete(Long id);

    void updateStatus(Long id, String status);

    /**
     * 查询指定时段内空闲的教室
     */
    List<Classroom> findAvailable(LocalDateTime startTime, LocalDateTime endTime);
}
