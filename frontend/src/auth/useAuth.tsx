// src/auth/useAuth.tsx
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an Auth0Provider');
  }
  return context;
};