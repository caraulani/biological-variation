// Run: node --test tests/rcv.test.ts   (Node >= 22.18 strips types natively)
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { rcv, compare, zScore, indexOfIndividuality } from "../src/ts/meaningful-change.ts";

const ex = JSON.parse(readFileSync(new URL("./literature_examples.json", import.meta.url), "utf8")).examples;

test("published RCVs", () => {
  for (const e of ex) {
    const i = e.inputs;
    const [down, up] = rcv(i.cvi, i.cva, i.probability ?? 0.95, i.sided ?? "two", i.model, i.z);
    const tol = 10 ** -e.decimals + 1e-9;
    if (e.expected.rcv_up !== undefined) assert.ok(Math.abs(up - e.expected.rcv_up) <= tol, `${e.id} up ${up}`);
    if (e.expected.rcv_down !== undefined) assert.ok(Math.abs(down - e.expected.rcv_down) <= tol, `${e.id} down ${down}`);
  }
});

test("z scores", () => {
  assert.ok(Math.abs(zScore(0.95, "two") - 1.959964) < 1e-5);
  assert.ok(Math.abs(zScore(0.95, "one") - 1.644854) < 1e-5);
  assert.ok(Math.abs(zScore(0.99, "two") - 2.575829) < 1e-5);
});

test("compare", () => {
  const r = compare({ value1: 100, value2: 140, cvi: 13.0, cva: 3.3, sided: "one" });
  assert.equal(r.exceeds, true);
  assert.equal(r.direction, "up");
  assert.equal(compare({ value1: 100, value2: 120, cvi: 13.0, cva: 3.3, sided: "one" }).exceeds, false);
  assert.throws(() => rcv(10, undefined as unknown as number));
});

test("python and typescript agree", () => {
  // Same inputs as tests/test_rcv.py::Behaviour; lognormal two-sided 95 %.
  const [d, u] = rcv(20, 3);
  assert.ok(Math.abs((1 + u / 100) * (1 + d / 100) - 1) < 1e-12);
  assert.ok(Math.abs(indexOfIndividuality(17.9, 36.2) - 0.49448) < 1e-4);
});
