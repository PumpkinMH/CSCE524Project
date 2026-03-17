# **MedTracker**

MedTracker is a robust, n-tier medication tracking application built with Django and PostgreSQL. It is designed to help users manage their daily medication schedules, track doses, and maintain a historical log of their treatments, ensuring medical adherence through a clean and intuitive interface.

## **🚀 Overview**

This project follows a professional n-tier architectural pattern, which separates concerns into distinct layers:

1. **Data Layer**: Powered by PostgreSQL, using UUIDs for secure and unique identification of all records.  
2. **Business Layer**: Core Python logic and Django models that handle the complex relationships between medications, schedules, and dose logs.  
3. **Service Layer**: A RESTful API and routing system built with Django REST Framework to facilitate data flow.  
4. **Presentation Layer**: A responsive frontend built using Django Templates, HTML5, and CSS3.

## **🛠️ Tech Stack**

* **Backend**: Python 3.10+, Django 5.2.12  
* **Database**: PostgreSQL  
* **API**: Django REST Framework  
* **Server**: Gunicorn (Production), Django Dev Server (Local)  
* **Tools**: VS Code, Beekeeper Studio  
* **Hosting**: Render

## **📂 Project Structure**

The repository is organized to clearly separate the application logic from the configuration files:

* /backend: Contains the core Django application, models, views, and business logic.  
* /backend/api/templates: The presentation layer containing the UI components.  
* create\_db.sql: The database schema initialization script.  
* fill\_db.sql: The initial seed data for the database.  
* requirements.txt: Comprehensive list of Python dependencies.

## **📋 Installation & Deployment**

For a detailed, step by step walkthrough on how to go from "Download ZIP" to "cool, that works\!", please refer to our full deployment documentation  
The guide covers:

* Local setup with VS Code and Beekeeper Studio.  
* Database initialization and configuration.  
* Virtual environment management.  
* Cloud deployment to Render.

## **🧪 Verification**

Once installed, you can verify the setup by navigating to your local or hosted URL. A successful setup will display the MedTracker dashboard, populated with the medications and schedules imported from the data layer.

## **🤝 Contributing**

This project was built as part of the CSCE524 project. If you have suggestions or improvements, feel free to fork the repository and submit a pull request.
