import hashlib
import os
import time
import ujson
import urequests

from machine import unique_id, Timer


CFG_FILE = 'cfg.json'
DEFAULT_CHECK_CFG_INTERVAL = 60  # 1m
SERVER_IP = '192.168.0.8'


class DeviceContext:
    fg: str
    cfg: dict
    timers: tuple[Timer, Timer]


def read_sensors_cb(timer: Timer) -> None:
    # TODO: read sensor
    # TODO: send events
    pass


def activate_pump() -> None:
    # TODO: activate pump
    # TODO: send events
    pass


def check_cfg_cb(timer: Timer, ctx: DeviceContext) -> None:
    cfg = fetch_config(ctx.fg)
    if cfg and is_cfg_outdated(cfg['cfg-hash']):
        update_local_config(cfg)
        ctx.cfg = cfg
        setup_timers(ctx)


def make_device_hash() -> str:
    hash_obj = hashlib.sha256(
        (os.uname().machine + unique_id().hex()).encode()
    )
    ret = hash_obj.digest()

    return ret.hex()


def fetch_config(dev_fg: str) -> dict | None:
    url = f'http://{SERVER_IP}/api/v1/devices/{dev_fg}/config/'

    try:
        reply = urequests.get(url)
        cfg = reply.json()
        reply.close()

        return cfg
    except Exception:
        print('failed to fetch config')

    return None


def is_cfg_outdated(cfg_hash: str) -> bool:
    global CFG_FILE

    if not cfg_hash:
        return False

    with open(CFG_FILE, 'r') as f:
        local_cfg = ujson.load(f)

        if local_cfg['cfg-hash'] != cfg_hash:
            return True

    return False


def has_local_config() -> bool:
    global CFG_FILE

    return os.path.exists(CFG_FILE)


def update_local_config(cfg: dict) -> None:
    global CFG_FILE

    with open(CFG_FILE, 'w') as f:
        ujson.dump(cfg, f)


def setup_timers(ctx: DeviceContext) -> None:
    t0 = ctx.timers[0]
    t1 = ctx.timers[1]

    t0.deinit()
    t1.deinit()

    t0.init(
        period=ctx.cfg['check-cfg-interval'] * 1000,
        mode=Timer.PERIODIC,
        callback=lambda t: check_cfg_cb(t, ctx)
    )
    t1.init(
        period=ctx.cfg['read-sensors-interval'] * 1000,
        mode=Timer.PERIODIC,
        callback=read_sensors_cb
    )


def main() -> None:
    global DEFAULT_CHECK_CFG_INTERVAL

    print('starting application')

    dev_fg = make_device_hash()
    while True:
        print('fetching config...')
        cfg = fetch_config(dev_fg)
        if cfg:
            break

        time.sleep(DEFAULT_CHECK_CFG_INTERVAL)

    print(f'config received: {cfg}')

    ctx = DeviceContext(fg=dev_fg, cfg=cfg, timers=(Timer(0), Timer(1)))
    if not has_local_config() or is_cfg_outdated(ctx.cfg['cfg-hash']):
        update_local_config(ctx.cfg)

    setup_timers(ctx)

    try:
        while True:
            time.sleep(ctx.cfg['activate-pump-interval'])
            activate_pump()
    except KeyboardInterrupt:
        print('stoping application')
        ctx.timers[0].deinit()
        ctx.timers[1].deinit()


if __name__ == '__main__':
    main()
