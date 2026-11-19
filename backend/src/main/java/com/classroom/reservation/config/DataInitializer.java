package com.classroom.reservation.config;

import com.classroom.reservation.entity.SysUser;
import com.classroom.reservation.mapper.SysUserMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * 数据初始化：确保初始用户密码已正确使用 BCrypt 加密
 */
@Component
public class DataInitializer implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(DataInitializer.class);

    private final SysUserMapper userMapper;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    public DataInitializer(SysUserMapper userMapper) {
        this.userMapper = userMapper;
    }

    @Override
    public void run(String... args) {
        String[][] initialUsers = {
                {"admin", "admin123"},
                {"teacher01", "123456"},
                {"student01", "123456"}
        };

        for (String[] userInfo : initialUsers) {
            String username = userInfo[0];
            String plainPassword = userInfo[1];
            SysUser user = userMapper.findByUsername(username);
            if (user != null) {
                // 检查密码是否是合法的 BCrypt 哈希（以 $2a$ 开头且能匹配）
                String currentPwd = user.getPassword();
                if (currentPwd == null || !currentPwd.startsWith("$2a$") ||
                        !passwordEncoder.matches(plainPassword, currentPwd)) {
                    // 更新为正确的 BCrypt 哈希
                    userMapper.updatePassword(user.getId(), passwordEncoder.encode(plainPassword));
                    log.info("已更新用户 [{}] 的密码哈希", username);
                }
            }
        }
        log.info("数据初始化检查完成");
    }
}
