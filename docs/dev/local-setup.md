# Run Kuizi on your PC

Everything Kuizi needs runs on your own computer with Docker (T237, [ADR 0006](../architecture/decisions/0006-local-first-development.md)). No cloud account, no cost, no real student data.

## 1. Install the tools (once)

You need a PC with **16 GB of RAM** (8 GB works if you close other apps) and about **10 GB of free disk**.

| Your PC | Install |
| --- | --- |
| **Windows 11** | 1. Open PowerShell as administrator and run `wsl --install`, then restart. This gives you Ubuntu inside Windows.<br>2. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and, in its settings, tick *Use the WSL 2 based engine* and *Resources → WSL integration → Ubuntu*.<br>3. Open the **Ubuntu** app and do everything below inside it, in your Linux home folder (not under `/mnt/c`, which is much slower). |
| **macOS** | Install [Docker Desktop](https://www.docker.com/products/docker-desktop/). In *Settings → Resources*, give it at least 6 GB of memory. |
| **Ubuntu** | Install Docker Engine ([guide](https://docs.docker.com/engine/install/ubuntu/)), then run `sudo usermod -aG docker $USER` and log out and back in. |

Then, in a terminal (the Ubuntu app on Windows):

```bash
# Git, make and curl (Windows/Ubuntu; macOS: run `xcode-select --install` instead)
sudo apt update && sudo apt install -y git make curl

# uv, the Python tool for the brain environment
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Get the code and start Kuizi

```bash
git clone https://github.com/salahamami/kuizi.git
cd kuizi
make up
```

The first `make up` downloads about 4 GB of images and builds the Kuizi Keycloak image (about 2 more minutes), so it takes a few minutes. After that it starts in under a minute. It creates your `.env` file from `.env.example`, starts every service and waits until each one is healthy.

Check that everything really works:

```bash
make smoke
```

Every line should say `ok`.

## 3. Set up the brain environment

```bash
make ml-setup   # Python 3.12, PyTorch (CPU), pyKT, JupyterLab
make ml-lab     # opens JupyterLab in your browser
```

## What is running

| Service | Address on your PC | Stands in for (cloud, from S8) |
| --- | --- | --- |
| PostgreSQL with pgvector | `localhost:5432` | Aurora PostgreSQL (T211) |
| Kafka API (Redpanda) | `localhost:19092`, schema registry `localhost:18081` | Amazon MSK (T021) |
| Redis | `localhost:6379` | ElastiCache (T026) |
| S3 storage (SeaweedFS) | `localhost:8333` | Amazon S3 (T213) |
| Keycloak (sign-in) | http://localhost:8080/admin (user `admin`, password in `.env`), realm `kuizi` with synthetic dev users: see [identity.md](identity.md) | Keycloak on EKS (T012) |
| MLflow (brain experiments) | http://localhost:5050 | MLflow on EKS (T218) |
| LiteLLM gateway, optional | `localhost:4000`, start with `make up-llm` | LiteLLM on EKS (T059) |

Application code reads the connection settings from `.env` (`DATABASE_URL`, `KAFKA_BOOTSTRAP_SERVERS`, `REDIS_URL`, `S3_ENDPOINT_URL`, `KEYCLOAK_URL`, `MLFLOW_TRACKING_URI`…). The cloud uses the same names, so moving to AWS (T240) changes settings, not code.

## Everyday commands

| Command | What it does |
| --- | --- |
| `make up` | Start everything |
| `make status` | Show each service and its address |
| `make smoke` | Test that every service works |
| `make check` | Check the repository is consistent (compose file, agent briefs, backlog); run it before handing work back |
| `make lint` | Run the CI linters on every project (Ruff, mypy, Prettier, ESLint, tsc); see [CI](ci.md) |
| `make test` | Run the unit tests with the CI coverage gates on every project |
| `make logs` | Follow the logs (Ctrl+C to stop) |
| `make down` | Stop everything, keep the data |
| `make reset` | Delete all local data and start from zero |
| `make help` | List the commands |

## If something goes wrong

- **"port is already allocated"**: another program uses that port. Change the port in `.env` (for example `KEYCLOAK_PORT=8081` and `KEYCLOAK_URL=http://localhost:8081`), then `make up` again.
- **"Cannot connect to the Docker daemon"**: start Docker Desktop (Windows, macOS) or run `sudo systemctl start docker` (Ubuntu).
- **A service stays "unhealthy"**: run `make logs`, then `make reset`. If your PC has 8 GB, close other apps or give Docker more memory.
- **Windows is slow**: make sure the code is in your Ubuntu home folder (`cd ~`), not in `/mnt/c/...`.

## Rules

- `.env` holds local settings and passwords. It is never committed (`.gitignore` already excludes it).
- Only synthetic or public data in the local stack and in notebooks. Real student data never goes on a PC.
