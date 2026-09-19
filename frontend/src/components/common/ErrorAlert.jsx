import { Alert } from "react-bootstrap";
export default function ErrorAlert({ message }) { return <Alert variant="danger" role="alert">{message}</Alert>; }
