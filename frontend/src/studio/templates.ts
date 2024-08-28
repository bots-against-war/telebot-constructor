import type { CommandEntryPoint, UserFlowConfig } from "../api/types";
import { DEFAULT_START_COMMAND_ENTRYPOINT_ID } from "../constants";
import { NodeTypeKey } from "./nodes/display";
import { boundingBox, generateNodeId, NodeKind } from "./utils";

export interface Template {
  config: UserFlowConfig;
  entryBlockId: string;
  customStartCmd: CommandEntryPoint;
}

export function contentOnlyTemplate(): Template {
  const contentBlockId = generateNodeId(NodeKind.block, NodeTypeKey.content);
  const config: UserFlowConfig = {
    entrypoints: [],
    blocks: [
      {
        content: {
          block_id: contentBlockId,
          contents: [
            {
              text: {
                text: "**«Римские каникулы»** (англ. _Roman Holiday_) — американская романтическая комедия с элементами мелодрамы 1953 года. Фильм снят по литературному сценарию Далтона Трамбо, режиссёр и продюсер Уильям Уайлер. В главной мужской роли Грегори Пек, в главной женской роли Одри Хепбёрн (первая значительная роль Хепбёрн, которая принесла актрисе премию «Оскар»).\n\n**Сюжет**\n\n>Анна — юная принцесса неназванного европейского государства, которая прибывает в Рим в рамках своего широко разрекламированного дипломатического тура по странам Европы. Время её расписано по минутам, а титул предполагает строгое следование этикету и тяготящие её длинные церемонии. На официальном балу она принимает первых лиц Италии и послов других стран, а после приёма — зная, что завтрашний день тоже будет представлять собой череду официальных визитов и пресс-конференций — срывается, не в силах более выносить груз королевских обязанностей, которые ограничивают её свободу. Чтобы остановить её истерику, придворный врач делает Анне укол нового снотворного и седативного средства, уверяя, что ей это наверняка поможет.\n>...\n>Ввиду своего увлечения, Джо принимает решение не публиковать статью о принцессе. Его коллеги в недоумении — босс считает, что Брэдли лукавит и таким образом пытается поднять цену на материал, а Ирвин, показав другу проявленные фотографии, — прямо заявляет, что тот сошёл с ума, выпуская из рук такую сенсацию. Фильм заканчивается ||невесёлой сценой пресс-конференции, на которой среди прочих журналистов Анна замечает Ирвина и Джо. На пресс-конференции она словно обращается напрямую к Джо, вкладывая в свои слова двойной смысл — так, на вопрос о том, какой город из всей поездки ей понравился больше всего, Анна вопреки подсказкам советников говорит, что никогда не забудет Рим и будет до конца жизни хранить память о нём.||\n\n[Википедия](https://ru.wikipedia.org/wiki/%D0%A0%D0%B8%D0%BC%D1%81%D0%BA%D0%B8%D0%B5_%D0%BA%D0%B0%D0%BD%D0%B8%D0%BA%D1%83%D0%BB%D1%8B)",
                markup: "markdown",
              },
              attachments: [],
            },
          ],
          next_block_id: null,
        },
        human_operator: null,
        menu: null,
        form: null,
        language_select: null,
        error: null,
      },
    ],
    node_display_coords: {},
  };
  config.node_display_coords[contentBlockId] = { x: 0, y: 130 };
  return {
    config,
    entryBlockId: contentBlockId,
    customStartCmd: {
      entrypoint_id: generateNodeId(NodeKind.entrypoint, NodeTypeKey.command),
      command: "content",
      next_block_id: null,
      scope: "private",
    },
  };
}

export function applyTemplate(config: UserFlowConfig, template: Template): UserFlowConfig {
  const startCommand = config.entrypoints.find(
    (ep) => ep.command?.entrypoint_id === DEFAULT_START_COMMAND_ENTRYPOINT_ID,
  )?.command;
  if (!startCommand) {
    throw "Start command not found in the config!";
  }

  config.entrypoints.push(...template.config.entrypoints);
  config.blocks.push(...template.config.blocks);
  if (startCommand.next_block_id === null) {
    startCommand.next_block_id = template.entryBlockId;
    config.node_display_coords = { ...config.node_display_coords, ...template.config.node_display_coords };
  } else {
    template.customStartCmd.next_block_id = template.entryBlockId;
    template.config.node_display_coords[template.customStartCmd.entrypoint_id] = { x: 0, y: 0 };

    config.entrypoints.push({ command: template.customStartCmd });
    const existingBbox = boundingBox(config.node_display_coords, 250, 200);
    const templateBbox = boundingBox(template.config.node_display_coords, 250, 200);

    // we want to move only in x direction for simplicity
    console.debug("existing bbox", existingBbox);
    console.debug("template bbox", templateBbox);
    let xOffset = 0;
    if (!(existingBbox.yMax < templateBbox.yMin || existingBbox.yMin > templateBbox.yMax)) {
      // there's an intersection along y axis
      const xMargin = 30;
      const xDeltaRight = Math.max(existingBbox.xMax - templateBbox.xMin, 0.0);
      const xDeltaLeft = Math.max(templateBbox.xMax - existingBbox.xMin, 0.0);
      console.debug("delta right", xDeltaRight, "delta left", xDeltaLeft);
      xOffset = xDeltaRight < xDeltaLeft ? xDeltaRight + xMargin : -xDeltaLeft - xMargin;
      console.debug("offset", xOffset);
    }
    config.node_display_coords = {
      ...config.node_display_coords,
      ...Object.fromEntries(
        Object.entries(template.config.node_display_coords).map(([key, { x, y }]) => [key, { x: x + xOffset, y }]),
      ),
    };
  }
  return config;
}
