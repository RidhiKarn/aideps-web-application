import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  name: string;
  email: string;
  organization?: string;
  role: 'admin' | 'analyst' | 'viewer';
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: async (email: string, password: string) => {
        // Simulate API call
        // In production, this would call your auth endpoint
        if (email === 'demo@mospi.gov.in' && password === 'demo123') {
          const mockUser: User = {
            id: '1',
            name: 'Data Analyst',
            email: email,
            organization: 'MoSPI',
            role: 'analyst',
          };
          
          const mockToken = 'mock-jwt-token-' + Date.now();
          
          set({
            user: mockUser,
            token: mockToken,
            isAuthenticated: true,
          });
          
          // Also store in localStorage for persistence
          localStorage.setItem('auth-token', mockToken);
        } else {
          throw new Error('Invalid credentials');
        }
      },
      
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
        localStorage.removeItem('auth-token');
        localStorage.removeItem('auth-storage'); // Clear zustand persistence
      },
      
      setUser: (user: User) => {
        set({ user });
      },
    }),
    {
      name: 'auth-storage', // unique name for localStorage key
      partialize: (state) => ({ 
        user: state.user, 
        token: state.token, 
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
);