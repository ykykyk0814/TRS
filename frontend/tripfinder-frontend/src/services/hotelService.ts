import axios from 'axios';
import API_CONFIG from '../config/api';

export interface HotelSearchParams {
  destination: string;
  check_in: string;
  check_out: string;
  guests: number;
  rooms: number;
  price_min?: number;
  price_max?: number;
  amenities?: string[];
}

export interface Hotel {
  id: string;
  name: string;
  description: string;
  location: string;
  price_per_night: number;
  rating: number;
  image_url: string;
  amenities: string[];
  available_rooms: number;
}

export interface BookingData {
  hotel_id: string;
  check_in: string;
  check_out: string;
  guests: number;
  rooms: number;
  special_requests?: string;
}

export interface Booking {
  booking_id: string;
  hotel_name: string;
  check_in: string;
  check_out: string;
  total_price: number;
  status: string;
  created_at: string;
}

class HotelService {
  private baseURL: string;

  constructor() {
    this.baseURL = `${API_CONFIG.BASE_URL}${API_CONFIG.API_PREFIX}`;
  }

  async searchHotels(searchParams: HotelSearchParams): Promise<Hotel[]> {
    try {
      const response = await axios.post(
        `${this.baseURL}${API_CONFIG.ENDPOINTS.HOTELS.SEARCH}`,
        searchParams
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Hotel search failed');
    }
  }

  async getHotelDetails(hotelId: string): Promise<Hotel> {
    try {
      const response = await axios.get(
        `${this.baseURL}${API_CONFIG.ENDPOINTS.HOTELS.DETAILS(hotelId)}`
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to get hotel details');
    }
  }

  async bookHotel(bookingData: BookingData): Promise<Booking> {
    try {
      const response = await axios.post(
        `${this.baseURL}${API_CONFIG.ENDPOINTS.HOTELS.BOOK}`,
        bookingData
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Booking failed');
    }
  }

  async getUserBookings(): Promise<Booking[]> {
    try {
      const response = await axios.get(
        `${this.baseURL}${API_CONFIG.ENDPOINTS.HOTELS.USER_BOOKINGS}`
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to get bookings');
    }
  }

  async testConnection(): Promise<boolean> {
    try {
      const response = await axios.get(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.HEALTH}`);
      return response.data.status === 'healthy';
    } catch (error) {
      return false;
    }
  }
}

export default new HotelService();
