import time
import os
import hashlib
from machine import Pin, unique_id


def main():
    p13 = Pin(13, Pin.OUT)

    while True:
        p13.off()
        time.sleep(1)
        p13.on()
        time.sleep(1)

if __name__ == "__main__":
    main()


# TODO: os.uname().machine
# TODO: unique_id.hex()
# >>> ret = hashlib.md5(b'ola')
# >>> ret.digest().hex()
# '2fe04e524ba40505a82e03a2819429cc'


# TODO: fetch configuration (period?)
# TODO: local config up to date? hash
    # TODO: no, update config
    # TODO: yes, nothing
# TODO: cronjob to enable pump
# TODO: send events
# TODO: read sensor
