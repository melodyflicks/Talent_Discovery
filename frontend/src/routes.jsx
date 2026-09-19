
import { Navigate, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import Skills from "./pages/Skills";
import Roles from "./pages/Roles";
import SkillGap from "./pages/SkillGap";
import Roadmap from "./pages/Roadmap";
import CareerAssistant from "./pages/CareerAssistant";
import HRDashboard from "./pages/HRDashboard";
import AppLayout from "./components/common/AppLayout";
import ProtectedRoute from "./components/common/ProtectedRoute";

export default function AppRoutes() {
  const employeePage = (page) => <ProtectedRoute><AppLayout>{page}</AppLayout></ProtectedRoute>;
  return <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/dashboard" element={employeePage(<Dashboard />)} />
    <Route path="/profile" element={employeePage(<Profile />)} />
    <Route path="/skills" element={employeePage(<Skills />)} />
    <Route path="/roles" element={employeePage(<Roles />)} />
    <Route path="/skill-gaps" element={employeePage(<SkillGap />)} />
    <Route path="/roadmap" element={employeePage(<Roadmap />)} />
    <Route path="/career-assistant" element={employeePage(<CareerAssistant />)} />
    <Route path="/hr" element={<ProtectedRoute roles={["hr", "admin"]}><AppLayout><HRDashboard /></AppLayout></ProtectedRoute>} />
    <Route path="*" element={<Navigate to="/dashboard" replace />} />
  </Routes>;
}
