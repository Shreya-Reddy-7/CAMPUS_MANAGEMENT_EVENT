# Campus Event Management

A simple Campus Event Management System for colleges to create events, and students to register, complete feedback and view reports. 

# Features 
Admin Portal (Web) 
-create and manage events (Hackathons, Workshops, Fests, etc..)
-generate reports (event popularity, student activity, average feedback) 
Student App (Web/Mobile) 
-browse upcoming events 
-register for events 
-complete feedback after attending 

 # 🗂️ Project Structure 
```│── app.py # main flask app 
│── reset_db.py # reset db script
│── requirements.txt # python dependencies 
│── events.db # sqlite db 
│── design_doc.md # design documentation 
│
├── templates/ # html templates 
│ ├── index.html 
│ ├── admin.html 
│ └── student.html 
│ 
├── static/ # static files 
│ ├── css/
│ │ └── style.css 
│ └── js/
│ ├── admin.js 
│ ├── student.js 
│ └── auth.js 
│ 
└── instance/ # flask instance folder
