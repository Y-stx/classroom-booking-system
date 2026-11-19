package com.classroom.reservation.service.impl;

import com.classroom.reservation.common.PageResult;
import com.classroom.reservation.dto.ClassroomQueryDTO;
import com.classroom.reservation.entity.Classroom;
import com.classroom.reservation.exception.BusinessException;
import com.classroom.reservation.mapper.ClassroomMapper;
import com.classroom.reservation.service.ClassroomService;
import com.classroom.reservation.utils.RedisUtil;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.List;

@Service
public class ClassroomServiceImpl implements ClassroomService {

    private final ClassroomMapper classroomMapper;
    private final RedisUtil redisUtil;

    public ClassroomServiceImpl(ClassroomMapper classroomMapper, RedisUtil redisUtil) {
        this.classroomMapper = classroomMapper;
        this.redisUtil = redisUtil;
    }

    @Override
    public PageResult<Classroom> findPage(ClassroomQueryDTO query) {
        String cacheKey = "classroom:page:" + query.getNormalizedPage() + ":" + query.getNormalizedPageSize();
        // 查询数据库
        int offset = (query.getNormalizedPage() - 1) * query.getNormalizedPageSize();
        List<Classroom> list = classroomMapper.findPage(
                query.getBuilding(), query.getType(), query.getStatus(),
                query.getNormalizedKeyword(), query.getMinCapacity(),
                offset, query.getNormalizedPageSize());
        long total = classroomMapper.count(
                query.getBuilding(), query.getType(), query.getStatus(),
                query.getNormalizedKeyword(), query.getMinCapacity());
        return PageResult.of(list, total, query.getNormalizedPage(), query.getNormalizedPageSize());
    }

    @Override
    public Classroom findById(Long id) {
        Classroom classroom = classroomMapper.findById(id);
        if (classroom == null) {
            throw new BusinessException(404, "教室不存在");
        }
        return classroom;
    }

    @Override
    public Classroom create(Classroom classroom) {
        if (classroom.getStatus() == null) {
            classroom.setStatus("AVAILABLE");
        }
        classroomMapper.insert(classroom);
        clearCache();
        return classroom;
    }

    @Override
    public Classroom update(Classroom classroom) {
        Classroom existing = classroomMapper.findById(classroom.getId());
        if (existing == null) {
            throw new BusinessException(404, "教室不存在");
        }
        classroomMapper.update(classroom);
        clearCache();
        return classroomMapper.findById(classroom.getId());
    }

    @Override
    public void delete(Long id) {
        classroomMapper.deleteById(id);
        clearCache();
    }

    @Override
    public void updateStatus(Long id, String status) {
        Classroom existing = classroomMapper.findById(id);
        if (existing == null) {
            throw new BusinessException(404, "教室不存在");
        }
        classroomMapper.updateStatus(id, status);
        clearCache();
    }

    private void clearCache() {
        redisUtil.deleteByPattern("classroom:*");
    }

    @Override
    public List<Classroom> findAvailable(LocalDateTime startTime, LocalDateTime endTime) {
        if (startTime == null || endTime == null) {
            throw new BusinessException("开始时间和结束时间不能为空");
        }
        if (!startTime.isBefore(endTime)) {
            throw new BusinessException("开始时间必须早于结束时间");
        }
        return classroomMapper.selectAvailableClassrooms(startTime, endTime);
    }
}
