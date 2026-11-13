import { useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ApiError } from '@/api/api-error';
import { useAuth } from '@/auth/auth-context';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { MaxContentWidth, Spacing } from '@/constants/theme';
import { USE_MOCK_API } from '@/config/env';
import { useTheme } from '@/hooks/use-theme';

type Mode = 'login' | 'register';

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/** Checks the form before calling the API. Rules come from docs/contracts/openapi.yaml. */
function validate(mode: Mode, displayName: string, email: string, password: string): string | null {
  if (mode === 'register') {
    if (displayName.trim().length === 0) return 'Please enter your name.';
    if (displayName.trim().length > 120) return 'Your name must be at most 120 characters.';
  }
  if (!EMAIL_PATTERN.test(email.trim())) return 'Please enter a valid email address.';
  if (mode === 'register' && password.length < 8) return 'Your password must have at least 8 characters.';
  if (password.length === 0) return 'Please enter your password.';
  if (password.length > 128) return 'Your password must be at most 128 characters.';
  return null;
}

/** Turns an API error into a sentence the citizen understands. */
function errorMessage(error: unknown, mode: Mode): string {
  if (error instanceof ApiError) {
    if (error.status === 0) return 'Cannot reach the server. Check your internet connection and try again.';
    if (error.status === 401) return 'Wrong email or password.';
    if (error.status === 409) return 'An account with this email already exists. Try logging in.';
    if (error.status === 422) return 'Some fields are not valid. Please check them.';
  }
  return mode === 'login'
    ? 'Login failed. Please try again.'
    : 'Registration failed. Please try again.';
}

/** Login and register screen, shown when nobody is logged in. */
export function AuthScreen() {
  const { signIn, signUp } = useAuth();
  const theme = useTheme();

  const [mode, setMode] = useState<Mode>('login');
  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const isRegister = mode === 'register';
  const inputStyle = [
    styles.input,
    { backgroundColor: theme.backgroundElement, color: theme.text, borderColor: theme.backgroundSelected },
  ];

  async function handleSubmit() {
    const problem = validate(mode, displayName, email, password);
    if (problem) {
      setError(problem);
      return;
    }

    setError(null);
    setSubmitting(true);
    try {
      if (isRegister) {
        await signUp({ display_name: displayName.trim(), email: email.trim(), password });
      } else {
        await signIn({ email: email.trim(), password });
      }
      // On success, the app switches to the tabs by itself (see src/app/_layout.tsx).
    } catch (e) {
      setError(errorMessage(e, mode));
      setSubmitting(false);
    }
  }

  function switchMode() {
    setMode(isRegister ? 'login' : 'register');
    setError(null);
  }

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <KeyboardAvoidingView
          style={styles.flex}
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
          <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
            <ThemedText type="subtitle">SWAFY</ThemedText>
            <ThemedText themeColor="textSecondary">
              {isRegister ? 'Create an account to report issues in your city.' : 'Log in to report issues in your city.'}
            </ThemedText>

            <View style={styles.form}>
              {isRegister && (
                <TextInput
                  style={inputStyle}
                  placeholder="Your name"
                  placeholderTextColor={theme.textSecondary}
                  value={displayName}
                  onChangeText={setDisplayName}
                  autoComplete="name"
                  textContentType="name"
                  maxLength={120}
                  editable={!submitting}
                />
              )}
              <TextInput
                style={inputStyle}
                placeholder="Email"
                placeholderTextColor={theme.textSecondary}
                value={email}
                onChangeText={setEmail}
                autoCapitalize="none"
                autoCorrect={false}
                autoComplete="email"
                keyboardType="email-address"
                textContentType="emailAddress"
                maxLength={254}
                editable={!submitting}
              />
              <TextInput
                style={inputStyle}
                placeholder={isRegister ? 'Password (at least 8 characters)' : 'Password'}
                placeholderTextColor={theme.textSecondary}
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                autoCapitalize="none"
                autoComplete={isRegister ? 'new-password' : 'current-password'}
                textContentType={isRegister ? 'newPassword' : 'password'}
                maxLength={128}
                editable={!submitting}
                onSubmitEditing={handleSubmit}
              />

              {error && (
                <ThemedText type="small" style={styles.error}>
                  {error}
                </ThemedText>
              )}

              <Pressable
                onPress={handleSubmit}
                disabled={submitting}
                style={({ pressed }) => [styles.button, (pressed || submitting) && styles.buttonPressed]}>
                {submitting ? (
                  <ActivityIndicator color="#FFFFFF" />
                ) : (
                  <ThemedText style={styles.buttonText}>{isRegister ? 'Create account' : 'Log in'}</ThemedText>
                )}
              </Pressable>

              <Pressable onPress={switchMode} disabled={submitting} hitSlop={8}>
                <ThemedText type="linkPrimary" style={styles.center}>
                  {isRegister ? 'Already have an account? Log in' : 'No account yet? Create one'}
                </ThemedText>
              </Pressable>
            </View>

            {__DEV__ && USE_MOCK_API && (
              <ThemedText type="small" themeColor="textSecondary" style={styles.center}>
                Demo mode: no real server is used.
              </ThemedText>
            )}
          </ScrollView>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  flex: {
    flex: 1,
  },
  content: {
    flexGrow: 1,
    justifyContent: 'center',
    gap: Spacing.three,
    padding: Spacing.four,
    width: '100%',
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
  },
  form: {
    gap: Spacing.three,
    marginTop: Spacing.three,
  },
  input: {
    borderWidth: 1,
    borderRadius: Spacing.two,
    paddingHorizontal: Spacing.three,
    paddingVertical: Spacing.three,
    fontSize: 16,
  },
  error: {
    color: '#E5484D',
  },
  button: {
    backgroundColor: '#208AEF',
    borderRadius: Spacing.two,
    paddingVertical: Spacing.three,
    alignItems: 'center',
  },
  buttonPressed: {
    opacity: 0.7,
  },
  buttonText: {
    color: '#FFFFFF',
    fontWeight: 700,
  },
  center: {
    textAlign: 'center',
  },
});
