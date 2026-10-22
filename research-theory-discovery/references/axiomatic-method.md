# Axiomatic method: ascent and descent

Expands sections 1-6 of `SKILL.md`. The Chinese version (`../../research-theory-discovery-zh/references/axiomatic-method.zh.md`) contains the full worked example.

## Why an axiom system instead of "first principles"

"First principles" is an attitude; an axiom system is a production line with rules: a few statements are accepted, and everything else must be derived from them. That makes claims **auditable** (each mechanism traces to its axioms, hidden assumptions surface in Lean), failures **diagnosable** (algorithm, extension axiom, derivation, or general axiom), and results **transferable** (change extension axioms or parameters, keep the derivations).

## Two historical examples

- **Euclid to Hilbert.** Five postulates gave 465 propositions. The parallel postulate proved independent: replacing it yields non-Euclidean geometry, which is the archetype of an independence witness. In 1899 Hilbert found unstated assumptions in Euclid (circle intersection, betweenness) and made them explicit axioms, the role Lean plays today.
- **Newton.**
  - Ascent: Tycho's data, then Kepler's laws (extension-axiom level), then Newton's laws plus gravitation.
  - Descent: Kepler's laws derived back; new phenomena predicted.
  - Diagnosis: Uranus pointed to the extension/data layer and Neptune was found. Mercury, after the "Vulcan" patch failed, pointed to the axiom layer and led to relativity.

## Ascent criteria

- **Promote a law to an extension axiom** only with a data source (which data, which version), a held-out test, and a validity range. Otherwise it is a hypothesis H.
- **From extension axioms to general axioms**, ask:
  - which more general constraint has this law as a special case;
  - whether two laws follow from one constraint;
  - whether a primitive notion follows from symmetry. Baez–Fong Noether for Markov processes: an observable commutes with the generator iff its mean and second moment are conserved for all initial states. Time-reversal symmetry plus Kolmogorov's criterion yields an energy function;
  - whether a constraint is really a boundary condition of another (openness for conservation; external drive as broken time-translation symmetry).
- **Independence and consistency.** Build, for each axiom, a model violating it while satisfying the rest. For example, a one-way 3-cycle A→B→C→A is conservative, local and finite yet runs a perpetual cycle, so "no perpetual motion" needs time-reversal symmetry. Then build one model satisfying all axioms.
- **Definitions.** Split the target definition: premises become axioms; emergent properties become target theorems or an existence conjecture.
- **Parameters.** Numbers are parameters (for example, genome-to-wiring information ratio: fly about 0.3-5, human about 1e-6 to 1e-7). They stay out of the axioms; changing them does not trigger diagnosis.

## Descent criteria

- **Derivation**: theorem statements list the clauses used; label each "Lean-proved" or "paper".
- **Algorithms**: computable Lean reference with proved properties; production code differentially tested; floating-point gap reported; resource limits from the target contract respected.
- **Tests**: pre-register, design decisive experiments, close false-win paths; results become new phenomena.

## Diagnosis order (bottom-up)

| Step | Layer | Typical checks |
|---|---|---|
| 1 | Algorithm | differential tests against the Lean reference; step-size convergence; does the code implement the theorem object |
| 2 | Extension axiom | can a registered alternative explain held-out data; is the law outside its validity range |
| 3 | Derivation | undeclared premises; Lean audit |
| 4 | General axiom | a no-go theorem first, then revise |

## Lean organization

See `../../harness/lean/README.md` and the compilable example in `../../harness/lean/example/`.
