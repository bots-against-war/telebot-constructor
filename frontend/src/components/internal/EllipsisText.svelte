<!-- Text element with a fixed max width that overflows with ellipsis -->
<script lang="ts">
  import { Text, type TextProps } from "@svelteuidev/core";

  interface EllipsisTextProps extends TextProps {
    maxWidth: string;
  }
  type $$Props = EllipsisTextProps;

  export let maxWidth: string;
</script>

<Text
  override={{
    ...$$restProps.override,
    maxWidth,
    textWrap: "nowrap",
    textOverflow: "ellipsis",
    overflowX: "hidden",
  }}
  {...$$restProps}><slot /></Text
>
