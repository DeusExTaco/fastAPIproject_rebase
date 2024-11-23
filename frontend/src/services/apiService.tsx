// src/services/api.ts
import { useAuth } from '../auth/useAuth';

const API_BASE_URL = 'http://localhost:8000/api';

export const useApi = () => {
  const { token } = useAuth();

  const fetchWithAuth = async (
    endpoint: string,
    options: RequestInit = {}
  ) => {
    if (!token) {
      throw new Error('No access token available');
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  };

  return { fetchWithAuth };
};

// Example usage in a component:
const UsersList = () => {
  const { fetchWithAuth } = useApi();
  const [users, setUsers] = useState([]);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await fetchWithAuth('/users');
        setUsers(data);
      } catch (error) {
        console.error('Failed to fetch users:', error);
      }
    };

    fetchUsers();
  }, [fetchWithAuth]);

  return // ... your JSX
};