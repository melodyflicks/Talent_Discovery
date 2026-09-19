import { Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import Skills from "./pages/Skills";
import Roles from "./pages/Roles";
import SkillGap from "./pages/SkillGap";
import Roadmap from "./pages/Roadmap";
import CareerAssistant from "./pages/CareerAssistant";
import HRDashboard from "./pages/HRDashboard";

export default function AppRoutes() { return <Routes><Route path="/" element={<Dashboard />} /><Route path="/login" element={<Login />} /><Route path="/profile" element={<Profile />} /><Route path="/skills" element={<Skills />} /><Route path="/roles" element={<Roles />} /><Route path="/skill-gap" element={<SkillGap />} /><Route path="/roadmap" element={<Roadmap />} /><Route path="/assistant" element={<CareerAssistant />} /><Route path="/hr" element={<HRDashboard />} /></Routes>; }
