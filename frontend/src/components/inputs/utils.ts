function getLengthError(max: number | null, length: number): string | null {
  if (typeof max === "number" && length > max) {
    let error = `Текст должен быть короче ${max} `;

    let numberString: string = max.toString();
    let lastDigit: number = +numberString.slice(numberString.length - 1, numberString.length);
    if (lastDigit === 1) {
      error += "символа";
    } else {
      error += "символов";
    }

    return error;
  }

  return null;
}

function defineName(label: string | null): string {
  function makeUnique(value: string): string {
    const serializedValue = value.toLocaleLowerCase().replaceAll(" ", "-");
    return addCode(serializedValue);
  }

  function addCode(value: string): string {
    const symbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let code = "-";
    for (let i = 0; i < 7; ++i) {
      const randomIndex = Math.floor(Math.random() * symbols.length);
      code += symbols.slice(randomIndex, randomIndex + 1);
    }

    return value + code;
  }

  if (label) return makeUnique(label);

  return makeUnique("implicit-input");
}

export { getLengthError, defineName };
