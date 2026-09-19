import axios from "axios";

// ─── Axios Instance ────────────────────────────────────────────────────
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
  timeout: 12000,
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("talent_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      sessionStorage.removeItem("talent_token");
      sessionStorage.removeItem("talent_user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ─── Auth ──────────────────────────────────────────────────────────────
export const login = async (credentials) => {
  const { data } = await api.post("/auth/login", credentials);
  return data; // { access_token, token_type, user }
};

export const getCurrentUser = async () => {
  const { data } = await api.get("/auth/me");
  return data;
};

// ─── Profile ───────────────────────────────────────────────────────────
export const getMyProfile = async () => {
  const { data } = await api.get("/profiles/me");
  return data;
};

export const updateMyProfile = async (payload) => {
  const { data } = await api.put("/profiles/me", payload);
  return data;
};

// ─── Skills ────────────────────────────────────────────────────────────
export const getSkillCatalog = async (params = {}) => {
  const { data } = await api.get("/skills", { params });
  return data;
};

export const getEmployeeSkills = async (employeeId) => {
  const { data } = await api.get(`/employees/${employeeId}/skills`);
  return data;
};

export const addEmployeeSkill = async (employeeId, payload) => {
  const { data } = await api.post(`/employees/${employeeId}/skills`, payload);
  return data;
};

// ─── Roles & Matching ──────────────────────────────────────────────────
export const getRoles = async (params = {}) => {
  const { data } = await api.get("/roles", { params });
  return data;
};

export const getEmployeeMatches = async (employeeId) => {
  const { data } = await api.get(`/employees/${employeeId}/matches`);
  return data;
};

export const generateMatches = async (employeeId, payload = {}) => {
  const { data } = await api.post(`/employees/${employeeId}/matches/generate`, payload);
  return data;
};

// ─── Skill Gaps ────────────────────────────────────────────────────────
export const getSkillGaps = async (employeeId) => {
  const { data } = await api.get(`/employees/${employeeId}/skill-gaps`);
  return data;
};

// ─── Courses & Recommendations ─────────────────────────────────────────
export const getCourses = async (params = {}) => {
  const { data } = await api.get("/courses", { params });
  return data;
};

export const getRecommendations = async (employeeId) => {
  const { data } = await api.get(`/employees/${employeeId}/recommendations`);
  return data;
};

// ─── Roadmap ───────────────────────────────────────────────────────────
export const getRoadmap = async (employeeId) => {
  const { data } = await api.get(`/employees/${employeeId}/roadmap`);
  return data;
};

// ─── Employees (HR) ────────────────────────────────────────────────────
export const getEmployees = async (params = {}) => {
  const { data } = await api.get("/employees", { params });
  return data;
};

export const getEmployee = async (employeeId) => {
  const { data } = await api.get(`/employees/${employeeId}`);
  return data;
};

// ─── HR Analytics ──────────────────────────────────────────────────────
export const getHRAnalytics = async () => {
  const { data } = await api.get("/hr/analytics");
  return data;
};

export const getHREmployees = async (params = {}) => {
  const { data } = await api.get("/hr/employees", { params });
  return data;
};

// ─── Career Assistant ──────────────────────────────────────────────────
export const sendAssistantMessage = async (payload) => {
  const { data } = await api.post("/assistant/chat", payload);
  return data; // { reply, suggestions }
};

export default api;
