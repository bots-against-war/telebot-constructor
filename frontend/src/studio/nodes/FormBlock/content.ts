import { type FormMessages } from "../../../api/types";

interface FormExampleContent {
  name: string;
  prompt: string;
}

export const EXAMPLE_CONTENT: FormExampleContent[] = [
  {
    name: "Имя",
    prompt: "Введите ваше имя.",
  },
  {
    name: "Возраст",
    prompt: "Сколько вам лет?",
  },
  {
    name: "Email",
    prompt: "Укажите ваш адрес электронной почты.",
  },
  {
    name: "Город",
    prompt: "Укажите ваш текущий город проживания.",
  },
  {
    name: "Занятие",
    prompt: "Какая у вас профессия или род деятельности?",
  },
  {
    name: "Оценка",
    prompt: "Поставьте оценку от 1 до 10, где 1 - очень плохо, 10 - отлично.",
  },
  {
    name: "Любимый цвет",
    prompt: "Какой у вас любимый цвет?",
  },
  {
    name: "Комментарий",
    prompt: "Есть ли у вас какие-либо дополнительные комментарии или пожелания?",
  },
  {
    name: "Любимое животное",
    prompt: "Какое ваше любимое животное?",
  },
  {
    name: "Любимый фильм",
    prompt: "Назовите ваш любимый фильм.",
  },
  {
    name: "Любимая книга",
    prompt: "Какая ваша любимая книга?",
  },
  {
    name: "Любимый вид спорта",
    prompt: "Какой ваш любимый вид спорта?",
  },
  {
    name: "Любимая еда",
    prompt: "Какое ваше любимое блюдо?",
  },
  {
    name: "Любимый цветок",
    prompt: "Какой ваш любимый цветок?",
  },
  {
    name: "Любимый эпизод SW",
    prompt: 'Назовите ваш любимый эпизод "Звездных Войн".',
  },
  {
    name: "Путешествия",
    prompt: "Какие места вы мечтаете посетить в будущем?",
  },
  {
    name: "Хобби",
    prompt: "У вас есть какие-либо увлечения или хобби? Опишите их.",
  },
  {
    name: "Суперспособность",
    prompt: "Если бы у вас была суперспособность, какую бы вы выбрали?",
  },
];

export function getRandomContent(): FormExampleContent {
  const idx = Math.floor(Math.random() * EXAMPLE_CONTENT.length);
  return EXAMPLE_CONTENT[idx];
}

export function formMessageName(key: keyof FormMessages | string): string {
  switch (key) {
    case "form_start":
      return "В начале заполнения формы";
    case "field_is_skippable":
      return "Когда поле можно пропустить";
    case "field_is_not_skippable":
      return "Когда поле нельзя пропустить";
    case "please_enter_correct_value":
      return "При некорректном значении";
    case "unsupported_command":
      return "При неподдерживаемой команде";
    default:
      return key;
  }
}
