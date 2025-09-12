
# 
## Overview
KukuKonnect is an IoT-based poultry monitoring platform that addresses thermal stress in chickens for Kenyan farmers by monitoring and regulating temperature and humidity in coops. By connecting farmers with IoT devices, KukuKonnect ensures optimal coop conditions through real-time data and automated controls. The platform supports two main user types—farmers and agrovets—and provides a robust, scalable backend with a well-defined database schema to manage users, devices, environmental data, automation settings, and threshold updates.

## Features
* **User Management:** Secure registration and authentication for farmers and agrovets, with automated email notifications for farmer account creation.
**Device and Data Directory:** Comprehensive database of IoT devices, their settings (e.g., temperature/humidity thresholds).
* **Environmental Monitoring:** Real-time tracking of temperature and humidity data from coops.
* **Automation Control:** Automatic activation of fans or heaters based on default or user-defined thresholds.
* **Scalable Architecture:** Modular Django-based backend for easy integration and maintenance.
* **Secure Data Handling:** Robust authentication and data encryption to protect sensitive user and device information.

# Technology Stack
* **Python 3.13+:** Modern Python for reliable development.
* **Django 4.2+:** A high-level web framework for rapid development.
* **Django REST Framework:** For building secure and scalable APIs.
* **PostgreSQL:** A robust relational database for managing healthcare data.
* **drf-yasg:** Generates interactive Swagger documentation.
* **Token Authentication:** Secure access to APIs and user sessions.
## Getting Started
Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.
### Prerequisites
*   Python 3.10
*   pip
*   virtualenv
### Installation
1.  **Clone the repository:**
    ```sh
    git clone git@github.com:akirachix/kukukonnect-backend.git
    cd kukukonnect-backend
    ```
2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv kukuenv
    source kukuenv/bin/activate
    ```
3.  **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
4.  **Apply database migrations:**
    ```sh
    python manage.py migrate
    ```
5.  **Run the development server:**
    ```sh
    python manage.py runserver
    ```
The API will be available at `https://kukukonnect-6aa0bdb81a64.herokuapp.com/api/`.
## API Documentation
API documentation is available through Swagger UI and ReDoc.
*   **Swagger UI:** `https://kukukonnect-6aa0bdb81a64.herokuapp.com/api/schema/swagger-ui/`
*   **ReDoc:** `https://kukukonnect-6aa0bdb81a64.herokuapp.com/api/schema/redoc/`
## Usage









