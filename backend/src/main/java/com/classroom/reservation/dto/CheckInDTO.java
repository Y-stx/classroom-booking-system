package com.classroom.reservation.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class CheckInDTO {

    @NotNull(message = "预约ID不能为空")
    private Long reservationId;
}
