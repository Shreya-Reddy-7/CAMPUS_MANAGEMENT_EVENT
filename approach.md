# Documenting My Process
## 1. Assumptions and Decisions

- The system will be used by ~50 colleges with ~500 students, and ~20 events each semester.

- In the prototype, the system will use a Single Database (SQLite), however, in a scaling situation, a proper DB such as Postgres would be more appropriate.

- All Event IDs are unique in the scope of the database. (I made the decision to use a single database to keep things as simple as possible since they arent unique to each college).

- Students have to register before logging in (which would be handled in the authentication flow).

- The application has been broken down into two parts:

Admin Portal (Web) - create/manage events, reports.

Student App (Web/Mobile) - browse events, register for events, submit feedback.

- Reports we considered:

- event popularity (registrations per event).

- student participation (events attended per student). 

- average feedback rating.

## 2. Brainstorming with LLM Tools

I used ChatGPT (GPT-5) as my AI programming assistant to brainstorm code snippets.

I used ChatGPT in our conversations to discuss the databas schema, route structure of the Flask app, templates for the front end, and REST endpoints.

We also had conversations about styling (CSS) and the JavaScript functionality of both the admin and the student portals.

I was able to get the AI to assist me with fixing errors; for example, dependencies, folder references, and other mistakes.

I will add screenshots of my AI conversations here.
<img width="2401" height="1294" alt="Screenshot (218)" src="https://github.com/user-attachments/assets/6d14d16d-147b-41d7-91d6-2709e8467223" />

<img width="2408" height="1306" alt="Screenshot (219)" src="https://github.com/user-attachments/assets/e88494d3-e615-4803-97c7-ea0c9fc9187b" />

## 3. Following vs Deviating from AI Suggestions

Following AI Suggestions

- Database schema - events, students, registrations, and feedback tables.

- Flask routes for registering students, creating events, submitting feedback, and generating reports.

- Base code for the Flask app routes.
