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
      DETAILS: (id: string) => `/hotels/${id}`,
      BOOK: '/hotels/book',
      USER_BOOKINGS: '/hotels/bookings/user',
    },
    // Flights (existing backend)
    TICKETS: {
      LIST: '/tickets',
      CREATE: '/tickets',
      BY_DESTINATION: (dest: string) => `/tickets/destination/${dest}`,
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
    },
    // Health
    HEALTH: '/health'
  }
};

export default API_CONFIG;
