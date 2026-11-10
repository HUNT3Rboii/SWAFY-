import { StyleSheet } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';

/**
 * MapLibre React Native only runs on Android and iOS.
 * The web dashboard has its own map (packages/map-web).
 */
export function MapCheck() {
  return (
    <ThemedView style={styles.container}>
      <ThemedText themeColor="textSecondary">The map is only available in the mobile app.</ThemedText>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
