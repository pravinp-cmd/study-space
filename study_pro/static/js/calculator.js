const display = document.getElementById("display");

let current = "0";
let storedValue = null;
let pendingOperator = null;
let startNewNumber = false;

function show(value) {
  display.textContent = value;
}

function formatNumber(value) {
  if (!Number.isFinite(value)) return "Error";
  return String(Number(value.toPrecision(10)));
}

function enterDigit(digit) {
  if (startNewNumber || current === "Error") {
    current = digit;
    startNewNumber = false;
  } else if (current === "0") {
    current = digit;
  } else if (current.length < 14) {
    current += digit;
  }

  show(current);
}

function calculate() {
  if (pendingOperator === null || storedValue === null) return;

  const rightValue = Number(current);
  let result;

  switch (pendingOperator) {
    case "+":
      result = storedValue + rightValue;
      break;
    case "-":
      result = storedValue - rightValue;
      break;
    case "*":
      result = storedValue * rightValue;
      break;
    case "/":
      result = rightValue === 0 ? NaN : storedValue / rightValue;
      break;
    default:
      return;
  }

  current = formatNumber(result);
  storedValue = null;
  pendingOperator = null;
  startNewNumber = true;
  show(current);
}

document.querySelector(".keypad").addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;

  if (button.dataset.digit !== undefined) {
    enterDigit(button.dataset.digit);
    return;
  }

  if (button.dataset.operator) {
    if (pendingOperator !== null && !startNewNumber) {
      calculate();
    }

    storedValue = Number(current);
    pendingOperator = button.dataset.operator;
    startNewNumber = true;
    return;
  }

  switch (button.dataset.action) {
    case "clear":
      current = "0";
      storedValue = null;
      pendingOperator = null;
      startNewNumber = false;
      show(current);
      break;

    case "decimal":
      if (startNewNumber || current === "Error") {
        current = "0";
        startNewNumber = false;
      }
      if (!current.includes(".")) current += ".";
      show(current);
      break;

    case "sign":
      if (current !== "0" && current !== "Error") {
        current = String(Number(current) * -1);
        show(current);
      }
      break;

    case "percent":
      if (current !== "Error") {
        current = formatNumber(Number(current) / 100);
        show(current);
      }
      break;

    case "equals":
      calculate();
      break;
  }
});

document.addEventListener("keydown", (event) => {
  if (/^\d$/.test(event.key)) {
    enterDigit(event.key);
  } else if (event.key === ".") {
    document.querySelector('[data-action="decimal"]').click();
  } else if (["+", "-", "*", "/"].includes(event.key)) {
    document
      .querySelector(`[data-operator="${event.key}"]`)
      .click();
  } else if (event.key === "Enter" || event.key === "=") {
    document.querySelector('[data-action="equals"]').click();
  } else if (event.key === "Escape") {
    document.querySelector('[data-action="clear"]').click();
  }
});