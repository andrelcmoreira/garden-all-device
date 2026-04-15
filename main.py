import hashlib
import os

from machine import unique_id


def make_device_hash() -> str:
    model = os.uname().machine
    uuid = unique_id().hex()

    return hashlib.md5((model + uuid).encode()).digest().hex()


def main() -> None:
    pass


if __name__ == "__main__":
    main()


# TODO: fetch configuration
#   - period?
#   - cronjob?
#   - send device hash on request
# TODO: local config is up to date?
#   - checking based on config hash
#   - no, update config
#   - yes, nothing
# TODO: activate pump
#   - cronjob?
#   - send events
# TODO: read sensor
#   - send events
