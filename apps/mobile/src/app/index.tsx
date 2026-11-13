import { StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { MapCheck } from '@/components/map-check';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing } from '@/constants/theme';
import { API_BASE_URL } from '@/config/env';

export default function MapScreen() {
  return (
    <View style={styles.container}>
      <MapCheck />

      {__DEV__ && (
        <SafeAreaView edges={['top']} style={styles.overlay} pointerEvents="none">
          <ThemedView type="backgroundElement" style={styles.badge}>
            <ThemedText type="code" themeColor="textSecondary">
              API: {API_BASE_URL}
            </ThemedText>
          </ThemedView>
        </SafeAreaView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  badge: {
    marginTop: Spacing.two,
    paddingHorizontal: Spacing.three,
    paddingVertical: Spacing.one,
    borderRadius: Spacing.three,
  },
});
