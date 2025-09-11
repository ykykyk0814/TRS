import axios from 'axios';
import API_CONFIG from '../config/api';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
}

export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
}

class AuthService {
  private baseURL: string;
  private token: string | null;

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

    // Setup response interceptor for handling auth errors
    axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async login(credentials: LoginCredentials): Promise<User> {
    try {
      // Use form data for login as required by FastAPI-Users
      const formData = new FormData();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);

      const response = await axios.post(
        `${this.baseURL}${API_CONFIG.ENDPOINTS.AUTH.LOGIN}`,
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      this.token = response.data.access_token;
      if (this.token) {
        localStorage.setItem('auth_token', this.token);
      }

      // Get user info after successful login
      const userResponse = await this.getCurrentUser();
      return userResponse;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  async register(userData: RegisterData): Promise<User> {
    try {
      const response = await axios.post(
        `${this.baseURL}${API_CONFIG.ENDPOINTS.AUTH.REGISTER}`,
        userData
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      const response = await axios.get(
        `${this.baseURL}${API_CONFIG.ENDPOINTS.AUTH.ME}`
      );
      return response.data;
    } catch (error) {
      throw new Error('Failed to get user info');
    }
  }

  logout(): void {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  getToken(): string | null {
    return this.token;
  }
}

export default new AuthService();
