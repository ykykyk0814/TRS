import React from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../App';

const HomePage: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div>
      {/* Hero Section */}
      <div className="bg-primary text-white py-5 mb-5">
        <Container>
          <Row className="align-items-center">
            <Col lg={6}>
              <h1 className="display-4 fw-bold mb-4">
                Find Your Perfect Stay with TripFinder
              </h1>
              <p className="lead mb-4">
                Discover amazing hotels, compare prices, and book your dream vacation
                with our intelligent travel recommendation system.
              </p>
              {isAuthenticated ? (
                <Button as={Link} to="/search" variant="light" size="lg">
                  Search Hotels Now
                </Button>
              ) : (
                <div>
                  <Button as={Link} to="/register" variant="light" size="lg" className="me-3">
                    Get Started
                  </Button>
                  <Button as={Link} to="/login" variant="outline-light" size="lg">
                    Sign In
                  </Button>
                </div>
              )}
            </Col>
            <Col lg={6}>
              <img
                src="https://via.placeholder.com/600x400/4285f4/ffffff?text=TripFinder"
                alt="Travel"
                className="img-fluid rounded"
              />
            </Col>
          </Row>
        </Container>
      </div>

      {/* Features Section */}
      <Container>
        <Row className="mb-5">
          <Col lg={12} className="text-center mb-5">
            <h2 className="display-5 fw-bold">Why Choose TripFinder?</h2>
            <p className="lead text-muted">
              Experience the future of travel booking with our advanced features
            </p>
          </Col>
        </Row>

        <Row>
          <Col md={4} className="mb-4">
            <Card className="h-100 text-center border-0 shadow-sm">
              <Card.Body className="p-4">
                <div className="bg-primary bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '80px', height: '80px'}}>
                  <i className="fas fa-search text-primary" style={{fontSize: '2rem'}}></i>
                </div>
                <Card.Title>AI-Powered Search</Card.Title>
                <Card.Text>
                  Our intelligent vector search finds the perfect hotels based on your preferences
                  and travel history.
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>

          <Col md={4} className="mb-4">
            <Card className="h-100 text-center border-0 shadow-sm">
              <Card.Body className="p-4">
                <div className="bg-success bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '80px', height: '80px'}}>
                  <i className="fas fa-shield-alt text-success" style={{fontSize: '2rem'}}></i>
                </div>
                <Card.Title>Secure Booking</Card.Title>
                <Card.Text>
                  Your personal information and payments are protected with enterprise-grade
                  security measures.
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>

          <Col md={4} className="mb-4">
            <Card className="h-100 text-center border-0 shadow-sm">
              <Card.Body className="p-4">
                <div className="bg-info bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '80px', height: '80px'}}>
                  <i className="fas fa-chart-line text-info" style={{fontSize: '2rem'}}></i>
                </div>
                <Card.Title>Real-time Analytics</Card.Title>
                <Card.Text>
                  Monitor your bookings and travel patterns with comprehensive analytics
                  and insights.
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* API Status Section */}
        <Row className="mt-5">
          <Col lg={12}>
            <Card className="bg-light">
              <Card.Body className="text-center">
                <h5>Backend API Status</h5>
                <div className="d-flex justify-content-center align-items-center">
                  <div className="bg-success rounded-circle me-2" style={{width: '12px', height: '12px'}}></div>
                  <span className="text-success">Connected to FastAPI Backend</span>
                </div>
                <small className="text-muted">
                  Powered by FastAPI with JWT authentication, Prometheus monitoring, and AI vector search
                </small>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default HomePage;
