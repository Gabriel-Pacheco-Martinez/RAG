# Centralized entry point for commands
import argparse
from scripts import ingest_documents
from scripts import query_questions

def main():
    parser = argparse.ArgumentParser(description="RAG Project CLI")
    parser.add_argument("-i", "--ingest", action="store_true", help="Ingest documents into FAISS")
    parser.add_argument("-q", "--query", type=str, help="Query a question")

    args = parser.parse_args()

    if args.ingest:
        print("🚀 Document ingestion:")
        ingest_documents.run()
    elif args.query:
        question = args.query
        print("🚀 Answering question:")
        query_questions.run(question)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
