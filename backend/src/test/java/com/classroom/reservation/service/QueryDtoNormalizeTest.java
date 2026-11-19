package com.classroom.reservation.service;

import com.classroom.reservation.dto.ClassroomQueryDTO;
import com.classroom.reservation.dto.ReservationQueryDTO;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * DTO 分页参数归一化单元测试
 */
@DisplayName("分页参数归一化测试")
class QueryDtoNormalizeTest {

    @Test
    @DisplayName("null page 默认返回 1")
    void nullPageDefaultsTo1() {
        ClassroomQueryDTO dto = new ClassroomQueryDTO();
        dto.setPage(null);
        assertEquals(1, dto.getNormalizedPage());
    }

    @Test
    @DisplayName("负数 page 默认返回 1")
    void negativePageDefaultsTo1() {
        ClassroomQueryDTO dto = new ClassroomQueryDTO();
        dto.setPage(-5);
        assertEquals(1, dto.getNormalizedPage());
    }

    @Test
    @DisplayName("null pageSize 默认返回 10")
    void nullPageSizeDefaultsTo10() {
        ClassroomQueryDTO dto = new ClassroomQueryDTO();
        dto.setPageSize(null);
        assertEquals(10, dto.getNormalizedPageSize());
    }

    @Test
    @DisplayName("pageSize 超过 100 被截断为 100")
    void pageSizeCappedAt100() {
        ClassroomQueryDTO dto = new ClassroomQueryDTO();
        dto.setPageSize(500);
        assertEquals(100, dto.getNormalizedPageSize());
    }

    @Test
    @DisplayName("正常 page 和 pageSize 保持原值")
    void normalValuesPreserved() {
        ClassroomQueryDTO dto = new ClassroomQueryDTO();
        dto.setPage(3);
        dto.setPageSize(20);
        assertEquals(3, dto.getNormalizedPage());
        assertEquals(20, dto.getNormalizedPageSize());
    }

    @Test
    @DisplayName("keyword 前后空格被 trim")
    void keywordIsTrimmed() {
        ReservationQueryDTO dto = new ReservationQueryDTO();
        dto.setKeyword("  会议  ");
        assertEquals("会议", dto.getNormalizedKeyword());
    }

    @Test
    @DisplayName("null keyword 返回 null")
    void nullKeywordReturnsNull() {
        ReservationQueryDTO dto = new ReservationQueryDTO();
        dto.setKeyword(null);
        assertNull(dto.getNormalizedKeyword());
    }
}
