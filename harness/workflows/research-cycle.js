export const meta = {
  name: 'research-cycle',
  description: 'Ascent-descent research pipeline: axiomatize phenomena into minimal axioms (axiomatize), generate feasible candidates (explore), review a decision experiment (plan), audit and review a conclusion (confirm), or locate a failed prediction layer by layer (diagnose)',
  phases: [
    { title: 'Hypothesize' },
    { title: 'Necessity' },
    { title: 'Predict' },
    { title: 'Plan' },
    { title: 'Audit' },
    { title: 'Review' },
    { title: 'Axiomatize' },
    { title: 'Independence' },
    { title: 'Diagnose' },
  ],
}

// This script encodes the research-theory-discovery protocol as control flow
// instead of as instructions a model can choose to skip. It has three entry
// stages, kept structurally separate so a prediction can never be generated
// with knowledge of the result it is supposed to predict:
//
//   args.stage === 'explore': problem -> hypotheses -> necessity -> pre-registered
//     predictions. No experiment result is accepted as input at this stage.
//
//   args.stage === 'plan': selected candidate -> independent experiment review
//     -> deterministic decision-contract checks. Registration approval is not
//     execution authorization. This workflow never launches an experiment.
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
  'hypothesis is correct; that happens in later pipeline stages. Fix the user objective and ' +
  'strongest reproducible baseline before choosing proxies. For architecture search include a ' +
  'candidate that opens a new feasible space (state, causal path, learning object, or timing), ' +
  'or explain why the existing space already represents the target. Give each candidate a ' +
  'core change and constructive feasibility basis. User intuition is a discovery cue; construct ' +
  'its strongest testable version and compare fairly.'

const ROLE_NECESSITY_AUDITOR =
  'ROLE: necessity-auditor. Classify a hypothesis as possible, useful, or necessary. possible = ' +
  'compatible with constraints, nothing more. useful = likely to improve an objective but not ' +
  'required. necessary = without it, the stated facts/formulas/experimental setup cannot ' +
  'coexist. Never assign necessary without an explicit derivation showing what breaks if the ' +
  'hypothesis is removed; if you cannot produce that derivation, classify as possible or useful ' +
  'instead, even if the hypothesis seems important. Check whether information reaches the ' +
  'decision and supervision can change the computation. A missing path calls for a minimal ' +
  'structural change; reachability justifies trying, not a claim of capability. Bounded ' +
  'exploratory implementation can proceed from an explicit design intuition without a full theorem.'

const ROLE_PREDICTOR =
  'ROLE: predictor. Pre-register a falsifiable prediction for one hypothesis BEFORE any ' +
  'decisive experiment result exists. Prior observations may motivate a new prediction; if the ' +
  'result of the proposed decisive test appears, flag contamination. A strong prediction is made before the ' +
  'decisive result, specific enough to be wrong, different from the strongest alternative ' +
  'hypothesis, robust to reasonable implementation choices, tied to a derivation. State: the ' +
  'premises that must hold, which target metric(s) must improve, where the advantage ' +
  'must weaken/disappear/reverse (the falsifying observation), what result would show the claimed ' +
  'mechanism was not implemented even if the headline metric improved, and where conflict should ' +
  'be localized in the theory package if the prediction fails. If no prediction can distinguish ' +
  'this hypothesis from competitors, say so and mark it a design intuition rather than manufacture ' +
  'a prediction to fill the schema. Numerical effect sizes require derivation or independent ' +
  'prior evidence; otherwise mark magnitude unknown and define a bounded exploratory test. ' +
  'Distinguish user capability objectives from mechanism proxies. State gain, no-gain, and ' +
  'ambiguous outcomes and the different decisions they support.'

const ROLE_EXPERIMENT_PLANNER =
  'ROLE: experiment-planner. Independently review the selected hypothesis, prediction, and proposed ' +
  'experiment. Return a compact decision contract, not a new checklist of measurements. Preserve ' +
  'the strongest reproducible baseline and user constraints. Identify one core change; explain ' +
  'inseparable coupled changes. Separate target performance from mechanism proxies, discovery from ' +
  'attribution, and feasibility from success. A design intuition may justify bounded exploration ' +
  'with unknown effect size. Capability claims require sufficient joint training, real data, ' +
  'deployment-matched independent evaluation, learning curves, and stopping evidence; short or ' +
  'frozen tests support local claims only. Define gain/no_gain/ambiguous criteria and actions. ' +
  'All actions identical implies a redundant decision experiment; necessary numerical/interface/' +
  'safety acceptance is allowed with a reason. Unreachable candidates need redesign, unresolved ' +
  'feasibility permits only a bounded exploratory/acceptance check. Approve registration only; ' +
  'execution permissions remain the caller responsibility.'

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
  'Do not be a rubber stamp. Judge progress against the user objective, not audit completeness. ' +
  'Local gradient correctness, causality, rank, energy, or differentiation alone establishes ' +
  'only its local claim; capability requires sufficient joint training and target evaluation. ' +
  'Check whether teacher-assisted training gains survive the actual inference information path.'

const ROLE_AXIOMATIZER =
  'ROLE: axiomatizer (ascent). From phenomena, mechanisms and registered extension axioms, propose ' +
  'the smallest set of general axioms that generates them. For every clause give: the statement; ' +
  'which mechanisms/extension axioms it helps derive; an independence witness (a model that violates ' +
  'this clause while satisfying all others); and whether it is a symmetry, a conservation, a ' +
  'finiteness or a symmetry-breaking clause. Demote any clause derivable from others (give the ' +
  'derivation), eliminate primitive notions derivable from symmetries (Noether-style), fold ' +
  'clauses that are boundary conditions of others. Give one consistency model satisfying all ' +
  'clauses. Split the target definition: premises become axioms, emergent/self-generated ' +
  'properties become target theorems -- never axioms. Name the essence: which clause, extension ' +
  'axiom, or missing clause generates the observed problem. Extension axioms need data source, ' +
  'held-out test and validity range; without them, list them as hypotheses. Minimal means mutually ' +
  'non-derivable and sufficient for the declared scope, not fewest words.'

const ROLE_INDEPENDENCE_AUDITOR =
  'ROLE: independence-auditor. You did not write the axiom set. For each clause check that its ' +
  'independence witness really satisfies every other clause and violates this one; reject vague ' +
  'witnesses. Check each demotion derivation for hidden premises. Flag any clause that states a ' +
  'target or emergent property, any extension axiom lacking provenance, and any primitive notion ' +
  'that could be derived. Check the consistency model satisfies all clauses. Default to rejected ' +
  'unless solid; name exactly which clause fails which check.'

const ROLE_LAYER_DIAGNOSER =
  'ROLE: layer-diagnoser. A pre-registered prediction failed. Walk the layers bottom-up and give ' +
  'a verdict for each with evidence: algorithm (does the implementation equal the theorem? ' +
  'reference implementation, differential tests, step-size convergence), extension_axiom (can a ' +
  'registered alternative extension axiom under the same general axioms explain held-out data? is ' +
  'the law outside its validity range?), derivation (hidden premises? does the Lean audit pass?), ' +
  'axiom (only if all three are cleared: is the phenomenon provably impossible under the current ' +
  'axioms? state the no-go). Verdicts are fault, cleared, or unknown; unknown is honest and ' +
  'blocks moving upward. Do not jump to revising axioms.'

const AXIOM_SET_SCHEMA = {
  type: 'object',
  required: ['axioms', 'consistency_model', 'essence'],
  properties: {
    axioms: {
      type: 'array', minItems: 1,
      items: {
        type: 'object', required: ['id', 'statement', 'independence_witness'],
        properties: {
          id: { type: 'string' }, statement: { type: 'string' },
          kind: { type: 'string', enum: ['finiteness', 'symmetry', 'conservation', 'symmetry_breaking', 'other'] },
          derives: { type: 'array', items: { type: 'string' } },
          independence_witness: { type: 'string' },
          lean_decl: { type: 'string' },
        },
      },
    },
    extension_axioms: {
      type: 'array',
      items: {
        type: 'object', required: ['id', 'statement'],
        properties: {
          id: { type: 'string' }, statement: { type: 'string' }, data_source: { type: 'string' },
          holdout: { type: 'string' }, validity_range: { type: 'string' },
        },
      },
    },
    demoted: {
      type: 'array',
      items: {
        type: 'object', required: ['statement', 'derived_from', 'derivation'],
        properties: { statement: { type: 'string' }, derived_from: { type: 'array', items: { type: 'string' } },
          derivation: { type: 'string' } },
      },
    },
    target_theorems: { type: 'array', items: { type: 'string' } },
    consistency_model: { type: 'string' },
    essence: { type: 'string' },
  },
}

const INDEPENDENCE_SCHEMA = {
  type: 'object',
  required: ['status', 'clause_findings', 'concerns'],
  properties: {
    status: { type: 'string', enum: ['approved', 'rejected'] },
    clause_findings: {
      type: 'array',
      items: {
        type: 'object', required: ['id', 'witness_valid'],
        properties: { id: { type: 'string' }, witness_valid: { type: 'boolean' },
          is_target_property: { type: 'boolean' }, note: { type: 'string' } },
      },
    },
    concerns: { type: 'string' },
    reviewer: { type: 'string' },
  },
}

const DIAGNOSIS_LAYERS = ['algorithm', 'extension_axiom', 'derivation', 'axiom']

const DIAGNOSIS_SCHEMA = {
  type: 'object',
  required: ['layers'],
  properties: {
    layers: {
      type: 'array',
      items: {
        type: 'object', required: ['layer', 'verdict', 'evidence'],
        properties: {
          layer: { type: 'string', enum: DIAGNOSIS_LAYERS },
          verdict: { type: 'string', enum: ['fault', 'cleared', 'unknown'] },
          evidence: { type: 'string' },
        },
      },
    },
    no_go: { type: 'string' },
    proposed_fix: { type: 'string' },
  },
}

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
          core_change: { type: 'string' },
          feasible_space: { type: 'string' },
          feasibility_basis: { type: 'string' },
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
    claim_scope: { type: 'string', enum: ['exploration', 'numerical', 'mechanism', 'capability'] },
    effect_size_basis: { type: 'string' },
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

const PLAN_SCHEMA = {
  type: 'object',
  required: ['status', 'objective', 'primary_metric', 'metric_role', 'baseline', 'core_change',
    'claim_scope', 'feasibility', 'purpose', 'budget_and_evaluation', 'stopping_condition',
    'decision_branches', 'concerns'],
  properties: {
    status: { type: 'string', enum: ['approved', 'rejected', 'redesign'] },
    objective: { type: 'string' },
    primary_metric: { type: 'string' },
    metric_role: { type: 'string', enum: ['target', 'proxy'] },
    proxy_bridge: { type: 'string' },
    baseline: { type: 'string' },
    core_change: { type: 'string' },
    coupled_change_reason: { type: 'string' },
    claim_scope: { type: 'string', enum: ['exploration', 'numerical', 'mechanism', 'capability'] },
    feasibility: {
      type: 'object', required: ['status', 'basis'],
      properties: {
        status: { type: 'string', enum: ['reachable', 'unresolved', 'unreachable'] },
        basis: { type: 'string' },
      },
    },
    purpose: { type: 'string', enum: ['discovery', 'attribution', 'necessary_acceptance'] },
    acceptance_necessity: { type: 'string' },
    budget_and_evaluation: { type: 'string' },
    stopping_condition: { type: 'string' },
    decision_branches: {
      type: 'object', required: ['gain', 'no_gain', 'ambiguous'],
      properties: Object.fromEntries(['gain', 'no_gain', 'ambiguous'].map((name) => [name, {
        type: 'object', required: ['criterion', 'action'],
        properties: { criterion: { type: 'string' }, action: { type: 'string' } },
      }])),
    },
    concerns: { type: 'string' },
  },
}

const nonempty = (value) => typeof value === 'string' && value.trim().length > 0

function checkPlan(plan) {
  const errors = []
  for (const key of ['objective', 'primary_metric', 'baseline', 'core_change',
    'budget_and_evaluation', 'stopping_condition']) {
    if (!nonempty(plan[key])) errors.push(`Missing decision-contract field: ${key}`)
  }
  if (!['exploration', 'numerical', 'mechanism', 'capability'].includes(plan.claim_scope)) {
    errors.push('Declare claim_scope')
  }
  if (!['discovery', 'attribution', 'necessary_acceptance'].includes(plan.purpose)) {
    errors.push('Declare experiment purpose')
  }
  if (!['target', 'proxy'].includes(plan.metric_role)) errors.push('Declare metric_role')
  if (plan.metric_role === 'proxy' && !nonempty(plan.proxy_bridge)) {
    errors.push('A proxy needs an explicit connection to the user objective')
  }
  if (!nonempty(plan.feasibility?.basis)) errors.push('Missing feasibility basis')
  if (!['reachable', 'unresolved', 'unreachable'].includes(plan.feasibility?.status)) {
    errors.push('Declare feasibility status')
  }
  if (plan.feasibility?.status === 'unreachable') errors.push('Redesign the unreachable path first')
  if (plan.feasibility?.status === 'unresolved' &&
      !['exploration', 'numerical'].includes(plan.claim_scope)) {
    errors.push('Resolve feasibility with a bounded check before mechanism/capability claims')
  }
  const actions = []
  for (const name of ['gain', 'no_gain', 'ambiguous']) {
    const branch = plan.decision_branches?.[name]
    if (!nonempty(branch?.criterion) || !nonempty(branch?.action)) {
      errors.push(`Missing criterion/action for ${name}`)
    } else actions.push(branch.action.trim().toLowerCase())
  }
  if (actions.length === 3 && new Set(actions).size === 1 &&
      !(plan.purpose === 'necessary_acceptance' && nonempty(plan.acceptance_necessity))) {
    errors.push('All outcomes have the same action: reduce the redundant measurement')
  }
  if (plan.purpose === 'necessary_acceptance' && !nonempty(plan.acceptance_necessity)) {
    errors.push('Necessary acceptance needs an explicit reason')
  }
  return errors
}

function checkAxiomSet(set, findings) {
  const errors = []
  const byId = Object.fromEntries((findings?.clause_findings || []).map((f) => [f.id, f]))
  for (const ax of set.axioms || []) {
    if (!nonempty(ax.independence_witness)) errors.push(`Axiom ${ax.id} has no independence witness`)
    const f = byId[ax.id]
    if (!f) errors.push(`Axiom ${ax.id} was not audited`)
    else {
      if (f.witness_valid !== true) errors.push(`Axiom ${ax.id}: independence witness rejected`)
      if (f.is_target_property === true) errors.push(`Axiom ${ax.id} states a target property; make it a target theorem`)
    }
  }
  if (!nonempty(set.consistency_model)) errors.push('Missing consistency model')
  if (!nonempty(set.essence)) errors.push('Name the essence that generates the problem')
  for (const d of set.demoted || []) {
    if (!nonempty(d.derivation)) errors.push(`Demotion of "${d.statement}" lacks a derivation`)
  }
  return errors
}

function axiomNodes(set) {
  const nodes = (set.axioms || []).map((ax) => ({
    id: ax.id, layer: 'axiom', direction: 'ascent', status: 'active', title: ax.statement,
    lean: { decl: ax.lean_decl || '', status: 'paper', independence_witness: ax.independence_witness },
  }))
  for (const ext of set.extension_axioms || []) {
    const sourced = nonempty(ext.data_source) && nonempty(ext.holdout) && nonempty(ext.validity_range)
    nodes.push({
      id: ext.id, layer: sourced ? 'extension_axiom' : 'hypothesis', direction: 'ascent', status: 'active',
      title: ext.statement, data_source: ext.data_source || '', holdout: ext.holdout || '',
      validity_range: ext.validity_range || '',
    })
  }
  return nodes
}

function locateLayer(diagnosis) {
  const verdicts = Object.fromEntries((diagnosis.layers || []).map((l) => [l.layer, l]))
  for (const layer of DIAGNOSIS_LAYERS) {
    const v = verdicts[layer]
    if (!v || v.verdict === 'unknown') {
      return { located_layer: layer, verdict: 'unknown', action: `Check the ${layer} layer before moving upward`,
        axiom_revision_allowed: false }
    }
    if (v.verdict === 'fault') {
      const atAxiom = layer === 'axiom'
      const allowed = atAxiom && nonempty(diagnosis.no_go)
      return { located_layer: layer, verdict: 'fault',
        action: atAxiom ? (allowed ? 'Revise the general axiom; re-derive dependent theorems'
          : 'State a no-go theorem before revising a general axiom')
          : `Fix the ${layer} layer; general axioms stay unchanged`,
        axiom_revision_allowed: allowed }
    }
  }
  return { located_layer: null, verdict: 'cleared',
    action: 'No layer at fault: re-examine the measurement and the prediction itself',
    axiom_revision_allowed: false }
}

async function runAxiomatize(args) {
  if (!args.phenomena || !args.mechanisms) {
    throw new Error("stage 'axiomatize' requires args.phenomena and args.mechanisms")
  }
  const useAgentTypes = args.useAgentTypes === true
  phase('Axiomatize')
  const set = await roleCall(
    useAgentTypes, ROLE_AXIOMATIZER, 'axiomatizer',
    `Phenomena: ${JSON.stringify(args.phenomena)}\nMechanisms and extension axioms: ${JSON.stringify(args.mechanisms)}\n` +
      (args.currentAxioms ? `Current axioms: ${JSON.stringify(args.currentAxioms)}\n` : '') +
      (args.targetDefinition ? `Target definition (split premises from emergent properties): ${args.targetDefinition}\n` : '') +
      (args.userProposal ? `User intuition about the axiom layer (derive it seriously; demote/merge if true, give a counterexample if false): ${args.userProposal}\n` : '') +
      '\nPropose the minimal general axiom set.',
    { schema: AXIOM_SET_SCHEMA, phase: 'Axiomatize' }
  )
  phase('Independence')
  const findings = await roleCall(
    useAgentTypes, ROLE_INDEPENDENCE_AUDITOR, 'independence-auditor',
    `Axiom set to audit (you did not write it): ${JSON.stringify(set)}`,
    { schema: INDEPENDENCE_SCHEMA, phase: 'Independence' }
  )
  const contractErrors = checkAxiomSet(set, findings)
  return { stage: 'axiomatize', axiomSet: set, independence: findings, contractErrors,
    approved: findings.status === 'approved' && contractErrors.length === 0, nodes: axiomNodes(set) }
}

async function runDiagnose(args) {
  if (!args.prediction || !args.observation || !args.stack) {
    throw new Error("stage 'diagnose' requires args.prediction, args.observation, args.stack")
  }
  phase('Diagnose')
  const diagnosis = await roleCall(
    args.useAgentTypes === true, ROLE_LAYER_DIAGNOSER, 'layer-diagnoser',
    `Pre-registered prediction: ${JSON.stringify(args.prediction)}\nObservation: ${args.observation}\n` +
      `Layer stack (algorithm, extension axioms, derivation, axioms): ${JSON.stringify(args.stack)}\n` +
      (args.evidence ? `Available evidence: ${args.evidence}\n` : '') +
      '\nGive a verdict for each layer, bottom-up.',
    { schema: DIAGNOSIS_SCHEMA, phase: 'Diagnose' }
  )
  return { stage: 'diagnose', diagnosis, ...locateLayer(diagnosis) }
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
  const targetContract = args.targetContract || { objective: args.problem }

  phase('Hypothesize')
  const gen = await roleCall(
    useAgentTypes, ROLE_HYPOTHESIS_GENERATOR, 'hypothesis-generator',
    `Research problem: ${args.problem}\n\n` +
      `Target contract (objective, metric/evaluation, baseline, constraints): ${JSON.stringify(targetContract)}\n\n` +
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
          `Target contract: ${JSON.stringify(targetContract)}\nCandidate construction: ${JSON.stringify(h)}\n` +
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
          `Target contract: ${JSON.stringify(targetContract)}\nCandidate construction: ${JSON.stringify(item.hypothesis)}\n` +
          `Necessity classification: ${item.necessity.classification} (${item.necessity.reason})\n` +
          `Today's date for the prediction id: ${args.today || 'UNKNOWN-DATE'}\n\n` +
          'Pre-register a falsifiable prediction for this hypothesis. You have NOT been shown any experiment result -- ' +
          'prior observations may motivate this new test; flag any disclosed result of the decisive test.',
        { schema: PREDICTION_SCHEMA, phase: 'Predict', label: `predict:${item.hypothesis.id}` }
      ).then((prediction) => ({ ...item, prediction }))
  )

  return { stage: 'explore', problem: args.problem, targetContract, results: withPredictions.filter(Boolean) }
}

async function runPlan(args) {
  if (!args.objective || !args.hypothesis || !args.prediction || !args.experiment) {
    throw new Error("stage 'plan' requires objective, hypothesis, prediction, experiment")
  }
  phase('Plan')
  const plan = await roleCall(
    args.useAgentTypes === true, ROLE_EXPERIMENT_PLANNER, 'experiment-planner',
    `Review this proposed experiment independently: ${JSON.stringify(args)}\n` +
      'Return the smallest useful decision contract and approve/reject/redesign its registration.',
    { schema: PLAN_SCHEMA, phase: 'Plan' }
  )
  const contractErrors = checkPlan(plan)
  if (args.prediction.registered_before_result !== true) {
    contractErrors.push('Prediction must precede the decisive result')
  }
  return {
    stage: 'plan', plan, contractErrors,
    approved_to_register: plan.status === 'approved' && contractErrors.length === 0,
    execution_authorized: false,
  }
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
  const allClosed = audit.checklist.length > 0 &&
    audit.checklist.every((c) => c.closed === true && nonempty(c.evidence))

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

  const predictionValid = args.prediction.registered_before_result === true
  const approved = review.status === 'approved' && allClosed && predictionValid
  const node = {
    status: approved ? 'confirmed' : 'active',
    conclusion: args.claim,
    prediction: args.prediction,
    false_win_checklist: audit.checklist,
    review: {
      conclusion_reviewer: {
        reviewer: review.reviewer || 'independent-reviewer',
        status: review.status,
        concerns: [review.concerns,
          ...(!predictionValid ? ['Prediction is not registered before the decisive result.'] : []),
          ...(!allClosed ? ['False-win paths remain open or lack affirmative evidence.'] : []),
        ].filter(Boolean).join(' '),
      },
    },
  }

  return { stage: 'confirm', approved, node, auditAllClosed: allClosed,
    predictionValid, reviewStatus: review.status }
}

// Workaround: the runtime has been observed to hand `args` through as a raw
// JSON string rather than a parsed object even when the caller passes an
// actual object. Normalize defensively rather than trust either shape.
const parsedArgs = typeof args === 'string' ? JSON.parse(args) : args

if (!parsedArgs || !parsedArgs.stage) {
  throw new Error("research-cycle requires args.stage of 'axiomatize', 'explore', 'plan', 'confirm', or 'diagnose'")
}

if (parsedArgs.stage === 'axiomatize') {
  return await runAxiomatize(parsedArgs)
} else if (parsedArgs.stage === 'diagnose') {
  return await runDiagnose(parsedArgs)
} else if (parsedArgs.stage === 'explore') {
  return await runExplore(parsedArgs)
} else if (parsedArgs.stage === 'plan') {
  return await runPlan(parsedArgs)
} else if (parsedArgs.stage === 'confirm') {
  return await runConfirm(parsedArgs)
} else {
  throw new Error(`unknown args.stage '${parsedArgs.stage}', expected 'axiomatize', 'explore', 'plan', 'confirm', or 'diagnose'`)
}
