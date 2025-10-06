import axios, { AxiosResponse } from 'axios';
import { ApiResponse, TimetableData, ConfigData, StatusData } from '../types/api';

// Dynamic API base URL - uses the same host as the frontend but port 5000
const getApiBaseUrl = () => {
  const hostname = window.location.hostname;
  
  // Always use the same hostname but with port 5000 for the API
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:5000';
  }
  
  // For network access (like 192.168.x.x), use the same IP with port 5000
  return `http://${hostname}:5000`;
};

const API_BASE_URL = process.env.REACT_APP_API_URL || getApiBaseUrl();

console.log('API Base URL:', API_BASE_URL); // Debug log

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
});

export const apiService = {
  // Health check
  healthCheck: async (): Promise<ApiResponse> => {
    const response: AxiosResponse<ApiResponse> = await api.get('/api/health');
    return response.data;
  },

  // Get configuration
  getConfig: async (): Promise<ApiResponse<ConfigData>> => {
    const response: AxiosResponse<ConfigData> = await api.get('/api/config');
    return {
      success: true,
      data: response.data,
      timestamp: new Date().toISOString()
    };
  },

  // Update semesters
  updateSemesters: async (semesters: string[]): Promise<ApiResponse> => {
    const response: AxiosResponse<ApiResponse> = await api.post('/api/config/semesters', {
      semesters
    });
    return response.data;
  },

  // Run scraper
  runScraper: async (): Promise<ApiResponse<TimetableData>> => {
    const response: AxiosResponse<ApiResponse<TimetableData>> = await api.post('/api/scrape');
    return response.data;
  },

  // Get latest timetable
  getLatestTimetable: async (): Promise<ApiResponse<TimetableData>> => {
    const response: AxiosResponse<ApiResponse<TimetableData>> = await api.get('/api/timetable');
    return response.data;
  },

  // Get status
  getStatus: async (): Promise<ApiResponse<StatusData>> => {
    const response: AxiosResponse<ApiResponse<StatusData>> = await api.get('/api/status');
    return response.data;
  },
};

export default apiService;