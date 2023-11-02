<script lang="ts">
  import { useSvelteUITheme, key as svelteUiThemeKey, SvelteUIProvider } from "@svelteuidev/core";
  import { setContext } from "svelte";

  // TODO: move to a normal fucking UI kit that can be properly themed and styled
  // warning: dumpster fire

  // first we set some internal context insite svelteui because it refuses to work otherwise
  const DEFAULT_THEME = useSvelteUITheme();
  setContext(svelteUiThemeKey, {
    theme: DEFAULT_THEME,
    styles: {},
    defaultProps: {},
  });

  interface HSLColor {
    hue: number;
    sat: number;
    lum: number;
  }
  interface StitchesColorDef {
    token: string;
    value: string;
    scale: string;
    prefix: string;
  }
  const SVELTEUI_PREFIX = "svelteui";

  function integerLerp(v1: number, v2: number, t: number) {
    return Math.round(v1 + t * (v2 - v1));
  }

  function generateColors(name: string, from: HSLColor, to: HSLColor): { [k: string]: StitchesColorDef } {
    const weights = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900];
    const keyValuePairs: [string, StitchesColorDef][] = weights.map((weight, idx) => {
      const token = `${name}${weight}`;
      const t = idx / (weights.length - 1);
      const color: HSLColor = {
        hue: integerLerp(from.hue, to.hue, t),
        sat: integerLerp(from.sat, to.sat, t),
        lum: integerLerp(from.lum, to.lum, t),
      };
      return [
        token,
        {
          token,
          value: `hsl(${color.hue}, ${color.sat}%, ${color.lum}%)`,
          scale: "colors",
          prefix: SVELTEUI_PREFIX,
        },
      ];
    });

    return Object.fromEntries(keyValuePairs);
  }

  const blueShadesOverride = generateColors("blue", { hue: 190, sat: 100, lum: 78 }, { hue: 199, sat: 88, lum: 10 });
</script>

<SvelteUIProvider
  theme={{
    colors: {
      ...DEFAULT_THEME.colors,
      ...blueShadesOverride,
    },
    // radii: {
    //   ...DEFAULT_THEME.radii,
    //   xs: "20px",
    //   sm: "20px",
    //   md: "25px",
    //   lg: "32px",
    //   xl: "64px",
    // },
  }}
  themeObserver={"light"}
  inherit
  override={{
    // FOR SOME REASON RADIUS IS NOT OVERRIDEN LIKE COLOR
    // BUT WITH THIS SHIT??????????
    "--svelteui-radii-sm": "20px",
  }}
>
  <slot />
</SvelteUIProvider>
