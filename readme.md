# HandsOn – A Community-Driven Social Volunteering Platform

---
### For Admin Testing in Production Use:
    ```bash
    admin: admin@admin.com
    password: 123
    ```

## 1. Project Overview

**HandsOn** is a social volunteering platform designed to connect individuals with community-driven volunteer opportunities. Users can discover and join events, post help requests, create teams for long-term initiatives, and track their volunteer impact. This platform aims to encourage social responsibility and community collaboration.

---

## 2. Technologies Used

### Frontend:
- **React.js** – For building the user interface and managing state.
- **Djano** – For server-side rendering and API building
- **Tailwind CSS** – For styling and building responsive layouts.
- **Axios** – For making HTTP requests.
- **Material-UI** – For pre-built React components (buttons, cards, etc.).

### Backend:
- **Django** – Web framework for handling requests.
- **PostgreSQL** – Relational database for storing user, event, and volunteer data.
- **JWT (JSON Web Tokens)** – For handling authentication and authorization.
- **Cors** – For enabling cross-origin requests.
- **Dotenv** – For managing environment variables.
- **DRF** - for API Building.

---

## 3. Features

### Frontend:
- **User Authentication**: Secure login and registration with JWT authentication.
- **Event Discovery**: Users can browse volunteer events, filter them by categories, and join them.
- **Profile Management**: Users can create and update their profile, showcasing their volunteer history.
- **Event Registration**: Easy event sign-up with one-click join functionality.
- **Responsive Design**: Fully responsive design optimized for desktop and mobile devices.

### Backend:
- **User Management**: API to register, log in, and update user profiles.
- **Event Management**: Users and organizations can create, list, and filter volunteer events.
- **Help Requests**: Users can post and offer help requests for ongoing community needs.
- **Impact Tracking**: Track volunteer hours, achievements, and milestones.
- **API Rate Limiting**: Prevents abuse and overuse of the API with rate limiting.

---

## 4. Database Schema

### Key Entities:
- **Users**: Stores user information like email, password (hashed), skills, and causes they support.
- **Events**: Stores event details like title, description, location, date, time, and category.
- **Help Requests**: Stores community requests for help, including the urgency and description.
- **Teams**: Stores information about teams, their members, and associated events.
- **Volunteer Hours**: Tracks hours volunteered by users in different events.
- **Comments**: Allows users to comment on help requests or events.

---

## 5. Setup Instructions

### Frontend:

1. Clone the repository:
    ```bash
    git clone https://github.com/mohammadSelimReza/hands-on-volunteering-platform-frontend.git
    ```

2. Navigate to the project directory:
    ```bash
    cd hands-on-volunteering-platform-frontend
    ```

3. Install dependencies:
    ```bash
    npm install
    ```

4. Create a `.env` file in the root directory and add the following environment variables:
    ```bash
    NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
    ```

5. Open the application in your browser at `http://localhost:3000`.

### Backend:

1. Create a virtual environment and activate it.
2. Clone the repository:
    ```bash
    git clone https://github.com/mohammadSelimReza/hands-on-volunteering-platform.git
    ```

3. Navigate to the project directory:
    ```bash
    cd hands-on-volunteering-platform
    ```

4. Install packages:
    ```bash
    pip install -r requirements.txt
    ```

5. If you want to run locally, in `_backend/settings/base.py` file, turn `DEBUG = True`.

6. Create a `.env` file and add the following:
    ```bash
    SECRET_KEY=1  # (or put a strong value)
    ```

7. It will auto-generate SQLite3.

8. Run migrations:
    ```bash
    py manage.py makemigrations
    ```

9. Migrate the database:
    ```bash
    py manage.py migrate
    ```

10. Create a superuser:
    ```bash
    py manage.py createsuperuser
    ```

11. Finally, start the server:
    ```bash
    py manage.py runserver
    ```

Enjoy!

---

## 6. API Documentation

### Register User
- **Endpoint**: `POST /api/auth/register`
- **Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "password123",
      "name": "John Doe"
    }
    ```
- **Response**:
    - 200: `{ "message": "User registered successfully" }`
    - 400: `{ "error": "Invalid input" }`

### Login User
- **Endpoint**: `POST /api/auth/login`
- **Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "password123"
    }
    ```
- **Response**:
    - 200: `{ "token": "JWT_TOKEN_HERE" }`
    - 401: `{ "error": "Invalid credentials" }`

---

### Event Management

#### Create Event
- **Endpoint**: `POST /api/events`
- **Headers**: `Authorization: Bearer <JWT_TOKEN>`
- **Body**:
    ```json
    {
      "title": "Tree Plantation",
      "description": "Join us to plant trees in the city park",
      "location": "City Park, Downtown",
      "date": "2025-05-01",
      "time": "09:00 AM",
      "category": "Environment"
    }
    ```
- **Response**:
    - 200: `{ "message": "Event created successfully" }`
    - 400: `{ "error": "Invalid event data" }`

#### Get Events
- **Endpoint**: `GET /api/events`
- **Response**:
    - 200: `[ { "id": 1, "title": "Tree Plantation", "date": "2025-05-01", "category": "Environment" }, ... ]`

---

## 7. Running the Project

### Locally:
1. Make sure both the frontend and backend servers are running.
2. Access the frontend at `http://localhost:3000`.
3. Access the backend at `http://localhost:5000`.

### In Production:
1. Set up environment variables for both frontend and backend.
2. Deploy the frontend on platforms like Vercel or Netlify.
3. Deploy the backend on platforms like Heroku or DigitalOcean.
4. Make sure both the frontend and backend are properly connected and functioning.
