# REST API Specification

Base URL: `http://localhost:8000/api`

All endpoints return JSON. Authenticated endpoints require a Bearer token in the `Authorization` header:
`Authorization: Bearer <access_token>`

---

## 1. System & Health

### `GET /api/health`
Checks server and API availability.
- **Auth**: None
- **Response**:
  ```json
  {
    "status": "ok"
  }
  ```

---

## 2. Authentication

### `POST /api/auth/login`
Authenticates a user and generates a JWT access token.
- **Auth**: None
- **Request Body**:
  ```json
  {
    "email": "admin1@talent.local",
    "password": "AdminPassword123!"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5c...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "admin1@talent.local",
      "full_name": "System Administrator 1",
      "role": "admin",
      "is_active": true
    }
  }
  ```

### `GET /api/auth/me`
Fetches the currently authenticated user's profile.
- **Auth**: Bearer Token
- **Response** (`200 OK`):
  ```json
  {
    "id": 1,
    "email": "admin1@talent.local",
    "full_name": "System Administrator 1",
    "role": "admin",
    "is_active": true
  }
  ```

---

## 3. Profiles (Self Service)

### `GET /api/profiles/me`
Retrieves the authenticated employee's full profile and skills.
- **Auth**: Bearer Token (Employee, HR, Admin)

### `PUT /api/profiles/me`
Updates the authenticated employee's profile bio, location, education, etc.
- **Auth**: Bearer Token

---

## 4. Employees Management

### `GET /api/employees`
Lists employees with optional department filtering.
- **Auth**: HR or Admin
- **Query Params**: `department` (string), `skip` (int), `limit` (int)

### `GET /api/employees/{employee_id}`
Retrieves employee details.
- **Auth**: HR/Admin or Self (Employee can only view their own record)

### `POST /api/employees`
Creates a new employee record and associated user account.
- **Auth**: Admin Only

### `PUT /api/employees/{employee_id}`
Updates an employee's details.
- **Auth**: HR/Admin or Self

---

## 5. Skills Taxonomy & Employee Skills

### `GET /api/skills`
Lists all standardized skills across domain categories.
- **Auth**: Any authenticated user
- **Query Params**: `category` (string)

### `POST /api/skills`
Adds a new skill to the taxonomy.
- **Auth**: HR or Admin

### `GET /api/employees/{employee_id}/skills`
Retrieves all skills and verification evidence for an employee.
- **Auth**: HR/Admin or Self

### `POST /api/employees/{employee_id}/skills`
Adds or updates a skill and attached evidence for an employee.
- **Auth**: HR/Admin or Self

---

## 6. Roles & Benchmarks

### `GET /api/roles`
Lists all organizational roles with required skills and importance weights.
- **Auth**: Any authenticated user

### `GET /api/roles/{role_id}`
Retrieves specific role details with required proficiencies.
- **Auth**: Any authenticated user

### `POST /api/roles`
Creates a new role specification.
- **Auth**: HR or Admin

---

## 7. Role Matching & Recommendations

### `GET /api/employees/{employee_id}/matches`
Retrieves evaluated role matches with match percentages, satisfied skills, and missing skills.
- **Auth**: HR/Admin or Self

### `POST /api/employees/{employee_id}/matches/generate`
Triggers role matching algorithm recalculation.
- **Auth**: HR/Admin or Self

### `GET /api/employees/{employee_id}/skill-gaps`
Retrieves categorized skill gaps (critical, high, medium, low) for an employee.
- **Auth**: HR/Admin or Self

---

## 8. Courses & Learning Roadmaps

### `GET /api/courses`
Lists available learning courses in the catalog.
- **Auth**: Any authenticated user

### `GET /api/employees/{employee_id}/recommendations`
Retrieves prioritized course recommendations tailored to close employee skill gaps.
- **Auth**: HR/Admin or Self

### `GET /api/employees/{employee_id}/roadmap`
Retrieves the personalized, multi-phase career acceleration roadmap for an employee.
- **Auth**: HR/Admin or Self

---

## 9. Career Assistant

### `POST /api/assistant/chat`
Converses with the career and talent development assistant.
- **Auth**: Any authenticated user
- **Request Body**:
  ```json
  {
    "message": "What skills should I learn to become a Senior Software Engineer?"
  }
  ```

---

## 10. HR Analytics

### `GET /api/hr/analytics`
Returns aggregate organizational talent metrics:
- **Auth**: HR or Admin
- **Response** (`200 OK`):
  ```json
  {
    "total_employees": 12,
    "profile_completion_rate": 84.5,
    "total_skills": 24,
    "emerging_skill_gaps": 7,
    "total_role_matches": 84,
    "learning_recommendations": 36,
    "skill_distribution": [
      { "skill": "Python", "category": "Backend Engineering", "count": 6, "avg_proficiency": 3.8 }
    ],
    "department_skills": [
      { "department": "Engineering", "headcount": 5, "total_skills": 22, "avg_completion": 88.0 }
    ],
    "skill_gaps": [
      { "skill": "Kubernetes", "category": "Cloud & DevOps", "affected_employees": 4, "avg_gap_size": 2.0 }
    ],
    "role_demand": [
      { "role": "Senior Software Engineer", "department": "Engineering", "level": "Senior", "evaluated_candidates": 12, "avg_match_score": 58.2 }
    ],
    "learning_categories": [
      { "provider": "Coursera", "course_count": 3, "assigned_count": 14 }
    ]
  }
  ```

### `GET /api/hr/skills`
Returns organization-wide skill distribution.
- **Auth**: HR or Admin

### `GET /api/hr/skill-gaps`
Returns organization-wide skill gap hotspots.
- **Auth**: HR or Admin

### `GET /api/hr/roles`
Returns role bench strength and candidate match averages.
- **Auth**: HR or Admin

### `GET /api/hr/employees`
Returns employee roster with department filtering for HR.
- **Auth**: HR or Admin
