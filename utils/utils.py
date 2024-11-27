import datetime

import config


def get_time_now(i=0):

    # 获取当前时间
    now = datetime.datetime.now()

    # 将当前时间加1秒
    one_second_later = now + datetime.timedelta(seconds=i)

    # 格式化时间为指定格式
    formatted_time = one_second_later.strftime(config.time_format)

    return formatted_time
