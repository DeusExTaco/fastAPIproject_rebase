// src/auth/Auth0Provider.tsx
import { Auth0Provider, useAuth0 } from '@auth0/auth0-react';
import React, { createContext, useContext, useCallback, useMemo } from 'react';
import { auth0Config } from './auth0-config';

interface AuthContextType {
  isAuthenticated: boolean;
  user: {
    id: string;
    username: string;
    roles: string[];
  } | null;
  token: string | null;
  login: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Auth0Provider {...auth0Config}>
      <AuthProviderContent>{children}</AuthProviderContent>
    </Auth0Provider>
  );
};

const AuthProviderContent: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const {
    isAuthenticated,
    user,
    getAccessTokenSilently,
    loginWithRedirect,
    logout: auth0Logout,
  } = useAuth0();

  const login = useCallback(() => {
    loginWithRedirect();
  }, [loginWithRedirect]);

  const logout = useCallback(() => {
    auth0Logout({
      logoutParams: {
        returnTo: window.location.origin,
      },
    });
  }, [auth0Logout]);

  // Transform Auth0 user to match your app's user structure
  const transformedUser = useMemo(() => {
    if (!user) return null;
    return {
      id: user.sub!,
      username: user.email!,
      // You'll need to configure these roles in Auth0 and include them in the token
      roles: (user['https://your-namespace/roles'] as string[]) || ['USER'],
    };
  }, [user]);

  const [token, setToken] = React.useState<string | null>(null);

  // Fetch token on mount and when authentication state changes
  React.useEffect(() => {
    const getToken = async () => {
      try {
        if (isAuthenticated) {
          const accessToken = await getAccessTokenSilently();
          setToken(accessToken);
        }
      } catch (error) {
        console.error('Error getting token:', error);
        setToken(null);
      }
    };

    void getToken();
  }, [getAccessTokenSilently, isAuthenticated]);

  const value = useMemo(() => ({
    isAuthenticated,
    user: transformedUser,
    token,
    login,
    logout,
  }), [isAuthenticated, transformedUser, token, login, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
