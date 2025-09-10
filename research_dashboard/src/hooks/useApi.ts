import { useState, useCallback } from 'react';
import axios, { AxiosResponse, AxiosError } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

interface ApiResponse<T = any> {
  data: T;
  success: boolean;
  message?: string;
}

interface ApiError {
  message: string;
  status?: number;
}

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const handleRequest = useCallback(async <T>(
    requestPromise: Promise<AxiosResponse<T>>
  ): Promise<ApiResponse<T>> => {
    setLoading(true);
    setError(null);

    try {
      const response = await requestPromise;
      return {
        data: response.data,
        success: true
      };
    } catch (err) {
      const apiError: ApiError = {
        message: 'An error occurred',
        status: 500
      };

      if (axios.isAxiosError(err)) {
        const axiosError = err as AxiosError<any>;
        apiError.message = axiosError.response?.data?.detail || axiosError.message || 'Network error';
        apiError.status = axiosError.response?.status || 500;
      }

      setError(apiError);
      throw apiError;
    } finally {
      setLoading(false);
    }
  }, []);

  const get = useCallback(async <T>(url: string): Promise<ApiResponse<T>> => {
    const token = localStorage.getItem('auth_token');
    return handleRequest(
      axios.get(`${API_BASE_URL}${url}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      })
    );
  }, [handleRequest]);

  const post = useCallback(async <T>(url: string, data?: any): Promise<ApiResponse<T>> => {
    const token = localStorage.getItem('auth_token');
    return handleRequest(
      axios.post(`${API_BASE_URL}${url}`, data, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      })
    );
  }, [handleRequest]);

  const put = useCallback(async <T>(url: string, data?: any): Promise<ApiResponse<T>> => {
    const token = localStorage.getItem('auth_token');
    return handleRequest(
      axios.put(`${API_BASE_URL}${url}`, data, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      })
    );
  }, [handleRequest]);

  const del = useCallback(async <T>(url: string): Promise<ApiResponse<T>> => {
    const token = localStorage.getItem('auth_token');
    return handleRequest(
      axios.delete(`${API_BASE_URL}${url}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      })
    );
  }, [handleRequest]);

  return {
    get,
    post,
    put,
    delete: del,
    loading,
    error,
    clearError: () => setError(null)
  };
};


// import { useState, useCallback } from 'react';
// import axios, { AxiosResponse, AxiosError } from 'axios';

// const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// interface ApiResponse<T = any> {
//   data: T;
//   success: boolean;
//   message?: string;
// }

// interface ApiError {
//   message: string;
//   status?: number;
// }

// export const useApi = () => {
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState<ApiError | null>(null);

//   const handleRequest = useCallback(async <T>(
//     requestPromise: Promise<AxiosResponse<T>>
//   ): Promise<ApiResponse<T>> => {
//     setLoading(true);
//     setError(null);

//     try {
//       const response = await requestPromise;
//       return {
//         data: response.data,
//         success: true
//       };
//     } catch (err) {
//       const apiError: ApiError = {
//         message: 'An error occurred',
//         status: 500
//       };

//       if (axios.isAxiosError(err)) {
//         const axiosError = err as AxiosError<any>;
//         apiError.message = axiosError.response?.data?.detail || axiosError.message || 'Network error';
//         apiError.status = axiosError.response?.status || 500;
//       }

//       setError(apiError);
//       throw apiError;
//     } finally {
//       setLoading(false);
//     }
//   }, []);

//   const get = useCallback(async <T>(url: string): Promise<ApiResponse<T>> => {
//     const token = localStorage.getItem('auth_token');
//     return handleRequest(
//       axios.get(`${API_BASE_URL}${url}`, {
//         headers: token ? { Authorization: `Bearer ${token}` } : {}
//       })
//     );
//   }, [handleRequest]);

//   const post = useCallback(async <T>(url: string, data?: any): Promise<ApiResponse<T>> => {
//     const token = localStorage.getItem('auth_token');
//     return handleRequest(
//       axios.post(`${API_BASE_URL}${url}`, data, {
//         headers: token ? { Authorization: `Bearer ${token}` } : {}
//       })
//     );
//   }, [handleRequest]);
//   const put = useCallback(async <T>(url: string, data?: any): Promise<ApiResponse<T>> => {
//    const token = localStorage.getItem('auth_token');
//    return handleRequest(
//      axios.put(`${API_BASE_URL}${url}`, data, {
//        headers: token ? { Authorization: `Bearer ${token}` } : {}
//      })
//    );
//  }, [handleRequest]);

//  const del = useCallback(async <T>(url: string): Promise<ApiResponse<T>> => {
//    const token = localStorage.getItem('auth_token');
//    return handleRequest(
//      axios.delete(`${API_BASE_URL}${url}`, {
//        headers: token ? { Authorization: `Bearer ${token}` } : {}
//      })
//    );
//  }, [handleRequest]);

//  return {
//    get,
//    post,
//    put,
//    delete: del,
//    loading,
//    error,
//    clearError: () => setError(null)
//  };
// };