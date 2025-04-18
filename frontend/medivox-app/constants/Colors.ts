/**
 * Below are the colors that are used in the app. The colors are defined in the light and dark mode.
 * There are many other ways to style your app. For example, [Nativewind](https://www.nativewind.dev/), [Tamagui](https://tamagui.dev/), [unistyles](https://reactnativeunistyles.vercel.app), etc.
 */

const tintColorLight = "#0a7ea4";
const tintColorDark = "#fff";

const white = "#fff";
const black = "#000";
const dark = "#626262";
const blue = "#1F41BB";
const green = "#3CB371";
const gray = "#ECECEC";
const lightBlue = "#f1f4ff";

export const Colors = {
  light: {
    // text: "#11181C",
    // background: "#fff",
    tint: tintColorLight,
    icon: "#687076",
    tabIconDefault: "#687076",
    tabIconSelected: tintColorLight,

    darkText: dark,
    text: black,
    background: white,
    primary: green,
    onPrimary: white,
    active: blue,
    borderWithOpacity: "#1f41bb",
    lightPrimary: lightBlue,
    gray: gray,
  },
  dark: {
    // text: "#ECEDEE",
    // background: "#151718",
    tint: tintColorDark,
    icon: "#9BA1A6",
    tabIconDefault: "#9BA1A6",
    tabIconSelected: tintColorDark,
    darkText: dark,
    text: black,
    background: white,
    primary: green,
    onPrimary: white,
    active: blue,
    borderWithOpacity: "#1f41bb",
    lightPrimary: lightBlue,
    gray: gray,
  },
};

// export default {
//   darkText: dark,
//   text: black,
//   background: white,
//   primary: blue,
//   onPrimary: white,
//   active: blue,
//   borderWithOpacity: "#1f41bb",
//   lightPrimary: lightBlue,
//   gray: gray,
// };
