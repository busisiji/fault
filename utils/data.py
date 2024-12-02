# coding: utf-8
def convert_data(self, raw_data, data_type):
    """
    根据数据类型转换原始数据。
    :param raw_data: 原始数据
    :param data_type: 数据类型
    :return: 转换后的数据
    """
    if data_type == 'uint16':
        return raw_data
    elif data_type == 'int16':
        return self.twos_complement(raw_data, 16)
    elif data_type == 'float32':
        return self.float_from_registers([raw_data])
    elif data_type == 'bool':
        return bool(raw_data)
    else:
        raise ValueError(f"不支持的数据类型: {data_type}")

def twos_complement(self, value, bits):
    """
    二进制补码转换。
    :param value: 输入值
    :param bits: 位数
    :return: 补码值
    """
    if value >= 2 ** (bits - 1):
        return value - 2 ** bits
    return value

def float_from_registers(self, registers):
    """
    从寄存器中读取浮点数。
    :param registers: 寄存器列表
    :return: 浮点数
    """
    import struct
    byte_array = bytearray()
    for reg in registers:
        byte_array.extend(reg.to_bytes(2, byteorder='big'))
    return struct.unpack('!f', byte_array)[0]
