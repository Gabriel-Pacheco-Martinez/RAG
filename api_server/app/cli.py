# Centralized entry point for commands
import argparse
import asyncio
from app import endpoint
from src import index

from dotenv import load_dotenv
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="API Server CLI")
    parser.add_argument("-i", "--ingest", action="store_true", help="Index documents")
    parser.add_argument("-s", "--server", action="store_true", help="Run server")

    args = parser.parse_args()

    if args.ingest:
        print("🚀 Document ingestion:")
        asyncio.run(index.run())
    elif args.server:
        print("🚀 Starting server at localhost:8000")
        endpoint.start_server()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
