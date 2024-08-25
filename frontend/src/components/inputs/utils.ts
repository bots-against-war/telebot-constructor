export function getLengthError(max: number, length: number): string | null {
  if (length <= max) {
    return null;
  }

  let error = `Текст не может быть длиннее ${max} `;

  let numberString: string = max.toString();
  let lastDigit: number = +numberString.slice(numberString.length - 1, numberString.length);
  if (lastDigit === 1) {
    error += "символа";
  } else {
    error += "символов";
  }

  return error;
}
