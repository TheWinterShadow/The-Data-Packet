#!/bin/bash

# Simple MongoDB Docker Script
# Usage: ./mongodb.sh [start|stop|status|logs|shell]

CONTAINER_NAME="mongodb-local"
MONGO_PORT="27017"
MONGO_USER="admin"
# MONGO_PASSWORD=""
MONGO_DB="the_data_packet"

case "${1:-start}" in
    start)
        echo "🚀 Starting MongoDB..."
        
        # Check if container already exists
        if docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
            echo "📦 Container exists, starting..."
            docker start $CONTAINER_NAME
        else
            echo "📦 Creating new MongoDB container..."
            docker run -d \
                --name $CONTAINER_NAME \
                -p $MONGO_PORT:27017 \
                -e MONGO_INITDB_ROOT_USERNAME=$MONGO_USER \
                -e MONGO_INITDB_ROOT_PASSWORD=$MONGO_PASSWORD \
                -e MONGO_INITDB_DATABASE=$MONGO_DB \
                -v mongodb_data:/data/db \
                mongo:7.0
        fi
        
        echo "⏳ Waiting for MongoDB to be ready..."
        sleep 5
        
        echo "✅ MongoDB is running!"
        echo "📍 Connection details:"
        echo "   Host: localhost"
        echo "   Port: $MONGO_PORT"
        echo "   Username: $MONGO_USER"
        echo "   Password: $MONGO_PASSWORD"
        echo "   Database: $MONGO_DB"
        echo ""
        echo "🔗 Connection URL:"
        echo "   mongodb://$MONGO_USER:$MONGO_PASSWORD@localhost:$MONGO_PORT/$MONGO_DB?authSource=admin"
        echo ""
        echo "💡 Usage:"
        echo "   ./mongodb.sh shell    # Open MongoDB shell"
        echo "   ./mongodb.sh logs     # View logs"
        echo "   ./mongodb.sh stop     # Stop MongoDB"
        ;;
        
    stop)
        echo "🛑 Stopping MongoDB..."
        docker stop $CONTAINER_NAME 2>/dev/null || echo "Container not running"
        ;;
        
    restart)
        echo "🔄 Restarting MongoDB..."
        docker restart $CONTAINER_NAME
        ;;
        
    status)
        if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q $CONTAINER_NAME; then
            echo "✅ MongoDB is running"
            docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep $CONTAINER_NAME
        else
            echo "❌ MongoDB is not running"
        fi
        ;;
        
    logs)
        echo "📋 MongoDB logs (press Ctrl+C to exit):"
        docker logs -f $CONTAINER_NAME
        ;;
        
    shell)
        echo "🐚 Opening MongoDB shell..."
        docker exec -it $CONTAINER_NAME mongosh -u $MONGO_USER -p $MONGO_PASSWORD --authenticationDatabase admin $MONGO_DB
        ;;
        
    remove)
        echo "🗑️  Removing MongoDB container and data..."
        read -p "⚠️  This will delete all data. Continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker stop $CONTAINER_NAME 2>/dev/null
            docker rm $CONTAINER_NAME 2>/dev/null
            docker volume rm mongodb_data 2>/dev/null
            echo "✅ Removed MongoDB container and data"
        else
            echo "❌ Cancelled"
        fi
        ;;
        
    *)
        echo "📖 Simple MongoDB Docker Script"
        echo ""
        echo "Usage: ./mongodb.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start     Start MongoDB (default)"
        echo "  stop      Stop MongoDB"
        echo "  restart   Restart MongoDB"
        echo "  status    Check if MongoDB is running"
        echo "  logs      View MongoDB logs"
        echo "  shell     Open MongoDB shell"
        echo "  remove    Remove container and all data"
        echo ""
        echo "Examples:"
        echo "  ./mongodb.sh                    # Start MongoDB"
        echo "  ./mongodb.sh shell              # Open shell"
        echo "  ./mongodb.sh logs               # View logs"
        ;;
esac