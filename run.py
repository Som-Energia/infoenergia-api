import argparse
import sys
from functools import partial

from sanic import Sanic
from sanic.worker.loader import AppLoader

from infoenergia_api.app import app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Infoenergia api service")

    parser.add_argument(
        "-H",
        "--host",
        help="host address to serve (default: %(default)r",
        type=str,
        default="0.0.0.0",
    )

    parser.add_argument(
        "-p",
        "--port",
        help="TCP/IP port to serve (default: %(default)r",
        type=int,
        default=9000,
    )

    args = parser.parse_args()
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=True,
            auto_reload=True,
        )
    except (KeyboardInterrupt, SystemExit):
        print("You kill me!!")
    except Exception as e:
        print(f"What the fuck @!#!:{e}")
    finally:
        sys.exit(0)
