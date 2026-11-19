package com.classroom.reservation.enums;

import org.apache.ibatis.type.BaseTypeHandler;
import org.apache.ibatis.type.JdbcType;
import org.apache.ibatis.type.MappedTypes;

import java.sql.CallableStatement;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * MyBatis TypeHandler: ReservationStatus 枚举与数据库 VARCHAR 的转换
 */
@MappedTypes(ReservationStatus.class)
public class ReservationStatusTypeHandler extends BaseTypeHandler<ReservationStatus> {

    @Override
    public void setNonNullParameter(PreparedStatement ps, int i, ReservationStatus parameter, JdbcType jdbcType)
            throws SQLException {
        ps.setString(i, parameter.name());
    }

    @Override
    public ReservationStatus getNullableResult(ResultSet rs, String columnName) throws SQLException {
        String value = rs.getString(columnName);
        return value == null ? null : ReservationStatus.fromCode(value);
    }

    @Override
    public ReservationStatus getNullableResult(ResultSet rs, int columnIndex) throws SQLException {
        String value = rs.getString(columnIndex);
        return value == null ? null : ReservationStatus.fromCode(value);
    }

    @Override
    public ReservationStatus getNullableResult(CallableStatement cs, int columnIndex) throws SQLException {
        String value = cs.getString(columnIndex);
        return value == null ? null : ReservationStatus.fromCode(value);
    }
}
