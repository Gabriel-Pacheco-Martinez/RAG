# Centralized entry point for commands
import argparse
from app import endpoint
from src import index


from dotenv import load_dotenv
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="RAG Project CLI")
    parser.add_argument("-i", "--ingest", action="store_true", help="Ingest documents into FAISS")
    parser.add_argument("-q", "--query", type=str, help="Query a question")
    parser.add_argument("-s", "--server", action="store_true", help="Run server")

    args = parser.parse_args()

    if args.ingest:
        print("🚀 Document ingestion:")
        index.run()
    elif args.server:
        print("🚀 Starting server at localhost:8000")
        endpoint.start_server()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
