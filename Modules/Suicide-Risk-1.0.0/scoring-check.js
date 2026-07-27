const fs = require("fs");

global.window = { location: { search: "" } };
global.localStorage = { setItem() {} };

eval(fs.readFileSync(`${__dirname}/app.js`, "utf8"));

const evaluate = window.SuicideScore.evaluate;
const blank = {
  q1: null,
  q2: null,
  q3: null,
  q4: null,
  q5: null,
  q6: null,
  q6Recent: null,
};

const cases = [
  ["incomplete", blank, "Incomplete", false],
  ["none", { ...blank, q1: false, q2: false, q6: false }, "No current risk endorsed", true],
  ["low", { ...blank, q1: true, q2: false, q6: false }, "Low risk", true],
  [
    "moderate-method",
    { ...blank, q1: false, q2: true, q3: true, q4: false, q5: false, q6: false },
    "Moderate risk",
    true,
  ],
  ["moderate-lifetime", { ...blank, q1: false, q2: false, q6: true, q6Recent: false }, "Moderate risk", true],
  [
    "high-intent",
    { ...blank, q1: false, q2: true, q3: false, q4: true, q5: false, q6: false },
    "High risk",
    true,
  ],
  ["high-recent", { ...blank, q1: false, q2: false, q6: true, q6Recent: true }, "High risk", true],
];

for (const [name, answers, result, completed] of cases) {
  const actual = evaluate(answers);
  if (actual.result !== result || actual.completed !== completed) {
    throw new Error(`${name} failed: ${JSON.stringify(actual)}`);
  }
}

console.log("scoring checks passed");
