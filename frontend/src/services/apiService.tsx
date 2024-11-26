// src/services/api.ts
import React, {createContext, useCallback, useMemo} from 'react';
import {useAuth} from '../contexts/AuthContext';

interface APIContextType {
  get: (endpoint: string) => Promise<any>;
  post: (endpoint: string, data?: any) => Promise<any>;
  put: (endpoint: string, data?: any) => Promise<any>;
  delete: (endpoint: string) => Promise<any>;
}

const APIContext = createContext<APIContextType | null>(null);

const BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const APIServiceProvider = ({ children }: { children: React.ReactNode }) => {
  const { logout } = useAuth();

  const handleResponse = useCallback(async (response: Response) => {
    if (response.status === 401) {
      console.error('Authentication error - logging out');
      await logout();
      throw new Error('Authentication error');
    }

    if (!response.ok) {
      let errorMessage = 'API request failed';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // If parsing JSON fails, use the status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }
    // Check if response is empty
    const contentType = response.headers.get('content-type');
    if (contentType?.includes?.('application/json')) {
      return response.json();
    }
    return null;
  }, [logout]);

  const fetchWithCredentials = useCallback(async (endpoint: string, options: RequestInit) => {
    const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;
    const defaultOptions: RequestInit = {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    };

    try {
      const response = await fetch(url, {
        ...defaultOptions,
        ...options,
        headers: {
          ...defaultOptions.headers,
          ...options.headers,
        },
      });
      return handleResponse(response);
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }, [handleResponse]);

  const get = useCallback((endpoint: string) => {
    return fetchWithCredentials(endpoint, { method: 'GET' });
  }, [fetchWithCredentials]);

  const post = useCallback((endpoint: string, data?: any) => {
    return fetchWithCredentials(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }, [fetchWithCredentials]);

  const put = useCallback((endpoint: string, data?: any) => {
    return fetchWithCredentials(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }, [fetchWithCredentials]);

  const delete_ = useCallback((endpoint: string) => {
    return fetchWithCredentials(endpoint, { method: 'DELETE' });
  }, [fetchWithCredentials]);

  const value = useMemo(() => ({
    get,
    post,
    put,
    delete: delete_,
  }), [get, post, put, delete_]);

  return (
    <APIContext.Provider value={value}>
      {children}
    </APIContext.Provider>
  );
};