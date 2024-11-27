import logging
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import threading
import time

# 配置日志
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

def create_data_store():
    # 创建数据块
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [0]*100),
        hr=ModbusSequentialDataBlock(0, [0]*100),
        ir=ModbusSequentialDataBlock(0, [0]*100)
    )
    return store

def update_register(store, register_address, num, value_generator, interval):
    while True:
        # 获取下一个值
        value = next(value_generator)
        log.debug(f"Next value from generator: {value}")
        # 创建一个包含多个值的列表
        values = [value] * num
        # 批量更新指定寄存器的数据
        store.setValues(3, register_address, values)
        log.info(f"Updated registers from {register_address} to {register_address + num - 1} to {value}")
        # 增加日志确认更新后的值
        updated_values = store.getValues(3, register_address, count=num)
        log.debug(f"Updated values: {updated_values}")
        time.sleep(interval)

def run_modbus_tcp_server():
    # 创建数据块
    store = create_data_store()

    # 创建上下文
    context = ModbusServerContext(slaves=store, single=True)

    # 启动定时任务
    register_address = 0  # 指定起始寄存器地址
    num = 100  # 指定要更新的寄存器数量
    value_generator = (i for i in range(1000))  # 生成器，产生从0到999的值
    interval = 1  # 定时间隔（秒）
    update_thread = threading.Thread(target=update_register, args=(store, register_address, num, value_generator, interval))
    update_thread.daemon = True
    update_thread.start()

    # 启动服务器
    StartTcpServer(context, address=("127.0.0.1", 8080))

if __name__ == "__main__":
    run_modbus_tcp_server()
