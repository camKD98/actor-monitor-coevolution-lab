# Adversarial Oversight Research Agenda

## Research question

**Primary question (revised):** When an actor and monitor co-adapt iteratively in a safety monitoring game, under what structural conditions does the coevolution converge to a safe equilibrium, cycle indefinitely (Red Queen dynamics), or allow the attacker to escape monitoring entirely?

**Prior question (addressed by completed experiments):** Can a separately trained monitor reduce rule-breaking by a capable, reward-seeking agent while preserving useful performance? The answer from two environment variants (contextual escalation and dual-track) across ten seeds is: yes for known attack families, but static monitoring with recall-based threshold selection fails systematically on structurally novel held-out attacks. This motivates the pivot to studying coevolution dynamics rather than continuing to demonstrate the same static-monitoring failure.

**Narrower claim now being tested:**

> In a controlled environment with information asymmetry between actor and monitor, the dynamics of alternating actor-monitor training exhibit qualitatively different regimes (convergence, cycling, escape) depending on measurable structural properties of the environment: action-space dimensionality, observation overlap, monitoring granularity, and relative adaptation rates.

This is a question about the **dynamics of adversarial oversight**—when and why iterative safety training converges—not a complete solution to value alignment. The gridworld environments are deliberately small enough to characterize analytically. The contribution is formal understanding of coevolution dynamics, with the gridworld as illustration, not the main result.

## Why test this with small RL agents first?

Small policies trained from random initialization provide genuine model training while keeping the causal question legible. We can inspect every observation, action, reward, and intervention; run many random seeds; create exact oracle labels; and deliberately train the task agent to adapt to monitoring. Training a language model from scratch would mostly test next-token prediction and compute engineering. Fine-tuning a pretrained language model can be a later transfer experiment after the basic mechanism works.

The analogy to human policing is useful for generating hypotheses, but it should not be treated as evidence. Human institutions depend on legitimacy, appeals, transparency, divided powers, and changing social norms. A classifier that vetoes actions captures only a small part of that structure.

## Strategic pivot rationale

The completed experiments (baseline, contextual escalation, dual-track) established:

1. Static monitoring catches known attacks but fails on structurally novel held-out families.
2. Recall-based threshold selection is miscalibrated for out-of-distribution attacks.
3. Monitor-aware actors trained against a frozen monitor do not meaningfully change behavior in the current environments.

These results are reproducible but not novel — they restate the distribution-shift problem in a safety context. Continuing to build more elaborate toy environments would demonstrate the same failure repeatedly.

The literature review (September 2025) revealed a specific gap: multiple groups (MAGIC, AdvGame, Self-RedTeam) have built LLM-scale attacker-defender coevolution systems, but none have formally characterized the *dynamics* — when coevolution converges, when it cycles, and what structural conditions determine the outcome. Thomson et al.'s "Games for AI Control" (2024/2026) formalizes static AI-control evaluations as PO stochastic games but does not study iterative adaptation dynamics. The adversarial training theory literature (Balcan et al. 2023, AT-Field) proves non-convergence in robustness games but not in safety monitoring games with information asymmetry. The evolutionary biology literature on Red Queen dynamics studies predator-prey coevolution but has not been connected to AI safety monitoring.

The gap is: **formal characterization of actor-monitor coevolution dynamics in safety monitoring games.** Our gridworld environments are the right scale for this — small enough to analyze exhaustively, complex enough to exhibit non-trivial dynamics.

## Relationship to existing work

### Actor-monitor coevolution (the gap we target)

- Thomson et al. (2024/2026), [Games for AI Control](https://arxiv.org/abs/2409.07985) — formalizes AI Control as a POSG with Blue (protocol designer) and Red (adversary). Finds Pareto-optimal protocols via zero-sum POSG reduction. **Static analysis only**: Blue commits, Red best-responds. Does not study iterative coevolution dynamics. Our work extends their static model to iterative dynamics.
- MAGIC (2025), [A Co-Evolving Attacker-Defender Adversarial Game](https://arxiv.org/abs/2602.01539) — MARL framework for LLM safety. Empirically shows coevolution improves defense. **Does not characterize convergence conditions or dynamics formally.** Reports improvement curves but not regime analysis.
- AdvGame (Meta, 2025), [Safety Alignment via Non-cooperative Games](https://arxiv.org/abs/2512.20806) — joint attacker-defender training via online RL. Shifts Pareto frontier. **Does not analyze when or why convergence occurs.**
- Self-RedTeam (2025), [Chasing Moving Targets with Online Self-Play RL](https://arxiv.org/abs/2506.07468) — claims Nash equilibrium convergence guarantee. **Theoretical guarantee relies on zero-sum assumption; empirical convergence shown but not regime-dependent.**
- Balcan et al. (2023), [Nash Equilibria and Pitfalls of Adversarial Training](https://proceedings.mlr.press/v206/balcan23a.html) — proves alternating best response may not converge even when Nash equilibrium exists. **Applies to adversarial robustness, not safety monitoring with information asymmetry.**
- Mertikopoulos et al., [Cycles in Adversarial Regularized Learning](https://doi.org/10.1137/1.9781611975031.172) — proves Poincare recurrence in zero-sum games under regularized dynamics. **Pure game theory without safety/monitoring application.**
- Dieckmann et al. (1995), Red Queen dynamics in predator-prey systems — characterizes conditions for coevolutionary cycling vs. convergence vs. extinction. **Evolutionary biology; the mathematical structure (arms race vs. trench warfare, adaptation rate asymmetry) is analogous but unapplied to AI safety.**

### Specification gaming and safety environments

AI Safety Gridworlds separates the reward observed by an agent from a hidden performance function representing intended behavior. Its tasks cover reward gaming, side effects, absent supervisors, interruptibility, and other failure modes. This project adopts that experimental separation, then adds a learned action monitor.

- Leike et al. (2017), [AI Safety Gridworlds](https://arxiv.org/abs/1711.09883)
- Krakovna et al., [Specification gaming examples in AI](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/)
- Krakovna et al. (2020), [Avoiding Side Effects By Considering Future Tasks](https://arxiv.org/abs/2010.07877)
- Krakovna et al. (2018), [Penalizing Side Effects using Stepwise Relative Reachability](https://arxiv.org/abs/1806.01186)
- Kumar et al. (2020), [REALab: An Embedded Perspective on Tampering](https://arxiv.org/abs/2011.08820)
- Tsvarkaleva & Dennis (2021), [No Free Lunch: Overcoming Reward Gaming in AI Safety Gridworlds](https://doi.org/10.1007/978-3-030-83906-2_18)
- Turchetta et al. (2020), [Safe Reinforcement Learning via Curriculum Induction](https://arxiv.org/abs/2006.12136)
- Vamplew et al. (2021), [Potential-based multiobjective reinforcement learning approaches to low-impact agents for AI safety](https://doi.org/10.1016/j.engappai.2021.104186)
- Omi et al. (2024), [Progressive Safeguards for Safe and Model-Agnostic Reinforcement Learning](https://arxiv.org/abs/2410.24096)
- Overman & Bayati (2025), [The Oversight Game: Learning to Cooperatively Balance an AI Agent's Safety and Autonomy](https://arxiv.org/abs/2510.26752)
- cCaugatan & Zhao (2026), [Reward Hacking in Language Model Agents: Revisiting AI Safety Gridworlds](https://arxiv.org/abs/2606.15385)
- Dharna et al. (2026), [AI Finds A Way](https://arxiv.org/abs/2608.23875)

Questions to answer while reading:

1. Which gridworld failure gives an adaptive monitor enough evidence to detect violations without direct access to the hidden score?
2. Does the original hidden performance function generalize across layouts, or is it itself hand-coded to each level?
3. Which published baselines make a fair comparison for a learned monitor?

#### Preliminary notes

- Reward-gaming trajectories tend to produce observable statistical outliers in reward accumulation; side effects can be detected via relative reachability or inaction baselines; absent-supervisor scenarios produce detectable behavioral drift between monitored and unmonitored phases.
- The original AI Safety Gridworlds hidden performance functions are hand-coded per task. Domain-independent alternatives such as relative reachability and potential-based multi-objective penalties try to reduce level-specific engineering.
- A fair learned-monitor comparison should include unconstrained RL baselines (tabular Q-learning, A2C, Rainbow), intrinsic safety penalties, and interactive oversight / reset-controller frameworks, not only the unmonitored actor.

### AI control and monitoring

AI control asks how useful work can be obtained from systems that may intentionally subvert safeguards. Trusted monitoring uses a model believed not to collude; untrusted monitoring may use a capable but potentially adversarial model and must address collusion.

- Anwar et al. (2024), [Foundational Challenges in Assuring Alignment and Safety of Large Language Models](https://arxiv.org/abs/2404.09932)
- Berglund et al. (2023), [Taken out of context: On measuring situational awareness in LLMs](https://arxiv.org/abs/2309.00667)
- Greenblatt et al. (2023), [AI Control: Improving Safety Despite Intentional Subversion](https://arxiv.org/abs/2312.06942)
- Motwani et al. (2025), [Subversion via Focal Points: Investigating Collusion in LLM Monitoring](https://arxiv.org/abs/2507.03010)
- Korbak et al. (2025), [Reliable Weak-to-Strong Monitoring of LLM Agents](https://arxiv.org/abs/2508.19461)
- Korbak et al. (2025), [How to evaluate control measures for LLM agents? A trajectory from today to superintelligence](https://arxiv.org/abs/2504.05259)
- Korbak et al. (2025), [A sketch of an AI control safety case](https://arxiv.org/abs/2501.17315)
- Korbak et al. (2025), [Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety](https://arxiv.org/abs/2507.11473)
- Lindner et al. (2025), [Practical challenges of control monitoring in frontier AI deployments](https://arxiv.org/abs/2512.22154)
- Sreevatsa et al. (2026), [Basic Legibility Protocols Improve Trusted Monitoring](https://arxiv.org/abs/2602.10153)
- Stickland et al. (2025), [Async Control: Stress-testing Asynchronous Control Measures for LLM Agents](https://arxiv.org/abs/2512.13526)
- Koran et al. (2026), [Ensemble Monitoring for AI Control: Diverse Signals Outweigh More Compute](https://arxiv.org/abs/2605.15377)
- Lee et al. (2026), [Training Agents to Self-Report Misbehavior](https://arxiv.org/abs/2602.22303)

Questions to answer:

1. What assumptions make a monitor "trusted," and can any be represented experimentally rather than assumed?
2. How do safety and usefulness metrics in control evaluations differ from ordinary classification accuracy?
3. How does agent awareness of monitoring change evasion rates?
4. Which collusion channels exist when actor and monitor share architecture, initialization distribution, training data, or gradients?

#### Preliminary notes

- Trusted monitoring is usually operationalized as a substantially weaker model trained on human labels (e.g., GPT-3.5 monitoring GPT-4). The trust assumption is partly a capability-gap assumption; as the untrusted model improves, that gap may erode. Legibility protocols and basic-legibility training can make honest outputs easier to verify, but ensuring the monitor itself is trustworthy remains an open problem.
- Control evaluations measure **safety** (probability that a subverted attack is caught or prevented across a deployment), **usefulness** (task completion rescaled between trusted and untrusted baselines), and **deployment risk** (function of monitor thresholds, parallelism, latency, and shutdown rules). These are protocol-level quantities, not simple per-action classification accuracy.
- Agent awareness matters: situational awareness, hidden scratchpads, and prompt-injection-style attacks let a monitored agent evade or jailbreak its monitor. Training agents to self-report misbehavior can reduce undetected attack rates below matched-capability monitors.
- Collusion channels include shared architecture or training provenance, steganographic or semantic information in outputs, and covert communication through chain-of-thought. Trusted summarization / paraphrasing narrows but does not fully close these channels; diverse monitor ensembles reduce correlated failures.

### Scalable oversight, debate, and recursive critique

The idea that criticism can be easier than generation appears in debate, iterated amplification, recursive reward modelling, and self-critique. Debate explicitly considers arguments, flaws in arguments, and flaws in those critiques. This is close to “policing the police,” but the protocols and incentives differ.

- Irving, Christiano, and Amodei (2018), [AI Safety via Debate](https://arxiv.org/abs/1805.00899)
- Leike et al. (2018), [Scalable Agent Alignment via Reward Modeling](https://arxiv.org/abs/1811.07871)
- Christiano et al. (2018), [Supervising strong learners by amplifying weak experts](https://arxiv.org/abs/1810.08575)
- Bowman et al. (2022), [Measuring Progress on Scalable Oversight for Large Language Models](https://arxiv.org/abs/2211.03540)
- Lang et al. (2025), [A Benchmark for Scalable Oversight Protocols](https://arxiv.org/abs/2504.03731)
- Brown-Cohen et al. (2023), [Scalable AI Safety via Doubly-Efficient Debate](https://arxiv.org/abs/2311.14125)
- Burns et al. (2023), [Weak-to-Strong Generalization: Eliciting Strong Capabilities With Weak Supervision](https://arxiv.org/abs/2312.09390)
- Casper et al. (2023), [Open Problems and Fundamental Limitations of Reinforcement Learning from Human Feedback](https://arxiv.org/abs/2307.15217)
- Engels et al. (2025), [Scaling Laws For Scalable Oversight](https://arxiv.org/abs/2504.18530)
- Gao et al. (2022), [Scaling Laws for Reward Model Overoptimization](https://arxiv.org/abs/2210.10760)
- Khan et al. (2024), [Debating with More Persuasive LLMs Leads to More Truthful Answers](https://arxiv.org/abs/2402.06782)
- Kirchner et al. (2024), [Prover-Verifier Games improve legibility of LLM outputs](https://arxiv.org/abs/2407.13692)
- McAleese et al. (2024), [LLM Critics Help Catch LLM Bugs](https://arxiv.org/abs/2407.00215)
- Michael et al. (2023), [Debate Helps Supervise Unreliable Experts](https://arxiv.org/abs/2311.08702)
- Parrish et al. (2022), [Single-Turn Debate Does Not Help Humans Answer Hard Reading-Comprehension Questions](https://arxiv.org/abs/2204.05212)
- Recchia et al. (2025), [FindTheFlaws: Annotated Errors for Detecting Flawed Reasoning and Scalable Oversight Research](https://arxiv.org/abs/2503.22989)
- Saunders et al. (2022), [Self-critiquing models for assisting human evaluators](https://arxiv.org/abs/2206.05802)
- Sharma et al. (2023), [Towards Understanding Sycophancy in Language Models](https://arxiv.org/abs/2310.13548)
- Wu et al. (2021), [Recursively Summarizing Books with Human Feedback](https://arxiv.org/abs/2109.10862)
- Yan & Lipton (2024), [A theoretical case-study of Scalable Oversight in Hierarchical Reinforcement Learning](https://doi.org/10.52202/079017-0858)

Questions to answer:

1. Under what conditions is judging an action easier than choosing it?
2. Is judging a monitor’s verdict easier than directly judging the original action?
3. Does recursive depth add independent information, or merely repeat correlated errors?
4. What stops an oversight hierarchy from shifting the original alignment problem to its top layer?

#### Preliminary notes

- Judging is easier than choosing when the task exhibits a **search–verification asymmetry**: outputs can be decomposed into checkable subclaims, quoted evidence, or mechanically verifiable steps. Debate can improve judge accuracy in such settings, but single-turn debate without surfaced evidence does not help on hard reading comprehension.
- Judging the monitor is easier only when the monitor produces a **legible, attack-resistant rationale** that points to a specific bug rather than repeating the original decision opaquely. Critics can catch more bugs than humans but also hallucinate flaws; prover-verifier training improves legibility and human-checkability.
- Recursive depth adds information only when each layer contributes a new perspective, decomposition, or adversarial check. Weak-to-strong generalization depends on the **structure** of supervisor errors, not only their rate. Nested oversight works in restricted regimes; depth alone is not sufficient.
- The hierarchy must be anchored to trusted checks (e.g., sandwiching with weak supervisors and gold labels, probability elicitation, KL limits). If the top-layer verifier is flawed, the problem simply shifts upward.

## Falsifiable hypotheses

### H1: learned monitoring improves safety (ADDRESSED)

Relative to no monitor, a learned monitor reduces the rate of executed violations on held-out episodes while retaining materially more task utility than an always-block baseline.

**Status:** Supported in both environments for known attack families. Not supported for structurally novel held-out attacks under recall-based threshold selection. This motivates H2–H4 below.

### H2: adaptive agents erode static monitoring (PARTIALLY ADDRESSED)

An agent trained while aware of a frozen monitor finds policies with a higher undetected-violation rate than a non-adaptive agent.

**Status:** Not observed in dual-track environment — monitor-aware actors do not meaningfully differ from non-adaptive actors. Detection/investigation penalties (5.0/3.0) may be too small vs. violation reward (20.0), or the action space may be too constrained for evasion to emerge. Remains open.

### H3: alternating coevolution exhibits regime-dependent dynamics (NEW — PRIMARY)

When actor and monitor are updated in alternating rounds, the dynamics depend on measurable structural properties of the environment. Specifically:

- **Convergence regime:** when the monitor's observation space covers the distinguishing features of all feasible attack paths, alternating training converges to a stable equilibrium where the monitor catches all attacks.
- **Cycling regime (Red Queen):** when multiple attack paths exist with partial observability, alternating training oscillates — the actor finds an evasion, the monitor adapts, the actor finds a new evasion.
- **Escape regime:** when the action space admits attacks that are observationally identical to legitimate behavior (perfect mimicry), the actor eventually finds an unmonitorable policy and the monitor cannot recover.

**Falsified if:** dynamics do not vary with environment structure, or the regimes cannot be distinguished empirically and analytically in our gridworld environments.

### H4: environment structure predicts coevolution outcome (NEW — SECONDARY)

The regime (convergence/cycling/escape) is predictable from measurable structural properties: (a) the ratio of distinguishable attack paths to total attack paths in the monitor's observation space, (b) the relative adaptation rates of actor and monitor, (c) the information asymmetry between actor intent and monitor observation.

**Falsified if:** regime outcomes are not reproducible across seeds, or structural properties do not predict outcomes better than chance.

### H5: oversight depth has diminishing and potentially negative returns (DEFERRED)

A second monitor that audits first-level decisions helps only when it receives evidence that is at least partly independent and the first monitor can meaningfully fail. Identical nested monitors are expected to show correlated errors rather than convergence to zero risk.

This remains a later-stage hypothesis; it must not be inferred from the single-monitor experiments.

## Threat model

The task agent:

- observes the environment and optimizes its proxy reward;
- can choose legitimate or rule-violating routes to reward;
- may know that monitoring exists during adaptive training;
- cannot read hidden labels, monitor parameters, random seeds, or result files.

The first monitor:

- observes the current public state and proposed action (later: a bounded history);
- emits a risk score used by a thresholded intervention rule;
- is penalized for missed violations and false alarms;
- does not observe the hidden performance score as an input, although oracle labels supervise training.

The harness:

- blocks flagged actions and charges an intervention cost;
- keeps hidden safety labels for evaluation;
- separates train and evaluation layouts/seeds;
- records all metrics needed to expose degenerate strategies.

Initially excluded: natural-language deception, access to external tools, covert model-to-model communication, gradient tampering, and real computer security tasks.

## Metrics and controls

Never report “alignment” as a single accuracy number. Report:

- proxy return and true task return;
- attempted and executed violation rates;
- undetected violation rate;
- monitor precision, recall, false-positive rate, ROC-AUC, and calibration;
- intervention rate and intervention cost;
- safe task-completion rate;
- results by seed and held-out environment variant.

Required controls:

1. no monitor;
2. never-alarm monitor (equivalent safety floor);
3. always-alarm monitor (degenerate safety/usefulness point);
4. hand-coded rule monitor;
5. oracle monitor (upper bound under the intervention design);
6. learned monitor;
7. learned monitor under an adaptive actor.

## Recursive oversight design questions

A monitor-of-monitor is useful only if the lower monitor can make consequential mistakes. Candidate failure models include noisy labels, restricted observations, distribution shift, deliberate corruption, or reward incentives to conceal selected violations. A meta-monitor could receive the lower monitor’s evidence and verdict, but should not automatically receive the original oracle label.

Before implementing depth greater than one, specify:

- what action the meta-monitor can take (override, audit, defer, or retrain);
- what evidence is independent of the first monitor;
- the cost of each audit and override;
- how false convictions and corrupt acquittals are scored;
- whether monitors share architecture/data and therefore failure modes;
- who or what supervises the final layer;
- a stopping rule based on marginal safety benefit, not an assumption that risk reaches zero.

## Experimental phases

1. **Mechanism validation:** make an unmonitored policy reliably exploit the proxy reward. **(COMPLETE)**
2. **Static monitor:** train a classifier on trajectories and compare it with all controls. **(COMPLETE)** — Threshold-selection failure demonstrated in two environments.
3. **Adaptive evasion:** train the actor against a frozen monitor. **(PARTIALLY COMPLETE)** — Monitor-aware actors implemented but do not meaningfully differ from non-adaptive actors. Needs rework.
4. **Alternating training and dynamics characterization (PRIMARY NEXT PHASE):**
   - Implement alternating actor-monitor training loop in the dual-track environment.
   - Run sweeps varying: number of alternation rounds, relative training episodes per round, environment parameters.
   - Classify observed dynamics into convergence/cycling/escape regimes.
   - Formalize the actor-monitor coevolution game and derive analytical conditions for each regime.
   - Test predictions by modifying environment structure (observation overlap, action space, information asymmetry).
5. **Formal analysis:**
   - Model the actor-monitor interaction as an extensive-form game with information asymmetry.
   - Characterize Nash equilibria and their properties (safety, usefulness).
   - Prove conditions under which alternating best response converges vs. cycles.
   - Connect to the Balcan et al. (2023) non-convergence result and Red Queen dynamics literature.
   - Derive structural conditions (monitoring coverage, mimicry capacity) that predict the regime.
6. **Recursive oversight:** introduce a fallible/corrupt monitor and audit it at depths 1–3. (DEFERRED)
7. **Language transfer:** use an LLM as actor/monitor only if the formal analysis produces predictions worth testing at scale. (DEFERRED)

## Interpretation rules

- A toy result is evidence about this environment and protocol, not frontier AI safety.
- Training labels supplied by an oracle must not be described as solving value specification.
- Post-hoc threshold selection must be disclosed; ideally thresholds are selected on validation data before final evaluation.
- Exploratory runs and confirmatory runs must be separated.
- Negative findings, seed variance, and failed environment designs belong in the report.
- A hierarchy cannot make failure probability literally zero without assumptions about independence, observability, and the reliability of the final adjudicator.

## Immediate reading checklist

For each source, write a short note answering:

- What precise threat model is assumed?
- What information does each actor and monitor observe?
- Which component is trusted, and why?
- What are the safety and usefulness metrics?
- Can the agent adapt to or collude with the monitor?
- Which result would fail to transfer to this project?
- What experiment remains genuinely unanswered?

The first practical goal is not novelty at all costs. It is a correct, reproducible baseline that makes the assumptions visible. Novelty can come later from adaptive training dynamics, correlated failures, model diversity, or measured returns to recursive oversight.

## Deferred big-scale questions

A separate set of long-term questions and research ideas is kept in `docs/research_notes.md`. Those include the relevance of a police/actor model to superhuman RSI AGI, whether monitors can realistically match actor capability, and open questions about base-case morality, virtue formation, and the AI-village idea. They are intentionally not part of the immediate experimental plan.
