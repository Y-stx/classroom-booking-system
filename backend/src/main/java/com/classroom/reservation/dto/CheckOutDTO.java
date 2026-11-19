package com.classroom.reservation.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class CheckOutDTO {

    @NotNull(message = "预约ID不能为空")
    private Long reservationId;

    @NotNull(message = "实际人数不能为空")
    @Min(value = 1, message = "实际人数至少为1")
    private Integer actualAttendees;

    private String equipmentStatus;

    @Min(value = 1, message = "卫生评分最低为1星")
    @Max(value = 5, message = "卫生评分最高为5星")
    private Integer cleanliness;

    private String notes;
}
