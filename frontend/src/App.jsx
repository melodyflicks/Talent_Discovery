import { Container, Nav, Navbar } from "react-bootstrap";
import { Link } from "react-router-dom";
import AppRoutes from "./routes";

export default function App() {
  return <><Navbar bg="dark" variant="dark" expand="lg"><Container><Navbar.Brand as={Link} to="/">Talent Discovery</Navbar.Brand><Nav><Nav.Link as={Link} to="/">Dashboard</Nav.Link><Nav.Link as={Link} to="/skills">Skills</Nav.Link><Nav.Link as={Link} to="/roles">Roles</Nav.Link></Nav></Container></Navbar><Container className="py-4"><AppRoutes /></Container></>;
}
