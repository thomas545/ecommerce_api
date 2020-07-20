from time import time, mktime
from datetime import timedelta


def time_calculator(func):
    def wrapper(*args, **kwargs):
        time1 = time()
        func(*args, **kwargs)
        time2 = time()
        print("Run Time : ", timedelta(time2 - time1).total_seconds())

    return wrapper
