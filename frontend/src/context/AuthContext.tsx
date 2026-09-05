import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, AuthResponseData, UserRole } from '../types';
import { apiRequest } from '../api/client';

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (phone: string, password: string) => Promise<void>;
  register: (name: string, phone: string, password: string, role: UserRole, region?: string, craft_specialty?: string, company_name?: string, requirements?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('sih_auth_token'));
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadUser() {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const userData = await apiRequest<User>('/auth/me');
        setUser(userData);
      } catch (err) {
        console.error('Failed to load user session:', err);
        localStorage.removeItem('sih_auth_token');
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    }
    loadUser();
  }, [token]);

  const login = async (phone: string, password: string) => {
    const data = await apiRequest<AuthResponseData>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ phone, password }),
    });
    localStorage.setItem('sih_auth_token', data.token);
    setToken(data.token);
    setUser({
      user_id: data.user_id,
      name: data.name,
      role: data.role,
      phone,
    });
  };

  const register = async (
    name: string,
    phone: string,
    password: string,
    role: UserRole,
    region?: string,
    craft_specialty?: string,
    company_name?: string,
    requirements?: string
  ) => {
    const data = await apiRequest<AuthResponseData>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        name,
        phone,
        password,
        role,
        region,
        craft_specialty,
        company_name,
        requirements,
      }),
    });
    localStorage.setItem('sih_auth_token', data.token);
    setToken(data.token);
    setUser({
      user_id: data.user_id,
      name: data.name,
      role: data.role,
      phone,
    });
  };

  const logout = () => {
    localStorage.removeItem('sih_auth_token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
