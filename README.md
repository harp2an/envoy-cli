# envoy-cli

> A CLI tool to manage and sync `.env` files across projects with encrypted remote storage support.

---

## Installation

```bash
pip install envoy-cli
```

Or with pipx for isolated installs:

```bash
pipx install envoy-cli
```

---

## Usage

Initialize envoy in your project:

```bash
envoy init
```

Push your `.env` file to remote storage:

```bash
envoy push --env .env --project my-app
```

Pull the latest `.env` for a project:

```bash
envoy pull --project my-app
```

Sync across multiple environments:

```bash
envoy sync --project my-app --env production
```

All files are encrypted before leaving your machine. Envoy uses AES-256 encryption by default and supports backends like S3, GCS, and a self-hosted option.

---

## Configuration

Envoy reads from a `.envoy.toml` file in your project root:

```toml
[remote]
backend = "s3"
bucket = "my-envoy-bucket"
region = "us-east-1"
```

---

## Requirements

- Python 3.8+
- An configured remote storage backend

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*Made with ☕ for developers who are tired of sharing `.env` files over Slack.*