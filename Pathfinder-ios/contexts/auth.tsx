import { createContext, useContext, useState, useEffect } from 'react';
import * as SecureStore from 'expo-secure-store';
import { useRouter, useSegments, useRootNavigationState } from 'expo-router';
import { getAuth, User, Auth } from '@firebase/auth';

type AuthContextType = {
  signIn: (token: string) => Promise<void>;
  signOut: () => Promise<void>;
  isLoading: boolean;
  user: User | null;
  setUser: (user: User | null) => void;
  isLoggedIn: boolean;
};

const AuthContext = createContext<AuthContextType | null>(null);

// This hook can be used to access the user info.
export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return value;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isLoading, setIsLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const rootSegments = useSegments();
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();
  const navigationState = useRootNavigationState();

  useEffect(() => {
    if (!navigationState?.key) return;
    
    const initializeAuth = async () => {
      try {
        const token = await SecureStore.getItemAsync('auth-token');
        setIsLoggedIn(!!token);
      } catch (err) {
        console.error('Failed to get token', err);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, [navigationState?.key]);

  useEffect(() => {
    if (!navigationState?.key) return;
    
    console.log('logged in', isLoggedIn);
    console.log('root segments', rootSegments);
    // Check if we're in the tabs group
    const inTabsGroup = rootSegments[0] === '(tabs)';
    console.log('in tabs group', inTabsGroup);

    if (isLoading) return;

    if (!isLoggedIn && inTabsGroup) {
      console.log('redirecting to login');
      // Redirect to the auth page
      router.replace('/auth');
    } else if (isLoggedIn && !inTabsGroup) {
      console.log('redirecting to tabs');
      router.replace('/(tabs)');
    }
  }, [isLoggedIn, isLoading, rootSegments, navigationState?.key]);

  const signIn = async (token: string) => {
    await SecureStore.setItemAsync('auth-token', token);
    setIsLoggedIn(true);
  };

  const signOut = async () => {
    await SecureStore.deleteItemAsync('auth-token');
    setIsLoggedIn(false);
  };

  return (
    <AuthContext.Provider value={{ signIn, signOut, isLoading, isLoggedIn, user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}