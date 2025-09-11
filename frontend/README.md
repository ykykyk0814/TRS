# TripFinder Frontend

A React TypeScript frontend for the TripFinder travel recommendation system, integrated with the FastAPI backend.

## 🚀 Features

- **Modern React Frontend**: Built with React 18 and TypeScript
- **Bootstrap UI**: Professional hotel booking interface using React Bootstrap
- **JWT Authentication**: Secure login and registration with FastAPI-Users
- **Hotel Search**: AI-powered hotel search and booking system
- **Real-time API Integration**: Connected to FastAPI backend with monitoring
- **Responsive Design**: Mobile-friendly interface

## 🛠️ Setup & Installation

### Prerequisites
- Node.js 16+ and npm
- FastAPI backend running on http://localhost:8000

### Installation

```bash
# Navigate to frontend directory
cd frontend/tripfinder-frontend

# Install dependencies
npm install

# Start development server
npm start
```

The app will open at http://localhost:3000

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=TripFinder
REACT_APP_VERSION=1.0.0
```

### API Configuration

The frontend is configured to connect to the FastAPI backend with the following endpoints:

- **Authentication**: `/api/auth/`
- **Hotels**: `/api/hotels/`
- **Health Check**: `/api/health`
- **Vector Search**: `/api/vector/`

## 📱 Application Structure

```
src/
├── components/          # React components
│   ├── HomePage.tsx     # Landing page
│   ├── LoginPage.tsx    # User authentication
│   ├── HotelSearchPage.tsx  # Hotel search interface
│   └── ...
├── services/           # API service layer
│   ├── authService.ts  # Authentication API calls
│   ├── hotelService.ts # Hotel API calls
│   └── ...
├── config/
│   └── api.ts         # API configuration
└── App.tsx            # Main application component
```

## 🔐 Authentication Flow

1. **Registration**: Create new account via `/register`
2. **Login**: Authenticate with email/password
3. **JWT Token**: Stored in localStorage for API calls
4. **Protected Routes**: Hotel search requires authentication

### Demo Credentials

For testing purposes:
- Email: `test@example.com`
- Password: `testpassword123`

## 🏨 Hotel Search Features

- **Search Form**: Destination, dates, guests, rooms
- **Results Display**: Hotel cards with images, ratings, pricing
- **Filter Options**: Price range, amenities
- **Responsive Design**: Works on mobile and desktop

## 🧪 Testing

### Manual Testing

1. Start both backend and frontend servers
2. Open http://localhost:3000
3. Register a new account or use demo credentials
4. Test hotel search functionality
5. Verify authentication flow

### Integration Test

Run the integration test script:

```bash
# Test backend connectivity
node ../test-integration.js
```

## 🔧 API Integration

### Service Layer

The frontend uses a service layer pattern:

```typescript
// Example: Hotel search
import hotelService from './services/hotelService';

const results = await hotelService.searchHotels({
  destination: 'New York',
  check_in: '2024-03-01',
  check_out: '2024-03-03',
  guests: 2,
  rooms: 1
});
```

### Error Handling

- Network errors are caught and displayed to users
- Authentication errors redirect to login page
- Validation errors show inline feedback

## 📊 Monitoring Integration

The frontend includes connection status monitoring:

- Backend health check on app startup
- Connection error handling
- Real-time status indicators

## 🚢 Deployment

### Development

```bash
npm start  # Starts dev server on port 3000
```

### Production

```bash
npm run build  # Creates optimized production build
npm run build && serve -s build  # Serve production build
```

### Environment Configuration

Update `.env` for production:

```bash
REACT_APP_API_URL=https://your-api-domain.com
```

## 🤝 Backend Integration

This frontend is designed to work with the FastAPI backend that includes:

- JWT authentication with FastAPI-Users
- Hotel search and booking endpoints
- Vector search for AI-powered recommendations
- Prometheus monitoring
- PostgreSQL database
- Comprehensive API documentation

## 📞 Support

For issues related to:
- **Frontend bugs**: Check browser console for errors
- **API connectivity**: Verify backend is running on port 8000
- **Authentication**: Check JWT token in browser localStorage
- **CORS issues**: Verify ALLOWED_ORIGINS in backend configuration

## 🎯 Next Steps

1. **Complete Hotel Details Page**: Full hotel information and booking
2. **Booking Management**: View and manage reservations
3. **User Profile**: Account settings and preferences
4. **Vector Search UI**: AI-powered search suggestions
5. **Mobile App**: React Native version

The frontend provides a solid foundation for a modern travel booking platform with professional UI/UX and robust backend integration. 
