import {
  EyeSlashSolid,
  LetterBoldOutline,
  LetterItalicOutline,
  LinkOutline,
  QuoteSolid,
  TextSlashOutline,
} from "flowbite-svelte-icons";
import { marked, type RendererObject, type Token, type TokenizerAndRendererExtension } from "marked";
import type { SvelteComponent } from "svelte";
import type { Newable } from "ts-essentials";

export type MarkdownEntityType = "bold" | "italic" | "strikethrough" | "spoiler" | "link" | "blockquote";

export const markdownEntityData: [Newable<SvelteComponent>, MarkdownEntityType, string][] = [
  [LetterBoldOutline, "bold", "Жирный"],
  [LetterItalicOutline, "italic", "Курсив"],
  [QuoteSolid, "blockquote", "Цитата"],
  [LinkOutline, "link", "Ссылка"],
  [TextSlashOutline, "strikethrough", "Зачеркнутый"],
  [EyeSlashSolid, "spoiler", "Спойлер"],
];

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

const telegramSpoiler: TokenizerAndRendererExtension = {
  name: "spoiler",
  level: "inline",
  start(src: string): number | undefined {
    return src.match(/||/)?.index;
  },
  tokenizer(src: string, tokens: Token[]): Token | undefined {
    const match = /^\|\|([^|\n]+)\|\|/.exec(src);
    if (match) {
      return {
        type: "spoiler",
        raw: match[0],
        body: this.lexer.inlineTokens(match[1].trim()),
      };
    }
  },
  renderer(token: any): string {
    // HACK: dependence on global style
    return `<span class="md-preview-spoiler">${this.parser.parseInline(token.body)}</span>`;
  },
  childTokens: ["body"],
};

const customRenderer: RendererObject = {
  link({ tokens, href }): string {
    return `<a href="${href}" target="_blank">${this.parser.parseInline(tokens)}</a>`;
  },
};

marked.use({
  async: false,
  breaks: true,
  gfm: true,
  silent: true,
  extensions: [telegramSpoiler],
  renderer: customRenderer,
});

export function renderPreview(text: string): string {
  // @ts-expect-error
  return marked.parse(text);
}
