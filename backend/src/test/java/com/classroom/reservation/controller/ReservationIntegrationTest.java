package com.classroom.reservation.controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * 预约与使用登记接口集成测试（MockMvc）
 * 依赖：MySQL + Redis 已启动，数据库已执行 schema-and-data.sql
 */
@SpringBootTest
@AutoConfigureMockMvc
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
@DisplayName("预约与使用登记接口集成测试")
class ReservationIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    private static String studentToken;
    private static Long createdReservationId;

    private static final DateTimeFormatter DTF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    @BeforeEach
    void setUp() throws Exception {
        if (studentToken == null) {
            loginAsStudent();
        }
    }

    private void loginAsStudent() throws Exception {
        String body = "{\"username\":\"student01\",\"password\":\"123456\"}";
        MvcResult result = mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andReturn();
        JsonNode json = objectMapper.readTree(result.getResponse().getContentAsString());
        studentToken = json.get("data").get("token").asText();
    }

    @Test
    @Order(1)
    @DisplayName("登录成功返回 token")
    void loginSuccess() throws Exception {
        String body = "{\"username\":\"student01\",\"password\":\"123456\"}";
        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.token").exists());
    }

    @Test
    @Order(2)
    @DisplayName("登录失败-密码错误返回401")
    void loginWrongPassword() throws Exception {
        String body = "{\"username\":\"student01\",\"password\":\"wrong\"}";
        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value(401));
    }

    @Test
    @Order(3)
    @DisplayName("未携带Token访问受保护接口返回401")
    void noTokenReturns401() throws Exception {
        mockMvc.perform(get("/api/classrooms"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @Order(4)
    @DisplayName("携带Token查询教室列表成功")
    void getClassroomsWithToken() throws Exception {
        mockMvc.perform(get("/api/classrooms")
                        .header("Authorization", "Bearer " + studentToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.list").isArray());
    }

    @Test
    @Order(5)
    @DisplayName("创建预约成功")
    void createReservationSuccess() throws Exception {
        // 使用较远未来时间，避免与已有测试数据冲突
        String startTime = LocalDateTime.now().plusDays(60).withHour(10).withMinute(0).withSecond(0).format(DTF);
        String endTime = LocalDateTime.now().plusDays(60).withHour(12).withMinute(0).withSecond(0).format(DTF);

        String body = String.format(
                "{\"classroomId\":1,\"title\":\"集成测试预约\",\"purpose\":\"测试\",\"startTime\":\"%s\",\"endTime\":\"%s\",\"attendees\":10}",
                startTime, endTime);

        MvcResult result = mockMvc.perform(post("/api/reservations")
                        .header("Authorization", "Bearer " + studentToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.id").exists())
                .andReturn();

        JsonNode json = objectMapper.readTree(result.getResponse().getContentAsString());
        createdReservationId = json.get("data").get("id").asLong();
    }

    @Test
    @Order(6)
    @DisplayName("创建预约-时间冲突被拒绝")
    void createReservationConflict() throws Exception {
        // 使用与上一条相同的时段（60天后 10:00-12:00），制造冲突
        String startTime = LocalDateTime.now().plusDays(60).withHour(11).withMinute(0).withSecond(0).format(DTF);
        String endTime = LocalDateTime.now().plusDays(60).withHour(13).withMinute(0).withSecond(0).format(DTF);

        String body = String.format(
                "{\"classroomId\":1,\"title\":\"冲突预约\",\"purpose\":\"测试\",\"startTime\":\"%s\",\"endTime\":\"%s\",\"attendees\":5}",
                startTime, endTime);

        mockMvc.perform(post("/api/reservations")
                        .header("Authorization", "Bearer " + studentToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(false));
    }

    @Test
    @Order(7)
    @DisplayName("创建预约-人数超过容量被拒绝")
    void createReservationExceedCapacity() throws Exception {
        String startTime = LocalDateTime.now().plusDays(61).withHour(10).withMinute(0).withSecond(0).format(DTF);
        String endTime = LocalDateTime.now().plusDays(61).withHour(12).withMinute(0).withSecond(0).format(DTF);

        String body = String.format(
                "{\"classroomId\":1,\"title\":\"超容量预约\",\"purpose\":\"测试\",\"startTime\":\"%s\",\"endTime\":\"%s\",\"attendees\":9999}",
                startTime, endTime);

        mockMvc.perform(post("/api/reservations")
                        .header("Authorization", "Bearer " + studentToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(false));
    }

    @Test
    @Order(8)
    @DisplayName("查询我的预约列表成功")
    void getMyReservations() throws Exception {
        mockMvc.perform(get("/api/reservations/my")
                        .header("Authorization", "Bearer " + studentToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.list").isArray());
    }

    @Test
    @Order(9)
    @DisplayName("空闲教室查询接口-返回可用教室列表")
    void getAvailableClassrooms() throws Exception {
        String startTime = LocalDateTime.now().plusDays(120).withHour(8).withMinute(0).withSecond(0).format(DTF);
        String endTime = LocalDateTime.now().plusDays(120).withHour(10).withMinute(0).withSecond(0).format(DTF);

        mockMvc.perform(get("/api/classrooms/available")
                        .header("Authorization", "Bearer " + studentToken)
                        .param("startTime", startTime)
                        .param("endTime", endTime))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data").isArray());
    }

    @Test
    @Order(10)
    @DisplayName("空闲教室查询-开始时间晚于结束时间返回错误")
    void getAvailableClassroomsInvalidTime() throws Exception {
        String startTime = LocalDateTime.now().plusDays(120).withHour(12).withMinute(0).withSecond(0).format(DTF);
        String endTime = LocalDateTime.now().plusDays(120).withHour(10).withMinute(0).withSecond(0).format(DTF);

        mockMvc.perform(get("/api/classrooms/available")
                        .header("Authorization", "Bearer " + studentToken)
                        .param("startTime", startTime)
                        .param("endTime", endTime))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(false));
    }
}
