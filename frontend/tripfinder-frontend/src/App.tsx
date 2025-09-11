import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

import authService, { User } from './services/authService';
import hotelService from './services/hotelService';

// Components
import Navbar from './components/Navbar';
import HomePage from './components/HomePage';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import HotelSearchPage from './components/HotelSearchPage';
import HotelDetailsPage from './components/HotelDetailsPage';
import BookingsPage from './components/BookingsPage';
import LoadingSpinner from './components/LoadingSpinner';

// Auth Context
interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'error'>('connecting');

  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Test backend connection
        const isConnected = await hotelService.testConnection();
        setConnectionStatus(isConnected ? 'connected' : 'error');

        // Check if user is already logged in
        if (authService.isAuthenticated()) {
          try {
            const currentUser = await authService.getCurrentUser();
            setUser(currentUser);
          } catch (error) {
            console.error('Failed to get current user:', error);
            authService.logout();
          }
        }
      } catch (error) {
        console.error('Failed to initialize app:', error);
        setConnectionStatus('error');
      } finally {
        setLoading(false);
      }
    };

    initializeApp();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const loggedInUser = await authService.login({ username, password });
      setUser(loggedInUser);
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const authContextValue: AuthContextType = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
        <LoadingSpinner />
      </div>
    );
  }

  if (connectionStatus === 'error') {
    return (
      <div className="container mt-5">
        <div className="alert alert-danger" role="alert">
          <h4 className="alert-heading">Connection Error</h4>
          <p>Unable to connect to the backend server. Please make sure the server is running on http://localhost:8000</p>
          <hr />
          <p className="mb-0">Try refreshing the page or check your backend server.</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={authContextValue}>
      <Router>
        <div className="App">
          <Navbar />
          <main>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route
                path="/search"
                element={
                  <ProtectedRoute>
                    <HotelSearchPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/hotel/:id"
                element={
                  <ProtectedRoute>
                    <HotelDetailsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/bookings"
                element={
                  <ProtectedRoute>
                    <BookingsPage />
                  </ProtectedRoute>
                }
              />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthContext.Provider>
  );
}

export default App;
