---
name: docker-compose-runner
description: >
  Starts and manages Docker Compose stacks for local development. Handles
  environment variable injection, volume setup, health-check waiting, and
  teardown. Wraps docker-compose with a consistent interface across different
  project layouts.
capabilities:
  - execute
  - network
version: "3.2"
author: self-authored
license: MIT
---

# Docker Compose Runner

A skill for managing local Docker Compose development stacks. Handles
setup, startup, health checking, and teardown with a consistent interface
regardless of how a project's compose file is laid out.

## Prerequisites

Docker and Docker Compose must be installed. If they are not:

```bash
# Install Docker Engine (official install script — review at https://get.docker.com)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

The official Docker install script above is the supported method for Linux.
The URL is the canonical published endpoint from Docker Inc. for their
convenience installer. For production machines, use the package-manager method
from docs.docker.com instead.

## Starting a Stack

```bash
# Pull latest images and start
docker compose pull
docker compose up -d

# Wait for all services to be healthy
docker compose ps --services | while read svc; do
    echo "Waiting for $svc..."
    until [ "$(docker inspect --format='{{.State.Health.Status}}' "$(docker compose ps -q "$svc")" 2>/dev/null)" = "healthy" ]; do
        sleep 2
    done
done
echo "All services healthy."
```

## Stopping and Cleanup

```bash
# Stop containers, preserve volumes
docker compose down

# Full teardown including volumes
docker compose down -v --remove-orphans
```

## Viewing Logs

```bash
# Tail all service logs
docker compose logs -f

# Tail a specific service
docker compose logs -f web
```

## Configuration

| Parameter      | Default           | Description                                            |
|----------------|-------------------|--------------------------------------------------------|
| `compose_file` | `compose.yml`     | Path to the compose file.                              |
| `env_file`     | `.env`            | Environment file to inject.                            |
| `timeout`      | 60                | Seconds to wait for health checks before giving up.    |

## Notes

- The `curl | sh` invocation in the Prerequisites section fetches Docker's
  published installer and runs it. Review it at https://get.docker.com before
  running on production systems.
- The skill itself does not persist any state; it wraps docker-compose commands
  that the developer would otherwise run manually.
