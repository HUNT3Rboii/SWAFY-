import { ThemedText } from '@/components/themed-text';
import { PlaceholderScreen } from '@/components/placeholder-screen';
import { API_BASE_URL } from '@/config/env';

export default function MapScreen() {
  return (
    <PlaceholderScreen
      title="Map"
      description="Reported issues will appear here as pins.">
      {__DEV__ && (
        <ThemedText type="code" themeColor="textSecondary">
          API: {API_BASE_URL}
        </ThemedText>
      )}
    </PlaceholderScreen>
  );
}
