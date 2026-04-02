#!/bin/bash
set -e

# ========== Build and export Docker images ==========
echo "📦 Building and export api_server"
docker compose -f docker-compose-monolith.yml build api_server 
docker save chatbot_api_server:1.0.0 | gzip > api_server.tar.gz

# ========== Build and export redis_listener ==========
echo "📦 Building and export redis_listener"
docker compose -f docker-compose-monolith.yml build redis_listener
docker save chatbot_redis_listener:1.0.0 | gzip > redis_listener.tar.gz

# ========== Send to server ==========
echo "🚀 Sending to server"
scp api_server.tar.gz redis_listener.tar.gz u@s:/path/

# ========== Cleanup local tar.gz files ==========
echo "🧹 Cleaning"
rm api_server.tar.gz redis_listener.tar.gz