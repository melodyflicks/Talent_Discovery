import { Card } from "react-bootstrap";
export default function ChartCard({ title, children }) { return <Card className="chart-card h-100"><Card.Body><Card.Title className="h6 mb-3">{title}</Card.Title>{children}</Card.Body></Card>; }
