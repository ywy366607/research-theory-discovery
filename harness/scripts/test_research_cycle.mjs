// Control-flow tests only: no LLM calls, model training, or experiment execution.
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const source = (await readFile(new URL('../workflows/research-cycle.js', import.meta.url), 'utf8'))
  .replace('export const meta =', 'const meta =')
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor
const workflow = new AsyncFunction('args', 'agent', 'parallel', 'pipeline', 'phase', source)

async function run(args, responses) {
  const pending = structuredClone(responses)
  const calls = []
  const result = await workflow(args, async (prompt, options) => {
    calls.push({ prompt, options })
    assert.ok(pending.length > 0, 'unexpected agent call')
    return pending.shift()
  }, async (jobs) => Promise.all(jobs.map((job) => job())),
  async (items, fn) => Promise.all(items.map(fn)), () => {})
  assert.equal(pending.length, 0, 'unused mock response')
  return { result, calls }
}

const prediction = {
  id: 'P-test', registered_before_result: true,
  expected_observation: 'Target improves; magnitude unknown',
  falsifying_observation: 'No target gain under the registered comparison',
}
const planArgs = {
  stage: 'plan', objective: 'Improve continuous prediction',
  hypothesis: { claim: 'A missing information path can be opened' },
  prediction, experiment: 'Bounded construction and interface check',
}
const goodPlan = {
  status: 'approved', objective: planArgs.objective,
  primary_metric: 'Next-event prediction error', metric_role: 'target',
  baseline: 'Retain the strongest reproducible checkpoint',
  core_change: 'Open the missing information path', claim_scope: 'exploration',
  feasibility: { status: 'unresolved', basis: 'Construct the causal path and check its Jacobian' },
  purpose: 'discovery', budget_and_evaluation: 'Bounded interface check, no capability claim',
  stopping_condition: 'Stop if the proposed path remains unreachable', concerns: '',
  decision_branches: {
    gain: { criterion: 'Path carries input', action: 'Register a joint-training comparison' },
    no_gain: { criterion: 'Path remains absent', action: 'Redesign the information path' },
    ambiguous: { criterion: 'Numerical uncertainty', action: 'Run one precision cross-check' },
  },
}
let passed = 0
async function test(name, fn) {
  await fn()
  passed += 1
  console.log(`PASS ${name}`)
}

await test('bounded design intuition passes; approval never authorizes execution', async () => {
  const { result } = await run(JSON.stringify(planArgs), [goodPlan])
  assert.equal(result.approved_to_register, true)
  assert.equal(result.execution_authorized, false)
})
await test('same decision for every outcome blocks redundant measurement', async () => {
  const plan = structuredClone(goodPlan)
  for (const branch of Object.values(plan.decision_branches)) branch.action = 'Continue unchanged'
  const { result } = await run(planArgs, [plan])
  assert.equal(result.approved_to_register, false)
  assert.ok(result.contractErrors.some((e) => e.includes('same action')))
})
await test('necessary acceptance permits same action only with reason', async () => {
  const plan = structuredClone(goodPlan)
  for (const branch of Object.values(plan.decision_branches)) branch.action = 'Record acceptance result'
  plan.purpose = 'necessary_acceptance'
  assert.equal((await run(planArgs, [plan])).result.approved_to_register, false)
  plan.acceptance_necessity = 'Required numerical precision acceptance before integration'
  assert.equal((await run(planArgs, [plan])).result.approved_to_register, true)
})
await test('unreachable path and unresolved capability require redesign/check', async () => {
  const plan = structuredClone(goodPlan)
  plan.feasibility.status = 'unreachable'
  assert.equal((await run(planArgs, [plan])).result.approved_to_register, false)
  plan.feasibility.status = 'unresolved'
  plan.claim_scope = 'capability'
  assert.equal((await run(planArgs, [plan])).result.approved_to_register, false)
})
await test('proxy without objective bridge and missing decision criteria are blocked', async () => {
  const plan = structuredClone(goodPlan)
  plan.metric_role = 'proxy'
  delete plan.decision_branches.ambiguous.criterion
  const { result } = await run(planArgs, [plan])
  assert.equal(result.approved_to_register, false)
  assert.equal(result.contractErrors.length, 2)
})
await test('review rejection and post-result prediction cannot approve plan', async () => {
  assert.equal((await run(planArgs, [{ ...goodPlan, status: 'rejected' }])).result.approved_to_register, false)
  const args = { ...planArgs, prediction: { ...prediction, registered_before_result: false } }
  assert.equal((await run(args, [goodPlan])).result.approved_to_register, false)
})
const confirmArgs = { stage: 'confirm', claim: 'Local interface is connected',
  evidence: 'Deterministic derivative checks', prediction }
const audit = { checklist: [{ path: 'Baseline bypass', closed: true, evidence: 'Matched interface check' }] }
const review = { status: 'approved', concerns: '' }
await test('confirmed needs evidence and pre-result registration, beyond reviewer approval', async () => {
  const good = (await run(confirmArgs, [audit, review])).result
  assert.equal(good.node.status, 'confirmed')
  const noEvidence = { checklist: [{ path: 'Baseline bypass', closed: true }] }
  assert.equal((await run(confirmArgs, [noEvidence, review])).result.node.status, 'active')
  const args = { ...confirmArgs, prediction: { ...prediction, registered_before_result: false } }
  const invalid = (await run(args, [audit, review])).result
  assert.equal(invalid.node.status, 'active')
  assert.match(invalid.node.review.conclusion_reviewer.concerns, /Prediction/)
})
await test('explore propagates objective and feasible construction to later roles', async () => {
  const args = { stage: 'explore', problem: 'Improve prediction',
    targetContract: { objective: 'Continuous prediction', baseline: 'champion' } }
  const hypothesis = { id: 'H1', claim: 'Open a causal path', family: 'information flow',
    core_change: 'New state path', feasibility_basis: 'Constructive causal map' }
  const { result, calls } = await run(args, [
    { hypotheses: [hypothesis] }, { classification: 'possible', reason: 'Constructible' }, prediction,
  ])
  assert.deepEqual(result.targetContract, args.targetContract)
  assert.equal(result.results.length, 1)
  assert.match(calls[1].prompt, /Constructive causal map/)
  assert.match(calls[2].prompt, /champion/)
  const legacy = await run({ stage: 'explore', problem: 'Legacy objective' }, [
    { hypotheses: [hypothesis] }, { classification: 'possible', reason: 'Constructible' }, prediction,
  ])
  assert.equal(legacy.result.targetContract.objective, 'Legacy objective')
})
await test('unsupported stages and incomplete plans fail before calling agents', async () => {
  await assert.rejects(run({ stage: 'other' }, []), /unknown args.stage/)
  await assert.rejects(run({ stage: 'plan', objective: 'Only objective' }, []), /requires/)
})
console.log(`${passed} contract tests passed (mock runtime; no live agent review).`)
