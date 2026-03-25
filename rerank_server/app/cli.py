# Centralized entry point for commands
import argparse
import asyncio
from app import endpoint

from dotenv import load_dotenv
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="RAG Server CLI")
    parser.add_argument("-s", "--server", action="store_true", help="Run server")

    args = parser.parse_args()

    if args.server:
        print("🚀 Starting server at localhost:8002")
        endpoint.start_server()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
