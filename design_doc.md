# Campus Event Management Platform - Design Document

## 1. Assumptions
- Each college has its own students and events, but IDs are unique across the whole system.
- Events can be hackathons, workshops, talks, fests, etc.
- Students must register before attending and can provide feedback afterwards.
- Reports are for Admin staff to analyze popularity, participation, and feedback.

## 2. Data to Track
- Event details: title, type, capacity, college_id.
- Student details: name, email, college_id.
- Registrations: event_id, student_id.
- Attendance: event_id, student_id, check-in status.
- Feedback: event_id, student_id, rating (1–5), comments.

## 3. Database Schema
### Tables
- **Colleges(id, name)**
- **Students(id, name, email, college_id)**
- **Events(id, title, type, capacity, college_id)**
- **Registrations(id, student_id, event_id, attended)**
- **Feedback(id, student_id, event_id, rating, comments)**

## 4. API Design
- **POST /register** → Create student account
- **POST /login** → Authenticate student/admin
- **POST /events** → Create event (admin only)
- **GET /events** → List all events
- **POST /events/{id}/register** → Student registers for event
- **POST /events/{id}/attendance** → Mark attendance
- **POST /feedback** → Submit feedback
- **GET /reports/event_popularity**
- **GET /reports/top_active_students**
- **GET /reports/average_feedback**

## 5. Workflows
### Student
1. Register → Login → Browse events → Register → Attend → Give feedback

### Admin
1. Login → Create events → View reports (popularity, participation, feedback)

## 6. Edge Cases
- Duplicate registrations → prevented with unique constraint on (student_id, event_id).
- Event full → capacity check before registering.
- Cancelled event → mark inactive so it won’t show.
- Missing feedback → allowed, reports use only available data.

## 7. Reports
- **Event Popularity** → total registrations per event.
- **Top Active Students** → students attending most events.
- **Average Feedback** → average rating per event.

