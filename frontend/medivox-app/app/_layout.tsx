import {
  DarkTheme,
  DefaultTheme,
  ThemeProvider,
} from "@react-navigation/native";
import { useFonts } from "expo-font";
import { Stack, Redirect, useRouter } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { StatusBar } from "expo-status-bar";
import { useEffect } from "react";
import "react-native-reanimated";

import { useColorScheme } from "@/hooks/useColorScheme";

// Prevent the splash screen from auto-hiding before asset loading is complete.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const router = useRouter();
  const colorScheme = useColorScheme();
  const [loaded] = useFonts({
    SpaceMono: require("../assets/fonts/SpaceMono-Regular.ttf"),
  });

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
      router.replace("/LoginScreen");
    }
  }, [loaded]);

  if (!loaded) {
    return null;
  }

  return (
    <ThemeProvider value={colorScheme === "dark" ? DarkTheme : DefaultTheme}>
      <Stack>
        <Stack.Screen name="(auth)" options={{ headerShown: false }} />
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="+not-found" />
      </Stack>
      <StatusBar style="auto" />
    </ThemeProvider>
  );
}

// import { Redirect, Slot, Stack, useRouter } from "expo-router";
// import { ThemeProvider } from "@react-navigation/native";
// import { DarkTheme, DefaultTheme } from "@react-navigation/native";
// import { StatusBar } from "expo-status-bar";
// import { useColorScheme } from "react-native";
// import { useEffect, useState } from "react";

// export default function RootLayout() {
//   const router = useRouter();
//   const [isReady, setIsReady] = useState(false);
//   const isLoggedIn = false; // Replace with real logic

//   useEffect(() => {
//     // Delay redirect until after mount
//     if (!isLoggedIn) {
//       router.replace("/LoginScreen");
//     }
//     setIsReady(true);
//   }, []);

//   if (!isReady) {
//     // Optional: show splash or loading while redirecting
//     return null;
//   }

//   return <Slot />;
// }

// //   return (
// //     <ThemeProvider value={colorScheme === "dark" ? DarkTheme : DefaultTheme}>
// //       <Stack
// //         screenOptions={{
// //           headerShown: false,
// //         }}
// //       />
// //       <StatusBar style="auto" />
// //     </ThemeProvider>
// //   );
// // }
