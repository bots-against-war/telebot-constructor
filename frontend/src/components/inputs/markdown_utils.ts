export type MarkdownEntityType = "bold" | "italic" | "strikethrough" | "spoiler" | "link" | "blockquote";

export interface MarkdownEntity {
  prefix: string;
  suffix: string;
  processed: string;
}

// see full docs at https://core.telegram.org/bots/api#markdownv2-style
// but bear in mind that the backend processed stuff with https://github.com/sudoskys/telegramify-markdown
export function makeMarkdownEntity(text: string, type: MarkdownEntityType, linkUrl: string = "url"): MarkdownEntity {
  switch (type) {
    case "bold":
      return { prefix: "**", suffix: "**", processed: text };
    case "italic":
      return { prefix: "_", suffix: "_", processed: text };
    case "strikethrough":
      return { prefix: "~~", suffix: "~~", processed: text };
    case "link":
      return { prefix: "[", suffix: `](${linkUrl})`, processed: text };
    case "blockquote":
      return {
        prefix: "\n",
        suffix: "\n\n",
        processed: text
          .split("\n")
          .map((line) => ">" + line)
          .join("\n"),
      };
    case "spoiler":
      return { prefix: "||", suffix: "||", processed: text };
    default:
      throw `Unexpected markdown entity type: ${type}`;
  }
}
