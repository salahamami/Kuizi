// Stand-in for a Pact consumer test: writes a pact file where CI collects it (pacts/).
import { mkdirSync, writeFileSync } from "node:fs";

mkdirSync("pacts", { recursive: true });
const pact = { consumer: { name: "ci-canary" }, provider: { name: "none" }, interactions: [] };
writeFileSync("pacts/ci-canary-none.json", JSON.stringify(pact, null, 2));
console.log("contract test: pacts/ci-canary-none.json written");
