import React from 'react';
import { Container, Alert } from 'react-bootstrap';

const HotelDetailsPage: React.FC = () => {
  return (
    <Container>
      <Alert variant="info">
        <h4>Hotel Details</h4>
        <p>This page will show detailed hotel information and booking options.</p>
      </Alert>
    </Container>
  );
};

export default HotelDetailsPage;
