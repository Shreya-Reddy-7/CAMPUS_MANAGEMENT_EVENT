# Campus Event Management

A lightweight **Campus Event Management Platform** that allows colleges to create events, and students to register, give feedback, and view reports.


## Features

- **Admin Portal (Web)**  
  - Create and manage events (Hackathons, Workshops, Fests, etc.).  
  - Generate reports (event popularity, student activity, average feedback).  

- **Student App (Web/Mobile)**  
  - Browse upcoming events.  
  - Register for events.  
  - Submit feedback after attending.  


## 🗂️ Project Structure
```CAMPUS_MANAGEMENT_EVENT/
│── app.py # Main Flask app
│── reset_db.py # Script to reset database
│── requirements.txt # Python dependencies
│── events.db # SQLite database
│── design_doc.md # Design documentation
│
├── templates/ # HTML templates
│ ├── index.html
│ ├── admin.html
│ └── student.html
│
├── static/ # Static files
│ ├── css/
│ │ └── style.css
│ └── js/
│ ├── admin.js
│ ├── student.js
│ └── auth.js
│
└── instance/ # Flask instance folder
