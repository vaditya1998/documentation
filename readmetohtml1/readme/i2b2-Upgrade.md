# i2b2 Upgrade Guide

This guide provides the recommended procedures for upgrading your i2b2 instance to a newer version.

---

## Step 1: Navigate to the i2b2-docker Directory

Ensure you are in the correct directory before starting the upgrade:

```sh
cd i2b2-docker
```

---

## Step 2: Checkout the New Release Branch

Ensure you are checking out the correct branch based on your installation type.

**Options:**  
- **Localhost deployment**  
- **Production/Remote database deployment**  

Execute the following commands:

```sh
git checkout <new_release_tag>
git pull
```

---

## Step 3: Stop Running Containers

Before pulling the latest updates, stop all running containers:

```sh
docker-compose down
```

---

## Step 4: Pull the Latest Images

Fetch the latest updates from the repository:

```sh
docker-compose pull
```

---

## Step 5: Start the Updated Containers

Restart the i2b2 Web and WildFly containers:

```sh
docker-compose up -d i2b2-web
```

---

## Step 6: Wait for Initialization

Allow a few moments for the containers to initialize and for **WildFly** to start completely.

For troubleshooting, refer to the [Troubleshooting Guide](https://github.com/devi2b2/i2b2_documentation/wiki/i2b2-Docker-installation-Guide-%E2%80%90-Localhost#troubleshooting-guide).

---

This completes the upgrade process for i2b2. If you encounter issues, check the logs or refer to the official i2b2 documentation.
