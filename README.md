<img width="1570" alt="Swagger_Current_State" src="https://github.com/NBDor/Resource-Management-System/assets/39236325/7fbdaea4-22ed-4e4f-91f9-36d56e49cf5d">Introduction:

The Resource Management System is a FastAPI-based application that manages the processing and classification of various resources, including herbs, minerals, and wood. The system is designed to handle the acquisition of raw resources from separate sources, process them, and store them in a database. Additionally, the system acts as a classifier, determining the appropriate processing steps for incoming resources based on client specifications and input data evaluation.

Features
- Resource Acquisition: The system retrieves raw resources (Herb, Mineral, and Wood) from separate sources and stores them in the database.
- Resource Classification: The system classifies the incoming resources based on client specifications and input data evaluation, determining the appropriate processing steps.
- Resource Processing: The system processes the raw resources and creates a new "Material" entity, which represents the processed resource.
- Asynchronous Processing: The classification and other post-initial-save processes are handled asynchronously using Celery, with separate queues for each task.

Technologies Used
- Backend: FastAPI, Python
- Database: PostgreSQL
- Asynchronous Processing: Celery
- Message Broker: RabbitMQ

Installation and Setup
- Clone the repository:
git clone https://github.com/your-username/resource-management-system.git
- Create a virtual environment and activate it:
python -m venv venv
source venv/bin/activate
- Install the required dependencies:
pip install -r requirements.txt
- Set up the PostgreSQL database and update the connection details in the config.py file.
- Set up the RabbitMQ message broker and update the connection details in the config.py file.
- Run the Celery worker in one terminal:
celery -A app.celery worker --beat --loglevel=info
- Run the FastAPI application in another terminal:
uvicorn app.main:app --reload

<div style="text-align: center;">
![Swagger Current State](Swagger_Current_State.png)
</div>




License
This project is licensed under the MIT License.
