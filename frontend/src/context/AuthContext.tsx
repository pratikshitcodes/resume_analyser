import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api/client';
import type { User } from '../types';

interface AuthContextType {
  user: User | null;
  role: 'candidate' | 'recruiter';
  token: string | null;
  isLoading: boolean;
  login: (email: string, password?: string, defaultRole?: 'candidate' | 'recruiter') => Promise<void>;
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
      const savedRole = (localStorage.getItem('app_role') as 'candidate' | 'recruiter') || 'candidate';
      setRole(savedRole);

      if (savedToken) {
        try {
          const res = await api.getMe();
          setUser(res.data);
          setRole(res.data.role === 'recruiter' ? 'recruiter' : 'candidate');
        } catch (err) {
          console.error('Session expired or invalid token', err);
          localStorage.removeItem('access_token');
          setToken(null);
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email: string, password = 'securepassword123', defaultRole: 'candidate' | 'recruiter' = 'candidate') => {
    try {
      const res = await api.login({ email, password });
      const { access_token, role: userRole } = res.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('app_role', userRole);
      setToken(access_token);
      setRole(userRole === 'recruiter' ? 'recruiter' : 'candidate');
      const me = await api.getMe();
      setUser(me.data);
    } catch (err) {
      try {
        const regRes = await api.register({
          email,
          password,
          full_name: email.split('@')[0].toUpperCase(),
          role: defaultRole
        });
        const { access_token, role: userRole } = regRes.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('app_role', userRole);
        setToken(access_token);
        setRole(userRole === 'recruiter' ? 'recruiter' : 'candidate');
        const me = await api.getMe();
        setUser(me.data);
      } catch (regErr) {
        throw regErr;
      }
    }
  };

  const register = async (email: string, password = 'securepassword123', fullName = 'User', regRole: 'candidate' | 'recruiter' = 'candidate') => {
    const res = await api.register({
      email,
      password,
      full_name: fullName,
      role: regRole
    });
    const { access_token, role: userRole } = res.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('app_role', userRole);
    setToken(access_token);
    setRole(userRole === 'recruiter' ? 'recruiter' : 'candidate');
    const me = await api.getMe();
    setUser(me.data);
  };

  const switchRole = async (newRole: 'candidate' | 'recruiter') => {
    setRole(newRole);
    localStorage.setItem('app_role', newRole);
    const demoEmail = newRole === 'recruiter' ? 'recruiter_demo@company.com' : 'candidate_demo@example.com';
    try {
      await login(demoEmail, 'securepassword123', newRole);
    } catch (e) {
      console.warn('Switched role view', e);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
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
