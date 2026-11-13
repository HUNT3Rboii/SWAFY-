import { useState } from 'react';
import { Pressable, StyleSheet } from 'react-native';

import { useAuth } from '@/auth/auth-context';
import { PlaceholderScreen } from '@/components/placeholder-screen';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing } from '@/constants/theme';

export default function MyReportsScreen() {
  const { user, signOut } = useAuth();
  const [signingOut, setSigningOut] = useState(false);

  async function handleSignOut() {
    setSigningOut(true);
    try {
      await signOut();
    } finally {
      setSigningOut(false);
    }
  }

  return (
    <PlaceholderScreen
      title="My reports"
      description="The reports you sent and their status will appear here.">
      <ThemedView type="backgroundElement" style={styles.account}>
        <ThemedText type="smallBold">{user?.display_name}</ThemedText>
        <ThemedText type="small" themeColor="textSecondary">
          {user?.email}
        </ThemedText>
        <Pressable onPress={handleSignOut} disabled={signingOut} hitSlop={8}>
          <ThemedText type="linkPrimary">{signingOut ? 'Logging out…' : 'Log out'}</ThemedText>
        </Pressable>
      </ThemedView>
    </PlaceholderScreen>
  );
}

const styles = StyleSheet.create({
  account: {
    alignItems: 'center',
    gap: Spacing.one,
    padding: Spacing.three,
    borderRadius: Spacing.three,
    marginTop: Spacing.four,
  },
});
