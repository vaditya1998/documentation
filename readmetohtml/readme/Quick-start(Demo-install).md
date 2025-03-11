# Quick Start - Demo install

This guide provides step-by-step instructions for installing i2b2 using Docker. It is intended for users setting up a fresh i2b2 instance.

---

## Prerequisites

Ensure that your system meets the following requirements before proceeding with the installation.

### Operating System

- **Ubuntu** (Recommended)

### Software Requirements

- **Git**
- **Docker**
- **Docker Compose**

---

## Installation Instructions

### Step 1: Clone the Repository

Open a terminal and execute the following command:

```sh
git clone https://github.com/i2b2/i2b2-docker.git
```

### Step 2: Navigate to the Repository Directory

```sh
cd i2b2-docker/
```

### Step 3: Start the i2b2 Containers

Change to the `pg` directory and start the containers using Docker Compose:

```sh
cd pg
docker-compose up -d i2b2-web
```

This command starts the **Postgres**, **Web**, and **WildFly** containers in detached mode.

### Step 4: Wait for Initialization

Allow a few moments for the containers to initialize and for **WildFly** to start completely.

### Step 5: Access the i2b2 Web Application

Open your preferred web browser and navigate to:

```
http://localhost/webclient
```

### Step 6: Log In to the Application

Ensure port **80** is forwarded, then use the default credentials:

- **Username:** `demo`
- **Password:** `demouser`

---

## Troubleshooting Guide

### Verify Running Containers

Check whether all necessary containers (**Web, WildFly, Postgres**) are running:

```sh
docker ps
```

### View Container Logs

To inspect logs for debugging, run:

```sh
docker logs -f <container_name>
```

### Stop All Running Containers

```sh
docker-compose stop
```

### Start All Stopped Containers

```sh
docker-compose start
```

---

## Fresh Installation

If you need to perform a **clean installation**, follow these steps:

### Step 1: Remove All Containers and Volumes

⚠️ *This will delete all existing Docker containers and volumes.*

```sh
docker rm -f $(docker ps -a -q)
docker volume rm $(docker volume ls -q)
```

### Step 2: Recreate and Start the Containers

```sh
cd i2b2-docker/pg
docker-compose up -d
```

---

This completes the setup and installation of i2b2 using Docker. If you encounter any issues, refer to the troubleshooting guide above.
