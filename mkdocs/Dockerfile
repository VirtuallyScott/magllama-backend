FROM python:3.9-slim

# Install Git
RUN apt-get update && apt-get install -y git

# Create a non-root user
RUN useradd -m docsuser
WORKDIR /home/docsuser/docs

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies with pinned versions
RUN pip install --no-cache-dir \
    mkdocs>=1.5 \
    mkdocs-material==9.6.2 \
    "pymdown-extensions[extra,mermaid]==10.14.3" \
    mkdocs-awesome-pages-plugin

# Copy docs and change ownership
COPY . .
RUN chown -R docsuser:docsuser /home/docsuser

USER docsuser

# Fix SSH permissions
RUN mkdir -p /home/docsuser/.ssh && chmod 700 /home/docsuser/.ssh

CMD ["mkdocs", "serve", "-a", "0.0.0.0:8000"]
