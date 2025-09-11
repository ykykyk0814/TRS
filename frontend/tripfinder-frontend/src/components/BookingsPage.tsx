import React from 'react';
import { Container, Alert } from 'react-bootstrap';

const BookingsPage: React.FC = () => {
  return (
    <Container>
      <Alert variant="info">
        <h4>My Bookings</h4>
        <p>This page will show user's booking history and current reservations.</p>
      </Alert>
    </Container>
  );
};

export default BookingsPage;
