import sys
import requests  # Let's add a dependency to make it interesting


def main():
    print(f"Hello from Python {sys.version}!")
    print(f"Requests version: {requests.__version__}")


if __name__ == "__main__":
    main()
