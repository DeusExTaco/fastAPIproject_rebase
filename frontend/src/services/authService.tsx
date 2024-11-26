// authService.ts
interface AuthConfig {
  domain: string;
  clientId: string;
  audience: string;
  backendUrl: string;
}

const config: AuthConfig = {
  domain: import.meta.env.VITE_AUTH0_DOMAIN,
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID,
  audience: import.meta.env.VITE_AUTH0_AUDIENCE,
  backendUrl: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
};

export const auth = {
  login: (): void => {
    // Clear any existing auth state
    sessionStorage.clear();
    localStorage.clear();

    const params = new URLSearchParams({
      response_type: 'code',
      client_id: config.clientId,
      redirect_uri: `${config.backendUrl}/api/auth/callback`,
      scope: 'openid profile email offline_access',
      audience: config.audience,
    });

    window.location.href = `https://${config.domain}/authorize?${params}`;
  },

  logout: async (): Promise<void> => {
    try {
      sessionStorage.setItem('isLoggingOut', 'true');
      localStorage.clear();

      // Clear cookies
      document.cookie.split(';').forEach(cookie => {
        const [name] = cookie.split('=');
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/api`;
      });

      await fetch(`${config.backendUrl}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });

      const returnTo = encodeURIComponent(window.location.origin);
      window.location.replace(
        `https://${config.domain}/v2/logout?client_id=${config.clientId}&returnTo=${returnTo}`
      );
    } catch (error) {
      console.error('Logout error:', error);
      window.location.href = '/';
    }
  },

  getUser: async () => {
    if (sessionStorage.getItem('isLoggingOut')) {
      return null;
    }

    try {
      const response = await fetch(`${config.backendUrl}/api/auth/me`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
        }
      });

      if (!response.ok) {
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching user:', error);
      return null;
    }
  }
};

export type { AuthConfig };