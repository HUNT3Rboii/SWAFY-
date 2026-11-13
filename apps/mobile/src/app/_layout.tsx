import { DarkTheme, DefaultTheme, ThemeProvider } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { useColorScheme } from 'react-native';

import { AuthProvider, useAuth } from '@/auth/auth-context';
import { AnimatedSplashOverlay } from '@/components/animated-icon';
import AppTabs from '@/components/app-tabs';
import { AuthScreen } from '@/components/auth-screen';

SplashScreen.preventAutoHideAsync();

/** Shows the login screen when nobody is logged in, and the tabs otherwise. */
function AppContent() {
  const { status } = useAuth();

  if (status === 'loading') {
    // The splash overlay stays visible while the saved session is read.
    return null;
  }

  return status === 'signedIn' ? <AppTabs /> : <AuthScreen />;
}

export default function RootLayout() {
  const colorScheme = useColorScheme();
  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <AuthProvider>
        <AnimatedSplashOverlay />
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}
