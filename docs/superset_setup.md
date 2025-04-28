
# Superset Quick Setup Guide (Docker Compose)

## 1. Clone the Superset Repository

```bash
git clone https://github.com/apache/superset
cd superset
```

## 2. Checkout the Latest Official Release

```bash
git checkout tags/4.1.2
```

## 3. Start Superset using Docker Compose

```bash
docker compose -f docker-compose-image-tag.yml up
```

## 4. Access Superset

Open your browser and navigate to [http://localhost:8088](http://localhost:8088)

**Default Credentials:**
- Username: `admin`
- Password: `admin`

## 5. Stopping Superset

When finished, shut down and clean up containers:

```bash
docker compose down
```

---
