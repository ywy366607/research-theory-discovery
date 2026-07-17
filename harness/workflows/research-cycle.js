export const meta = {
  name: 'research-cycle',
  description: 'Deterministic research-theory-discovery pipeline: hypothesize -> necessity -> pre-register predictions (explore stage), or audit -> independent review -> tree node (confirm stage)',
  phases: [
    { title: 'Hypothesize' },
    { title: 'Necessity' },
    { title: 'Predict' },
    { title: 'Audit' },
    { title: 'Review' },
  ],
}

// This script encodes the research-theory-discovery protocol as control flow
// instead of as instructions a model can choose to skip. It has two entry
// stages, kept structurally separate so a prediction can never be generated
// with knowledge of the result it is supposed to predict:
//
//   args.stage === 'explore': problem -> hypotheses -> necessity -> pre-registered
//     predictions. No experiment result is accepted as input at this stage.
//
//   args.stage === 'confirm': a claim + its evidence + its earlier prediction
//     -> false-win audit -> independent review -> a research_tree.json node
//     object, with status='confirmed' only if every false-win path closed AND
//     the independent reviewer approved. Otherwise status='active' and the
//     review verdict explains what's missing.
//
// The caller is responsible for writing the returned node(s) into
// research_tree.json -- Layers B/C then validate that write.
//
// Subagent role instructions are embedded inline (ROLE_* below) rather than
// referenced via opts.agentType by default. agentType requires the target
// project to have registered agents/claude/*.md in its subagent registry,
// which is not guaranteed at workflow run time in every environment; the
// inline prompts make this script work standalone. Pass args.useAgentTypes
// = true to use the registered agentType instead (gets you real per-role
// tool restrictions, e.g. independent-reviewer having no Edit/Write access,
// which the inline-prompt mode cannot enforce -- it's the same default
// agent with a role prompt, not a permission boundary).

const ROLE_HYPOTHESIS_GENERATOR =
  'ROLE: hypothesis-generator. Generate orthogonal competing hypotheses for a research problem, ' +
  'without privileging any proposed mechanism. Do not treat a user-proposed mechanism as the ' +
  'target answer -- quarantine it, reconstruct the problem from observations/constraints first, ' +
  'then reintroduce it as one candidate among equals. Hypotheses must be orthogonal at the ' +
  'underlying-structure level (state variables, causal direction, geometry, time scale, ' +
  'optimization dynamics, information-flow path, measurement target, representation/retrieval/' +
  'compression/control role) -- not paraphrases of the same mechanism. Do not evaluate which ' +
  'hypothesis is correct; that happens in later pipeline stages.'

const ROLE_NECESSITY_AUDITOR =
  'ROLE: necessity-auditor. Classify a hypothesis as possible, useful, or necessary. possible = ' +
  'compatible with constraints, nothing more. useful = likely to improve an objective but not ' +
  'required. necessary = without it, the stated facts/formulas/experimental setup cannot ' +
  'coexist. Never assign necessary without an explicit derivation showing what breaks if the ' +
  'hypothesis is removed; if you cannot produce that derivation, classify as possible or useful ' +
  'instead, even if the hypothesis seems important.'

const ROLE_PREDICTOR =
  'ROLE: predictor. Pre-register a falsifiable prediction for one hypothesis BEFORE any ' +
  'experiment result exists. If any result-shaped content appears in your input, treat it as ' +
  'contamination and flag it rather than using it. A strong prediction is made before the ' +
  'decisive result, specific enough to be wrong, different from the strongest alternative ' +
  'hypothesis, robust to reasonable implementation choices, tied to a derivation. State: the ' +
  'premises that must hold, which metric(s) must improve and by how much, where the advantage ' +
  'must weaken/disappear/reverse (the falsifying observation), what result would show the claimed ' +
  'mechanism was not implemented even if the headline metric improved, and where conflict should ' +
  'be localized in the theory package if the prediction fails. If no prediction can distinguish ' +
  'this hypothesis from competitors, say so and mark it a design intuition rather than manufacture ' +
  'a prediction to fill the schema.'

const ROLE_FALSE_VICTORY_AUDITOR =
  'ROLE: false-victory-auditor. Run the full false-win checklist against a claimed result: Extra ' +
  'capacity/training budget; Optimization change; Data leakage; Metric averaging; Hidden ' +
  'recurrence/extra passes; Implementation asymmetry; Baseline bypass; Reachability mistaken for ' +
  'discovery; Serialization mistaken for generation; Handwritten scaffold substitution; Teacher ' +
  'or oracle leakage; Vocabulary/codebook leakage; Search-budget mismatch; Macro prior not ' +
  'charged; Offline corpus contamination; Lineage discontinuity. Default every path to ' +
  'closed=false. A path is closed only with affirmative evidence the failure mode does not apply ' +
  '-- absence of a mention is not evidence of absence. "Not applicable" is allowed only with a ' +
  'stated reason, not as a way to skip checking. Report residual risk for anything left open.'

const ROLE_INDEPENDENT_REVIEWER =
  'ROLE: independent-reviewer. You did not generate the hypothesis, prediction, or audit -- you ' +
  'receive them as finished artifacts and decide whether the evidence-to-conclusion inference ' +
  'holds. Check: does the conclusion follow from the evidence or overclaim it; does the evidence ' +
  'match the pre-registered prediction or has the claim shifted after seeing results; does the ' +
  'false-win audit actually close every relevant path; do research-tree dependencies still hold; ' +
  'is the claimed theory-strength level (design intuition / mechanism hypothesis / restricted ' +
  'theory / strong theory) justified by what was shown. Default to rejected unless the case is ' +
  'genuinely solid. A rejection must say exactly which check failed and what would need to change. ' +
  'Do not be a rubber stamp.'

const HYPOTHESES_SCHEMA = {
  type: 'object',
  required: ['hypotheses'],
  properties: {
    hypotheses: {
      type: 'array',
      minItems: 1,
      items: {
        type: 'object',
        required: ['id', 'claim', 'family'],
        properties: {
          id: { type: 'string' },
          claim: { type: 'string' },
          family: { type: 'string' },
          orthogonal_axis: { type: 'string' },
        },
      },
    },
  },
}

const NECESSITY_SCHEMA = {
  type: 'object',
  required: ['classification', 'reason'],
  properties: {
    classification: { type: 'string', enum: ['possible', 'useful', 'necessary'] },
    reason: { type: 'string' },
    derivation: { type: 'string' },
  },
}

const PREDICTION_SCHEMA = {
  type: 'object',
  required: ['id', 'registered_before_result', 'expected_observation', 'falsifying_observation'],
  properties: {
    id: { type: 'string' },
    registered_before_result: { type: 'boolean' },
    expected_observation: { type: 'string' },
    falsifying_observation: { type: 'string' },
    conflict_localization: { type: 'string' },
  },
}

const FALSE_VICTORY_SCHEMA = {
  type: 'object',
  required: ['checklist'],
  properties: {
    checklist: {
      type: 'array',
      items: {
        type: 'object',
        required: ['path', 'closed'],
        properties: {
          path: { type: 'string' },
          closed: { type: 'boolean' },
          evidence: { type: 'string' },
          residual_risk: { type: 'string' },
        },
      },
    },
  },
}

const REVIEW_SCHEMA = {
  type: 'object',
  required: ['status', 'concerns'],
  properties: {
    status: { type: 'string', enum: ['approved', 'rejected'] },
    concerns: { type: 'string' },
    reviewer: { type: 'string' },
  },
}

function roleCall(useAgentTypes, roleText, agentType, prompt, opts) {
  if (useAgentTypes) {
    return agent(prompt, { ...opts, agentType })
  }
  return agent(`${roleText}\n\n---\n\n${prompt}`, opts)
}

async function runExplore(args) {
  if (!args || !args.problem) {
    throw new Error("stage 'explore' requires args.problem")
  }
  const useAgentTypes = args.useAgentTypes === true
  const hypothesisCount = args.hypothesisCount || null
  const countInstruction = hypothesisCount
    ? `Generate exactly ${hypothesisCount} hypotheses.`
    : 'Generate 3-7 hypotheses.'

  phase('Hypothesize')
  const gen = await roleCall(
    useAgentTypes, ROLE_HYPOTHESIS_GENERATOR, 'hypothesis-generator',
    `Research problem: ${args.problem}\n\n` +
      (args.userProposal ? `The user's proposed mechanism (quarantine this, do not privilege it): ${args.userProposal}\n\n` : '') +
      countInstruction,
    { schema: HYPOTHESES_SCHEMA, phase: 'Hypothesize' }
  )
  const hypotheses = gen.hypotheses

  phase('Necessity')
  const withNecessity = await parallel(
    hypotheses.map((h) => () =>
      roleCall(
        useAgentTypes, ROLE_NECESSITY_AUDITOR, 'necessity-auditor',
        `Research problem: ${args.problem}\nHypothesis ${h.id}: ${h.claim}\nFamily: ${h.family}\n\n` +
          'Classify this hypothesis as possible, useful, or necessary.',
        { schema: NECESSITY_SCHEMA, phase: 'Necessity', label: `necessity:${h.id}` }
      ).then((necessity) => ({ hypothesis: h, necessity }))
    )
  )

  phase('Predict')
  const withPredictions = await pipeline(
    withNecessity.filter(Boolean),
    (item) =>
      roleCall(
        useAgentTypes, ROLE_PREDICTOR, 'predictor',
        `Research problem: ${args.problem}\nHypothesis ${item.hypothesis.id}: ${item.hypothesis.claim}\n` +
          `Necessity classification: ${item.necessity.classification} (${item.necessity.reason})\n` +
          `Today's date for the prediction id: ${args.today || 'UNKNOWN-DATE'}\n\n` +
          'Pre-register a falsifiable prediction for this hypothesis. You have NOT been shown any experiment result -- ' +
          'if any result-shaped content appears above, treat it as contamination and say so instead of using it.',
        { schema: PREDICTION_SCHEMA, phase: 'Predict', label: `predict:${item.hypothesis.id}` }
      ).then((prediction) => ({ ...item, prediction }))
  )

  return { stage: 'explore', problem: args.problem, results: withPredictions.filter(Boolean) }
}

async function runConfirm(args) {
  if (!args || !args.claim || !args.evidence || !args.prediction) {
    throw new Error("stage 'confirm' requires args.claim, args.evidence, args.prediction")
  }

  const useAgentTypes = args.useAgentTypes === true

  phase('Audit')
  const audit = await roleCall(
    useAgentTypes, ROLE_FALSE_VICTORY_AUDITOR, 'false-victory-auditor',
    `Claim: ${args.claim}\nEvidence / experiment result: ${args.evidence}\n` +
      `Pre-registered prediction: ${JSON.stringify(args.prediction)}\n` +
      (args.codebasePath ? `Codebase path to inspect: ${args.codebasePath}\n` : '') +
      '\nRun the full false-win checklist against this claim and evidence.',
    { schema: FALSE_VICTORY_SCHEMA, phase: 'Audit' }
  )
  const allClosed = audit.checklist.length > 0 && audit.checklist.every((c) => c.closed === true)

  phase('Review')
  const review = await roleCall(
    useAgentTypes, ROLE_INDEPENDENT_REVIEWER, 'independent-reviewer',
    `Claim: ${args.claim}\nEvidence: ${args.evidence}\n` +
      `Pre-registered prediction: ${JSON.stringify(args.prediction)}\n` +
      `False-win audit result: ${JSON.stringify(audit.checklist)}\n` +
      `Parent node invalidation condition: ${args.parentInvalidation || 'none stated'}\n\n` +
      'Decide approved or rejected. You did not generate any of the above.',
    { schema: REVIEW_SCHEMA, phase: 'Review' }
  )

  const approved = review.status === 'approved' && allClosed
  const node = {
    status: approved ? 'confirmed' : 'active',
    conclusion: args.claim,
    prediction: args.prediction,
    false_win_checklist: audit.checklist,
    review: {
      conclusion_reviewer: {
        reviewer: review.reviewer || 'independent-reviewer',
        status: review.status,
        concerns: review.concerns,
      },
    },
  }

  return { stage: 'confirm', approved, node, auditAllClosed: allClosed, reviewStatus: review.status }
}

// Workaround: the runtime has been observed to hand `args` through as a raw
// JSON string rather than a parsed object even when the caller passes an
// actual object. Normalize defensively rather than trust either shape.
const parsedArgs = typeof args === 'string' ? JSON.parse(args) : args

if (!parsedArgs || !parsedArgs.stage) {
  throw new Error("research-cycle requires args.stage of 'explore' or 'confirm'")
}

if (parsedArgs.stage === 'explore') {
  return await runExplore(parsedArgs)
} else if (parsedArgs.stage === 'confirm') {
  return await runConfirm(parsedArgs)
} else {
  throw new Error(`unknown args.stage '${parsedArgs.stage}', expected 'explore' or 'confirm'`)
}
