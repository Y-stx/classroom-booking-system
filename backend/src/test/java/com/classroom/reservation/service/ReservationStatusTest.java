package com.classroom.reservation.service;

import com.classroom.reservation.enums.ReservationStatus;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * ReservationStatus 枚举状态流转单元测试
 */
@DisplayName("预约状态流转测试")
class ReservationStatusTest {

    @Test
    @DisplayName("PENDING 可以流转到 APPROVED")
    void pendingCanApprove() {
        assertTrue(ReservationStatus.PENDING.canTransitTo(ReservationStatus.APPROVED));
    }

    @Test
    @DisplayName("PENDING 可以流转到 REJECTED")
    void pendingCanReject() {
        assertTrue(ReservationStatus.PENDING.canTransitTo(ReservationStatus.REJECTED));
    }

    @Test
    @DisplayName("PENDING 可以流转到 CANCELLED")
    void pendingCanCancel() {
        assertTrue(ReservationStatus.PENDING.canTransitTo(ReservationStatus.CANCELLED));
    }

    @Test
    @DisplayName("APPROVED 可以流转到 COMPLETED")
    void approvedCanComplete() {
        assertTrue(ReservationStatus.APPROVED.canTransitTo(ReservationStatus.COMPLETED));
    }

    @Test
    @DisplayName("APPROVED 可以流转到 CANCELLED")
    void approvedCanCancel() {
        assertTrue(ReservationStatus.APPROVED.canTransitTo(ReservationStatus.CANCELLED));
    }

    @Test
    @DisplayName("COMPLETED 不能流转到任何状态")
    void completedCannotTransit() {
        assertFalse(ReservationStatus.COMPLETED.canTransitTo(ReservationStatus.PENDING));
        assertFalse(ReservationStatus.COMPLETED.canTransitTo(ReservationStatus.APPROVED));
        assertFalse(ReservationStatus.COMPLETED.canTransitTo(ReservationStatus.CANCELLED));
    }

    @Test
    @DisplayName("REJECTED 不能流转到任何状态")
    void rejectedCannotTransit() {
        assertFalse(ReservationStatus.REJECTED.canTransitTo(ReservationStatus.PENDING));
        assertFalse(ReservationStatus.REJECTED.canTransitTo(ReservationStatus.APPROVED));
    }

    @Test
    @DisplayName("CANCELLED 不能流转到任何状态")
    void cancelledCannotTransit() {
        assertFalse(ReservationStatus.CANCELLED.canTransitTo(ReservationStatus.PENDING));
        assertFalse(ReservationStatus.CANCELLED.canTransitTo(ReservationStatus.COMPLETED));
    }

    @Test
    @DisplayName("APPROVED 不能流转到 PENDING")
    void approvedCannotRevertToPending() {
        assertFalse(ReservationStatus.APPROVED.canTransitTo(ReservationStatus.PENDING));
    }

    @Test
    @DisplayName("fromCode 正确解析状态字符串")
    void fromCodeParsesCorrectly() {
        assertEquals(ReservationStatus.PENDING, ReservationStatus.fromCode("PENDING"));
        assertEquals(ReservationStatus.APPROVED, ReservationStatus.fromCode("approved"));
        assertEquals(ReservationStatus.COMPLETED, ReservationStatus.fromCode("Completed"));
    }

    @Test
    @DisplayName("fromCode 非法值抛出异常")
    void fromCodeThrowsOnInvalid() {
        assertThrows(IllegalArgumentException.class, () -> ReservationStatus.fromCode("INVALID"));
        assertThrows(IllegalArgumentException.class, () -> ReservationStatus.fromCode(""));
        assertThrows(IllegalArgumentException.class, () -> ReservationStatus.fromCode(null));
    }

    @Test
    @DisplayName("getDescription 返回正确的中文描述")
    void descriptionIsCorrect() {
        assertEquals("待审批", ReservationStatus.PENDING.getDescription());
        assertEquals("已通过", ReservationStatus.APPROVED.getDescription());
        assertEquals("已驳回", ReservationStatus.REJECTED.getDescription());
        assertEquals("已完成", ReservationStatus.COMPLETED.getDescription());
        assertEquals("已取消", ReservationStatus.CANCELLED.getDescription());
    }
}
