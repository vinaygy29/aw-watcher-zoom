import logging
import os
import sys
from datetime import datetime, timezone
from time import sleep

from aw_client import ActivityWatchClient
from aw_core import dirs
from aw_core.models import Event
from .api import get_meeting
from .exceptions import FatalError
from .lib import get_current_window

logger = logging.getLogger("aw-watcher-zoom")
DEFAULT_CONFIG = """
[aw-watcher-zoom]
host_email = ""
account_id = ""
client_id = ""
client_secret = ""
poll_time = 5.0"""


def load_config():
    from aw_core.config import load_config_toml as _load_config

    return _load_config("aw-watcher-zoom", DEFAULT_CONFIG)


config = load_config()


def main():
    logging.basicConfig(level=logging.INFO)
    global config
    config = load_config()
    config_dir = dirs.get_config_dir("aw-watcher-zoom")

    poll_time = float(config["aw-watcher-zoom"].get("poll_time"))
    host_email = config["aw-watcher-zoom"].get("host_email", None)
    account_id = config["aw-watcher-zoom"].get("account_id", None)
    client_id = config["aw-watcher-zoom"].get("client_id", None)
    client_secret = config["aw-watcher-zoom"].get("client_secret", None)

    if not host_email or not client_id or not client_secret or not account_id:
        logger.warning(
            "host_email, account_id, client_id or client_secret not specified in config file (in folder {}). Get your "
            "account_id, client_id and"
            "client_secret here: https://marketplace.zoom.us/develop/apps/".format(
                config_dir
            )
        )
        sys.exit(1)

    # TODO: Fix --testing flag and set testing as appropriate
    client = ActivityWatchClient("aw-watcher-zoom", testing=False)
    bucket_id = f"{client.client_name}_{client.client_hostname}"
    event_type = "current-meeting"
    client.create_bucket(bucket_id, event_type, queued=True)
    logger.info("aw-watcher-zoom started")

    sleep(1)  # wait for server to start
    with client:
        heartbeat_loop(
            client,
            bucket_id,
            poll_time=poll_time,
            strategy="",
            exclude_title=False,
        )


def heartbeat_loop(client, bucket_id, poll_time, strategy, exclude_title=False):
    while True:
        if os.getppid() == 1:
            logger.info("window-watcher stopped because parent process died")
            break

        current_window = None
        try:
            current_window = get_current_window(strategy)
            logger.debug(current_window)
        except (FatalError, OSError):
            # Fatal exceptions should quit the program
            try:
                logger.exception("Fatal error, stopping")
            except OSError:
                pass
            break
        except Exception:
            # Non-fatal exceptions should be logged
            try:
                # If stdout has been closed, this exception-print can cause (I think)
                #   OSError: [Errno 5] Input/output error
                # See: https://github.com/ActivityWatch/activitywatch/issues/756#issue-1296352264
                #
                # However, I'm unable to reproduce the OSError in a test (where I close stdout before logging),
                # so I'm in uncharted waters here... but this solution should work.
                logger.exception("Exception thrown while trying to get active window")
            except OSError:
                break

        if current_window is None:
            logger.debug("Unable to fetch window, trying again on next poll")
        else:
            if exclude_title:
                current_window["title"] = "excluded"

            if current_window["app"] == "Zoom.exe":
                meeting = get_meeting(config)
                if len(meeting) != 0:
                    current_window["meeting_id"] = meeting["id"]
                    current_window["meeting_topic"] = meeting["topic"]
                    current_window["meeting_host"] = meeting["host"]
                    current_window["meeting_start_time"] = meeting["start_time"]

            now = datetime.now(timezone.utc)

            current_window_event = Event(timestamp=now, data=current_window)

            # Set pulsetime to 1 second more than the poll_time
            # This since the loop takes more time than poll_time
            # due to sleep(poll_time).
            if current_window["app"] == "Zoom.exe":
                client.heartbeat(
                    bucket_id, current_window_event, pulsetime=poll_time + 3.0, queued=True
                )

        sleep(poll_time)
