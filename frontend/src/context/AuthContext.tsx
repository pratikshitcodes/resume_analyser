import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api/client';
import type { User } from '../types';

interface AuthContextType {
  user: User | null;
  role: 'candidate' | 'recruiter';
  token: string | null;
  isLoading: boolean;
  login: (email: string, password?: string) => Promise<void>;
  register: (email: string, password?: string, fullName?: string, role?: 'candidate' | 'recruiter') => Promise<void>;
  switchRole: (newRole: 'candidate' | 'recruiter') => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [role, setRole] = useState<'candidate' | 'recruiter'>('candidate');
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('access_token');
      const savedRefreshToken = localStorage.getItem('refresh_token');
      const savedRole = (localStorage.getItem('app_role') as 'candidate' | 'recruiter') || 'candidate';
      setRole(savedRole);

      if (savedToken) {
        try {
          const res = await api.getMe();
          setUser(res.data);
          setRole(res.data.role === 'recruiter' ? 'recruiter' : 'candidate');
        } catch (err) {
          // Access token might be expired, try refreshing using refresh_token
          if (savedRefreshToken) {
            try {
              const refreshRes = await api.refreshToken(savedRefreshToken);
              const { access_token, refresh_token: newRefreshToken, role: userRole } = refreshRes.data;
              localStorage.setItem('access_token', access_token);
              if (newRefreshToken) localStorage.setItem('refresh_token', newRefreshToken);
              setToken(access_token);
              setRole(userRole === 'recruiter' ? 'recruiter' : 'candidate');
              const meRes = await api.getMe();
              setUser(meRes.data);
            } catch (refreshErr) {
              console.error('Session expired. Please sign in again.', refreshErr);
              logout();
            }
          } else {
            logout();
          }
        }
      } else if (savedRefreshToken) {
        // Only refresh token exists, attempt auto-refresh
        try {
          const refreshRes = await api.refreshToken(savedRefreshToken);
          const { access_token, refresh_token: newRefreshToken, role: userRole } = refreshRes.data;
          localStorage.setItem('access_token', access_token);
          if (newRefreshToken) localStorage.setItem('refresh_token', newRefreshToken);
          setToken(access_token);
          setRole(userRole === 'recruiter' ? 'recruiter' : 'candidate');
          const meRes = await api.getMe();
          setUser(meRes.data);
        } catch (e) {
          logout();
        }
      }
      setIsLoading(false);
    };

    const handleAuthLogout = () => {
      logout();
    };
    window.addEventListener('auth:logout', handleAuthLogout);

    initAuth();

    return () => {
      window.removeEventListener('auth:logout', handleAuthLogout);
    };
  }, []);

  const login = async (email: string, password = 'securepassword123') => {
    const res = await api.login({ email, password });
    const { access_token, refresh_token, role: userRole } = res.data;
    localStorage.setItem('access_token', access_token);
    if (refresh_token) {
      localStorage.setItem('refresh_token', refresh_token);
    }
    localStorage.setItem('app_role', userRole);
    setToken(access_token);
    setRole(userRole === 'recruiter' ? 'recruiter' : 'candidate');
    const me = await api.getMe();
    setUser(me.data);
  };

  const register = async (email: string, password = 'securepassword123', fullName = 'User', regRole: 'candidate' | 'recruiter' = 'candidate') => {
    const res = await api.register({
      email,
      password,
      full_name: fullName,
      role: regRole
    });
    const { access_token, refresh_token, role: userRole } = res.data;
    localStorage.setItem('access_token', access_token);
    if (refresh_token) {
      localStorage.setItem('refresh_token', refresh_token);
    }
    localStorage.setItem('app_role', userRole);
    setToken(access_token);
    setRole(userRole === 'recruiter' ? 'recruiter' : 'candidate');
    const me = await api.getMe();
    setUser(me.data);
  };

  const switchRole = (newRole: 'candidate' | 'recruiter') => {
    setRole(newRole);
    localStorage.setItem('app_role', newRole);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('app_role');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, role, token, isLoading, login, register, switchRole, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
