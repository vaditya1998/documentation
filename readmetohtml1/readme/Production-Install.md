# i2b2 Production Deployment Guide

This guide provides instructions for deploying i2b2 in a production environment, assuming you are using a PostgreSQL database on a remote production server.

---

## 1. Setting up Subnets in the Cloud

*temp*

---

## 2. Setting up PostgreSQL Database

Follow the official i2b2 guide to set up the PostgreSQL database:

> [i2b2 Data Installation Guide](https://community.i2b2.org/wiki/display/getstarted/Chapter+3.+Data+Installation)

---

## 3. Deploying Client Containers and Database Connectivity

This section provides guidance for deploying the i2b2 web client and WildFly service using Docker while connecting them to a pre-configured production PostgreSQL database.

### Step 1: Clone the Repository

If you have not already cloned the repository, execute:

```sh
git clone https://github.com/i2b2/i2b2-docker.git
```

### Step 2: Navigate to the Repository Directory

```sh
cd i2b2-docker
```

### Step 3: Checkout the Production Branch

Checkout the branch that contains only the web client and WildFly service.

```sh
git checkout release-v1.8.1a.0001_prod_db
```

### Step 4: Configure the Database

Ensure that the PostgreSQL production database is already set up and running. 

- Update the database environment variables in the `.env` file to match your production settings.
- Configure the following parameters:
  - **Database Host**
  - **Port**
  - **Username**
  - **Password**
  - **Database Name**
  - **Schema Name**

### Step 5: Start the Web and WildFly Containers

Run the following command to start the containers:

```sh
docker-compose up -d i2b2-web
```

### Step 6: Verify the Deployment

- Check if the WildFly container has started successfully:

  ```sh
  docker-compose logs WildFly
  ```

- Access the i2b2 web client in your browser using the appropriate production URL and port.

---

This completes the i2b2 production deployment. If you encounter any issues, refer to the logs or the official i2b2 documentation.
