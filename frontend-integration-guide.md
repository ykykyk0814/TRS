# TripFinder React Template Integration Guide

## 🚀 Backend-Frontend Integration Setup

### 1. **API Base Configuration**

Create an API configuration file in your React project:

```javascript
// src/config/api.js
const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  API_PREFIX: '/api',
  ENDPOINTS: {
    // Authentication
    AUTH: {
      LOGIN: '/auth/jwt/login',
      REGISTER: '/auth/register',
      LOGOUT: '/auth/jwt/logout',
      ME: '/auth/users/me',
    },
    // Hotels (newly created for template)
    HOTELS: {
      SEARCH: '/hotels/search',
      DETAILS: (id) => `/hotels/${id}`,
      BOOK: '/hotels/book',
      USER_BOOKINGS: '/hotels/bookings/user',
    },
    // Flights (existing backend)
    TICKETS: {
      LIST: '/tickets',
      CREATE: '/tickets',
      BY_DESTINATION: (dest) => `/tickets/destination/${dest}`,
    },
    // Vector Search (AI features)
    VECTOR: {
      SEARCH: '/vector/search',
      ADD_CONTENT: '/vector/content',
    },
    // User Preferences
    PREFERENCES: {
      GET: '/preferences',
      CREATE: '/preferences',
    }
  }
};

export default API_CONFIG;
```

### 2. **Authentication Service**

```javascript
// src/services/authService.js
import axios from 'axios';
import API_CONFIG from '../config/api';

class AuthService {
  constructor() {
    this.baseURL = `${API_CONFIG.BASE_URL}${API_CONFIG.API_PREFIX}`;
    this.token = localStorage.getItem('auth_token');
    
    // Setup axios interceptor for authentication
    axios.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });
  }

  async login(email, password) {
    try {
      const response = await axios.post(
        `${this.baseURL}${API_CONFIG.ENDPOINTS.AUTH.LOGIN}`,
        { username: email, password }
      );
      
      this.token = response.data.access_token;
      localStorage.setItem('auth_token', this.token);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  async register(userData) {
    try {
      const response = await axios.post(
        `${this.baseURL}${API_CONFIG.ENDPOINTS.AUTH.REGISTER}`,
        userData
      );
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  }

  async getCurrentUser() {
    try {
      const response = await axios.get(
        `${this.baseURL}${API_CONFIG.ENDPOINTS.AUTH.ME}`
      );
      return response.data;
    } catch (error) {
      throw new Error('Failed to get user info');
    }
  }

  logout() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  isAuthenticated() {
    return !!this.token;
  }
}

export default new AuthService();
```

### 3. **Hotel Service (for Template)**

```javascript
// src/services/hotelService.js
import axios from 'axios';
import API_CONFIG from '../config/api';

class HotelService {
  constructor() {
    this.baseURL = `${API_CONFIG.BASE_URL}${API_CONFIG.API_PREFIX}`;
  }

  async searchHotels(searchParams) {
    try {
      const response = await axios.post(
        `${this.baseURL}${API_CONFIG.ENDPOINTS.HOTELS.SEARCH}`,
        searchParams
      );
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Hotel search failed');
    }
  }

  async getHotelDetails(hotelId) {
    try {
      const response = await axios.get(
        `${this.baseURL}${API_CONFIG.ENDPOINTS.HOTELS.DETAILS(hotelId)}`
      );
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get hotel details');
    }
  }

  async bookHotel(bookingData) {
    try {
      const response = await axios.post(
        `${this.baseURL}${API_CONFIG.ENDPOINTS.HOTELS.BOOK}`,
        bookingData
      );
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Booking failed');
    }
  }

  async getUserBookings() {
    try {
      const response = await axios.get(
        `${this.baseURL}${API_CONFIG.ENDPOINTS.HOTELS.USER_BOOKINGS}`
      );
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get bookings');
    }
  }
}

export default new HotelService();
```

### 4. **Data Model Mappers**

```javascript
// src/utils/dataMappers.js

// Map backend hotel data to template expected format
export const mapHotelData = (backendHotel) => ({
  id: backendHotel.id,
  title: backendHotel.name,
  description: backendHotel.description,
  location: backendHotel.location,
  price: backendHotel.price_per_night,
  rating: backendHotel.rating,
  image: backendHotel.image_url,
  amenities: backendHotel.amenities,
  availableRooms: backendHotel.available_rooms,
  // Add any template-specific fields
  gallery: [backendHotel.image_url], // Template might expect image gallery
  reviews: [], // Add reviews if available
  coordinates: { lat: 0, lng: 0 }, // Add coordinates if available
});

// Map template search data to backend format
export const mapSearchRequest = (templateSearch) => ({
  destination: templateSearch.destination,
  check_in: templateSearch.checkIn,
  check_out: templateSearch.checkOut,
  guests: templateSearch.guests,
  rooms: templateSearch.rooms,
  price_min: templateSearch.priceRange?.min,
  price_max: templateSearch.priceRange?.max,
  amenities: templateSearch.amenities,
});

// Map template booking data to backend format
export const mapBookingRequest = (templateBooking) => ({
  hotel_id: templateBooking.hotelId,
  check_in: templateBooking.checkIn,
  check_out: templateBooking.checkOut,
  guests: templateBooking.guests,
  rooms: templateBooking.rooms,
  special_requests: templateBooking.specialRequests,
});
```

### 5. **Environment Configuration**

Create a `.env` file in your React project:

```bash
# .env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=TripFinder
REACT_APP_VERSION=1.0.0

# For production
# REACT_APP_API_URL=https://your-production-api.com
```

### 6. **CORS Configuration Update**

Update your FastAPI CORS settings to allow the React app:

```python
# In your app/main.py, update CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development server
    "http://localhost:3001",  # Alternative React port
    "https://your-frontend-domain.com",  # Production frontend
]
```

### 7. **Template Adaptation Steps**

#### 7.1 Replace Template API Calls
1. Find all API calls in the template (usually in services/ or api/ folders)
2. Replace with your backend endpoints
3. Update data structures to match your backend responses

#### 7.2 Update Component Props
```javascript
// Before (template format)
const HotelCard = ({ hotel }) => (
  <div>
    <h3>{hotel.title}</h3>
    <p>{hotel.price}</p>
  </div>
);

// After (your backend format)
const HotelCard = ({ hotel }) => (
  <div>
    <h3>{hotel.name}</h3>
    <p>${hotel.price_per_night}/night</p>
  </div>
);
```

#### 7.3 Authentication Integration
1. Replace template auth with your JWT authentication
2. Update protected routes to check your auth token
3. Add user profile data from your backend

### 8. **Development Workflow**

1. **Start Backend**: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
2. **Start Frontend**: `npm start` (in React project directory)
3. **API Documentation**: Visit `http://localhost:8000/docs` to test endpoints

### 9. **Template-Specific Integrations**

#### 9.1 Search Functionality
```javascript
// Update search components to use your backend
const handleSearch = async (searchData) => {
  try {
    const mappedSearch = mapSearchRequest(searchData);
    const results = await hotelService.searchHotels(mappedSearch);
    setHotels(results.map(mapHotelData));
  } catch (error) {
    console.error('Search failed:', error);
  }
};
```

#### 9.2 Booking Flow
```javascript
// Update booking components
const handleBooking = async (bookingData) => {
  try {
    const mappedBooking = mapBookingRequest(bookingData);
    const booking = await hotelService.bookHotel(mappedBooking);
    // Handle successful booking
    setBookingConfirmation(booking);
  } catch (error) {
    console.error('Booking failed:', error);
  }
};
```

### 10. **Advanced Features**

#### 10.1 Vector Search Integration
```javascript
// Add AI-powered search recommendations
const getSearchSuggestions = async (query) => {
  try {
    const response = await axios.post(
      `${API_CONFIG.BASE_URL}/api/vector/search`,
      { query, limit: 5 }
    );
    return response.data.results;
  } catch (error) {
    console.error('Vector search failed:', error);
    return [];
  }
};
```

#### 10.2 User Preferences
```javascript
// Load user preferences for personalized experience
const loadUserPreferences = async () => {
  try {
    const prefs = await axios.get(`${API_CONFIG.BASE_URL}/api/preferences`);
    return prefs.data;
  } catch (error) {
    return null;
  }
};
```

### 11. **Testing Integration**

```javascript
// Test your API integration
const testAPI = async () => {
  console.log('Testing API integration...');
  
  try {
    // Test health endpoint
    const health = await axios.get(`${API_CONFIG.BASE_URL}/api/health`);
    console.log('✅ Health check:', health.data);
    
    // Test hotel search
    const hotels = await hotelService.searchHotels({
      destination: 'New York',
      check_in: '2024-03-01',
      check_out: '2024-03-03',
      guests: 2,
      rooms: 1
    });
    console.log('✅ Hotel search:', hotels);
    
  } catch (error) {
    console.error('❌ API test failed:', error);
  }
};
```

### 12. **Deployment Considerations**

1. **Environment Variables**: Set production API URLs
2. **Build Process**: Update build scripts for production
3. **HTTPS**: Ensure secure connections in production
4. **CORS**: Update allowed origins for production domain

### 13. **Next Steps**

1. **Install Template**: Extract and set up the TripFinder template
2. **Update API Calls**: Replace template API calls with your backend
3. **Test Integration**: Use the test functions to verify connectivity
4. **Customize UI**: Adapt the template to match your brand
5. **Add Features**: Integrate vector search and user preferences

This integration will give you a professional hotel booking interface backed by your robust FastAPI system with authentication, monitoring, and AI-powered search capabilities. 
