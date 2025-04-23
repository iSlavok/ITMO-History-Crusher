#!/bin/bash

COMPOSE_FILE="docker-compose.yml"
PROFILE="prod"
PROJECT_NAME=$(basename $(pwd))

echo "🚀 Starting bot update..."

if [ -d ".git" ]; then
    echo "📥 Downloading latest changes from repository..."
    if ! git pull; then
        echo "❌ Error updating code! Check access rights or merge conflicts."
        exit 1
    fi
    echo "✅ Code successfully updated!"
fi

echo "🛑 Stopping current containers..."
docker compose -f $COMPOSE_FILE --profile $PROFILE down

echo "🗑️ Removing old bot images..."
OLD_IMAGES=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "^${PROJECT_NAME}-bot" || true)
if [ ! -z "$OLD_IMAGES" ]; then
    echo "🧹 Removing images: $OLD_IMAGES"
    docker rmi $OLD_IMAGES || true
fi

echo "🏗️ Building new version of the bot from scratch..."
if ! docker compose -f $COMPOSE_FILE build --no-cache; then
    echo "❌ Error building image! Check error log above."
    exit 1
fi

echo "🚀 Starting new version of the bot..."
if ! docker compose -f $COMPOSE_FILE --profile $PROFILE up -d; then
    echo "❌ Error starting containers! Check error log above."
    exit 1
fi

echo "🧹 Removing other unused images..."
docker image prune -f

echo "✨ Done! Bot successfully updated and launched."
echo "📊 Containers status:"
docker compose -f $COMPOSE_FILE ps