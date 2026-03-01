# 🚀 3-Tier Microservices Web Application

## 📖 Overview
This project demonstrates a full microservices architecture deployed on the cloud. It features a Python (Flask) frontend web application connected to a MongoDB backend database. Both services are fully containerized and orchestrated using Docker Compose, and deployed live on an AWS EC2 instance.

## 🛠️ Tech Stack
* **Application:** Python, Flask
* **Database:** MongoDB
* **Containerization:** Docker, Docker Hub
* **Orchestration:** Docker Compose
* **Cloud Infrastructure:** AWS EC2 (Ubuntu Linux)
* **Security:** Kubernetes/Docker Secrets (for DB credentials), AWS Security Groups

## 🏗️ Architecture
1. **Frontend:** A Python web app that tracks visitor counts.
2. **Backend:** A MongoDB database that securely stores the persistent count data.
3. **Network:** Both containers communicate over a private bridge network, with only the web app exposed to the public internet via Port 5000.

## ⚙️ How to Run Locally
1. Clone this repository: `git clone https://github.com/Jeet4949/devops-microservices-project.git`
2. Navigate into the directory: `cd devops-microservices-project`
3. Build and run the containers: `docker-compose up -d --build`
4. Access the app at `http://localhost:5000`

## ☁️ Cloud Deployment (AWS)
This application was successfully deployed to an AWS EC2 instance.
* Provisioned an Ubuntu server using SSH and RSA Key Pairs (`.pem`).
* Configured AWS Security Groups to allow inbound traffic on Port 22 (SSH) and Port 5000 (HTTP).
* Installed the Docker daemon and Docker Compose directly onto the Linux server to serve the application to the public internet.
