// src/App.tsx
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import AppRoutes from './AppRoutes';
import { APIServiceProvider } from './services/apiService.tsx';

function App() {
  return (
    <Router>
      <AuthProvider>
        <APIServiceProvider>
          <AppRoutes />
        </APIServiceProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;