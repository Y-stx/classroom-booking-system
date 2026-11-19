package com.classroom.reservation;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

@SpringBootApplication
@MapperScan("com.classroom.reservation.mapper")
@EnableCaching
public class ClassroomReservationApplication {

    public static void main(String[] args) {
        SpringApplication.run(ClassroomReservationApplication.class, args);
        System.out.println("\n" +
                "╔══════════════════════════════════════════════╗\n" +
                "║   教室预约与使用登记系统后端启动成功!          ║\n" +
                "║   Swagger: http://localhost:8080/swagger-ui   ║\n" +
                "╚══════════════════════════════════════════════╝\n");
    }
}
