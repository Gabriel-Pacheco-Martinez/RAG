# Centralized entry point for commands
import argparse
from scripts import ingest_documents
from scripts import query_questions
from app import endpoint

def main():
    parser = argparse.ArgumentParser(description="RAG Project CLI")
    parser.add_argument("-i", "--ingest", action="store_true", help="Ingest documents into FAISS")
    parser.add_argument("-q", "--query", type=str, help="Query a question")
    parser.add_argument("-s", "--server", action="store_true", help="Run server")

    args = parser.parse_args()

    if args.ingest:
        print("🚀 Document ingestion:")
        ingest_documents.run()
    elif args.query:
        question = args.query
        print("🚀 Answering question:")
        query_questions.run(question)
    elif args.server:
        print("🚀 Starting server at localhost:8000")
        endpoint.start_server()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
