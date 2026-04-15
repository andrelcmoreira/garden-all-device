import hashlib
import json
import os
import urequests

from machine import unique_id


def make_device_hash() -> str:
    model = os.uname().machine
    uuid = unique_id().hex()

    return hashlib.md5((model + uuid).encode()).digest().hex()


# $ cat config.json:
# {
#   "period": 3600,
#   "config_hash": "def456",
# }
CFG_FILE = 'config.json'
DEVICE_FINGERPRINT = make_device_hash()
RUMNING_CFG = None
DEFAULT_CFG = {
    "period": 86400,  # 24h
    "config_hash": "",
}


def fetch_config() -> dict:
    global DEVICE_FINGERPRINT
    global DEFAULT_CFG

    url = f'https://example.com/config?device_hash={DEVICE_FINGERPRINT}'

    try:
        reply = urequests.get(url)
        cfg = reply.json()
        reply.close()

        return cfg
    except Exception:
        print('failed to fetch config, using default')

    return DEFAULT_CFG


def is_cfg_outdated(cfg: dict) -> bool:
    with open(CFG_FILE, 'r') as f:
        local_cfg = json.load(f)

        if local_cfg['config_hash'] != cfg['config_hash']:
            return True

    return False


def has_local_config() -> bool:
    return os.path.exists(CFG_FILE)


def update_local_config(cfg: dict) -> None:
    with open(CFG_FILE, 'w') as f:
        json.dump(cfg, f)


def main() -> None:
    print('starting up...')

    cfg = fetch_config()
    if not has_local_config() or is_cfg_outdated(cfg):
        update_local_config(cfg)

    # TODO: setup a timer to fetch config every X seconds
    # TODO: setup a timer to read sensors every Y seconds
    # TODO: setup a timer to activate pump every cfg['period'] seconds


if __name__ == '__main__':
    main()


# TODO: local config is up to date?
#   - checking based on config hash
#   - no, update config
#   - yes, nothing
# TODO: activate pump
#   - cronjob?
#   - send events
# TODO: read sensor
#   - send events
