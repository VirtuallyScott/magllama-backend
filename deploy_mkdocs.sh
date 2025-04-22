#!/bin/bash

# Environment Variables:
# GITHUB_TOKEN: Personal access token for GitHub authentication
# GITHUB_EMAIL: Email associated with the GitHub account
# GITHUB_USERNAME: GitHub username
# REPO_NAME: Name of the GitHub repository

# Set variables
CONTAINER_NAME="mkdocs-deploy"
IMAGE_NAME="mkdocs-site"
REPO_PATH=$(pwd)
DOCS_PATH="$REPO_PATH/mkdocs"
GITHUB_TOKEN="$AUTOMATION_TOKEN"
GITHUB_EMAIL="$GITHUB_EMAIL"
GITHUB_USERNAME="$GITHUB_USERNAME"
REPO_NAME="magllama-backend"

# Ensure required environment variables are set
if [ -z "$GITHUB_TOKEN" ] || [ -z "$GITHUB_EMAIL" ] || [ -z "$GITHUB_USERNAME" ] || [ -z "$REPO_NAME" ]; then
    echo "Error: One or more environment variables are not set."
    exit 1
fi

# Step 1: Build the Docker image (if not exists)
echo "🔧 Building the MkDocs Docker image..."
docker build -t $IMAGE_NAME - <<EOF
FROM python:3.10
RUN pip install --no-cache-dir mkdocs mkdocs-material mkdocs-awesome-pages-plugin
WORKDIR /home/docsuser/repo
ENTRYPOINT ["mkdocs"]
EOF

# Step 2: Create a new MkDocs project if it doesn't exist
if [ ! -d "$DOCS_PATH" ]; then
    echo "📁 Creating a new MkDocs site at $DOCS_PATH..."
    mkdir -p "$DOCS_PATH"
    docker run --rm -v "$DOCS_PATH":/home/docsuser/repo -w /home/docsuser/repo $IMAGE_NAME new .
fi

# Step 3: Run the container in detached mode
echo "🚀 Starting MkDocs container..."
docker run -d --name $CONTAINER_NAME \
  -v "$REPO_PATH":/home/docsuser/repo \
  -w /home/docsuser/repo/mkdocs \
  -e GIT_DISCOVERY_ACROSS_FILESYSTEM=1 \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  $IMAGE_NAME tail -f /dev/null

# Step 4: Configure Git and deploy
echo "📢 Deploying documentation to GitHub Pages..."
docker exec -it $CONTAINER_NAME sh -c "
  git config --global user.email '$GITHUB_EMAIL' &&
  git config --global user.name '$GITHUB_USERNAME' &&
  git remote set-url origin https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$REPO_NAME.git &&
  mkdocs build &&
  mkdocs gh-deploy --force --verbose --remote-name origin --remote-branch gh-pages
"

# Step 5: Stop and remove the container
echo "🧹 Cleaning up..."
docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME

echo "✅ Deployment complete! Your site should be live at:"
echo "🌍 https://$GITHUB_USERNAME.github.io/$REPO_NAME/"
