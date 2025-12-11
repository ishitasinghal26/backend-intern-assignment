Organization Management Service 
(A Multi-Tenant Backend System built with FastAPI & MongoDB)

This project implements a scalable backend service for managing organizations in a multi-tenant architecture. Each organization receives its own dedicated MongoDB collection, and all global metadata is stored in a master database. Admin authentication is powered by JWT, and passwords are securely hashed using Argon2.

📌 Features

Organization Management  
a) Create a new organization  
b) Fetch organization details  
c) Update organization name, admin credentials, and dynamic collection name  
d) Delete organization along with its admin and dynamic collection

Multi-Tenant Architecture  
a) Master database stores global metadata  
b) Each organization gets its own dynamic MongoDB collection
  - Example: org_testorg

Admin Authentication  
a) Secure password hashing using Argon2 (recommended modern password hashing)  
b) Admin login generates a JWT token containing:
   - Admin ID (sub)
   - Organization ID (org_id)
c) Protected endpoints require valid JWT authentication

📌 Tech Stack  
Backend Framework: FastAPI  
Database: MongoDB (PyMongo)  
Password Hashing: Argon2 (Passlib[argon2])  
Auth: JWT (PyJWT)  
Server: Uvicorn  
Environment: Python 3.10+

📌 Instructions to Run the Application

1️) Clone the repository: Run the following commands in your terminal.
- git clone repo-url
- cd project-assignment

2️) Create and activate a virtual environment: Run the following commands in your terminal.
- python -m venv venv
- venv\Scripts\activate # Windows

3️) Install dependencies: Run the following command in your terminal.
- pip install -r requirements.txt

4️) Configure environment variables  
Create a .env file: (inside your project folder)  

MONGO_URI=mongodb://localhost:27017  
MONGO_DB_NAME=org_master_db  
JWT_SECRET=supersecretkey123  
JWT_ALGORITHM=HS256  
JWT_EXP_MINUTES=60

5️) Start the server: Run the following command in your terminal.  
- uvicorn app.main:app --reload

📌 API docs available at: http://localhost:8000/docs

📌 Testing the Endpoints (Postman)

- Create Organization  
POST /org/create  
→ Body (raw → json):  
{ "organization_name": "TestOrg", "email": "admin@test.com", "password": "Password123" }

- Admin Login  
POST /admin/login  
→ Body (raw → json):  
{ "email": "admin@test.com", "password": "Password123" }  
→ Response: { "access_token": "<JWT_TOKEN>", "token_type": "bearer" }

- Get Organization  
GET /org/get?organization_name=TestOrg

- Update Organization (Requires JWT)  
PUT /org/update  
→ Headers: Authorization: Bearer <JWT_TOKEN>  
→ Body (raw → json):  
{ "organization_name": "TestOrgUpdated", "email": "newadmin@test.com", "password": "NewPass123" }

- Delete Organization (Requires JWT)  
DELETE /org/delete?organization_name=TestOrgUpdated  
→ Headers: Authorization: Bearer <JWT_TOKEN>
