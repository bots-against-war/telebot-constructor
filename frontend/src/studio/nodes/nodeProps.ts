import type { ComponentProps } from "svelte";
import { Node } from "svelvet";

export const DEFAULT_NODE_PROPS: ComponentProps<Node> = {
  bgColor: "white",
  textColor: "black",
  borderColor: "rgb(206, 212, 218)",
  // @ts-ignore
  borderWidth: "1px",
  borderRadius: 10,
  editable: false,
};
