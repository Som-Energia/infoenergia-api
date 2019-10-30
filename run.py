import argparse
import sys


def main(host, port):
    from api import app

    try:
        app.run(host=host, port=port, debug=True)
    except (KeyboardInterrupt, SystemExit):
        print("You kill me!!")
    finally:
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Infoenergia api service")

    parser.add_argument(
        "-H", "--host",
        help="host address to serve (default: %(default)r",
        type=str,
        default="0.0.0.0"
    )

    parser.add_argument(
        "-p", "--port",
        help="TCP/IP port to serve (default: %(default)r",
        type=str,
        default="9000"
    )

    args = parser.parse_args()

    main(args.host, args.port)
