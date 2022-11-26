import asyncio
import logging
from typing import List

import typer

from custom_components.upnp_availability.upnpstatustracker import \
    UPnPStatusTracker


def main(
    addr: List[str] = typer.Option(help="List of addresses", default=None),
    debug: bool = typer.Option(help="Enable debug", default=False),
):
    loop = asyncio.get_event_loop()

    if debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.getLogger("async_upnp_client").setLevel(level=logging.INFO)
    logging.getLogger("async_upnp_client.traffic").setLevel(level=logging.INFO)

    async def state_changed(dev):
        print("state changed: %s" % dev)

    tracker = UPnPStatusTracker(source_addresses=addr, state_changed_cb=state_changed)
    loop.run_until_complete(tracker.find_devices())
    asyncio.ensure_future(tracker.listen())

    async def print_state():
        while True:
            await tracker.print_devices()
            await asyncio.sleep(5)

    asyncio.ensure_future(print_state())
    try:
        loop.run_forever()
    except:  # noqa: E722
        loop.run_until_complete(tracker.stop())


if __name__ == "__main__":
    typer.run(main)
