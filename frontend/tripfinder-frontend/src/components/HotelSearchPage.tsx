import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import hotelService, { Hotel, HotelSearchParams } from '../services/hotelService';
import LoadingSpinner from './LoadingSpinner';

const HotelSearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useState<HotelSearchParams>({
    destination: '',
    check_in: '',
    check_out: '',
    guests: 1,
    rooms: 1,
  });
  const [hotels, setHotels] = useState<Hotel[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasSearched, setHasSearched] = useState(false);

  const navigate = useNavigate();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setSearchParams(prev => ({
      ...prev,
      [name]: name === 'guests' || name === 'rooms' ? parseInt(value) : value,
    }));
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const results = await hotelService.searchHotels(searchParams);
      setHotels(results);
      setHasSearched(true);
    } catch (err: any) {
      setError(err.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleHotelClick = (hotelId: string) => {
    navigate(`/hotel/${hotelId}`);
  };

  return (
    <Container>
      <Row>
        <Col lg={4} className="mb-4">
          <Card className="shadow-sm">
            <Card.Header>
              <h5 className="mb-0">Search Hotels</h5>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={handleSearch}>
                <Form.Group className="mb-3">
                  <Form.Label>Destination</Form.Label>
                  <Form.Control
                    type="text"
                    name="destination"
                    value={searchParams.destination}
                    onChange={handleInputChange}
                    placeholder="Enter city or location"
                    required
                  />
                </Form.Group>

                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Check-in</Form.Label>
                      <Form.Control
                        type="date"
                        name="check_in"
                        value={searchParams.check_in}
                        onChange={handleInputChange}
                        required
                      />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Check-out</Form.Label>
                      <Form.Control
                        type="date"
                        name="check_out"
                        value={searchParams.check_out}
                        onChange={handleInputChange}
                        required
                      />
                    </Form.Group>
                  </Col>
                </Row>

                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Guests</Form.Label>
                      <Form.Control
                        as="select"
                        name="guests"
                        value={searchParams.guests}
                        onChange={handleInputChange}
                      >
                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
                          <option key={num} value={num}>{num}</option>
                        ))}
                      </Form.Control>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Rooms</Form.Label>
                      <Form.Control
                        as="select"
                        name="rooms"
                        value={searchParams.rooms}
                        onChange={handleInputChange}
                      >
                        {[1, 2, 3, 4, 5].map(num => (
                          <option key={num} value={num}>{num}</option>
                        ))}
                      </Form.Control>
                    </Form.Group>
                  </Col>
                </Row>

                <Button
                  type="submit"
                  variant="primary"
                  className="w-100"
                  disabled={loading}
                >
                  {loading ? 'Searching...' : 'Search Hotels'}
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={8}>
          {error && (
            <Alert variant="danger" className="mb-4">
              {error}
            </Alert>
          )}

          {loading && (
            <div className="text-center">
              <LoadingSpinner />
            </div>
          )}

          {!loading && hasSearched && hotels.length === 0 && (
            <Alert variant="info">
              No hotels found for your search criteria. Try adjusting your search parameters.
            </Alert>
          )}

          {!loading && hotels.length > 0 && (
            <div>
              <h4 className="mb-4">Search Results ({hotels.length} hotels found)</h4>
              {hotels.map((hotel) => (
                <Card
                  key={hotel.id}
                  className="mb-3 shadow-sm hotel-card"
                  style={{ cursor: 'pointer' }}
                  onClick={() => handleHotelClick(hotel.id)}
                >
                  <Row className="g-0">
                    <Col md={4}>
                      <img
                        src={hotel.image_url}
                        alt={hotel.name}
                        className="img-fluid rounded-start h-100"
                        style={{ objectFit: 'cover' }}
                      />
                    </Col>
                    <Col md={8}>
                      <Card.Body>
                        <div className="d-flex justify-content-between align-items-start">
                          <div>
                            <Card.Title className="h5">{hotel.name}</Card.Title>
                            <p className="text-muted mb-2">{hotel.location}</p>
                            <p className="mb-2">{hotel.description}</p>
                            <div className="mb-2">
                              <span className="badge bg-primary me-1">
                                ⭐ {hotel.rating}/5
                              </span>
                              <span className="badge bg-success">
                                {hotel.available_rooms} rooms available
                              </span>
                            </div>
                            <div>
                              {hotel.amenities.slice(0, 3).map((amenity, index) => (
                                <span key={index} className="badge bg-light text-dark me-1">
                                  {amenity}
                                </span>
                              ))}
                              {hotel.amenities.length > 3 && (
                                <span className="text-muted">
                                  +{hotel.amenities.length - 3} more
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="text-end">
                            <h4 className="text-primary mb-0">
                              ${hotel.price_per_night}
                            </h4>
                            <small className="text-muted">per night</small>
                          </div>
                        </div>
                      </Card.Body>
                    </Col>
                  </Row>
                </Card>
              ))}
            </div>
          )}

          {!hasSearched && !loading && (
            <div className="text-center py-5">
              <h5 className="text-muted">Enter your search criteria to find hotels</h5>
              <p className="text-muted">Use the search form on the left to get started</p>
            </div>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default HotelSearchPage;
