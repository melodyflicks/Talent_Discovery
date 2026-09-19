from . import assistant, auth, courses, employees, hr, matching, profiles, roadmap, roles, skill_gaps, skills

routers = [auth.router, employees.router, profiles.router, skills.router, roles.router, matching.router, skill_gaps.router, courses.router, roadmap.router, assistant.router, hr.router]
