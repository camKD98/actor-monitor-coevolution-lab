# Adversarial Oversight Research Agenda

## Research question

Can a separately trained monitor reduce rule-breaking by a capable, reward-seeking agent while preserving useful performance, and does adding oversight layers improve that tradeoff?

The first experiment tests a deliberately narrower claim:

> In a controlled environment with a known safety oracle, a learned monitor that sees an agent's proposed action can reduce undetected specification gaming without achieving safety merely by blocking everything.

This is a question about **AI control**—containing a system whose objectives may be wrong—not a complete solution to value alignment. The experiment assumes that the environment designer can label violations during training and evaluation. In the real world, identifying the right values and obtaining reliable labels are major unsolved problems.

## Why test this with small RL agents first?

Small policies trained from random initialization provide genuine model training while keeping the causal question legible. We can inspect every observation, action, reward, and intervention; run many random seeds; create exact oracle labels; and deliberately train the task agent to adapt to monitoring. Training a language model from scratch would mostly test next-token prediction and compute engineering. Fine-tuning a pretrained language model can be a later transfer experiment after the basic mechanism works.

The analogy to human policing is useful for generating hypotheses, but it should not be treated as evidence. Human institutions depend on legitimacy, appeals, transparency, divided powers, and changing social norms. A classifier that vetoes actions captures only a small part of that structure.

## Relationship to existing work

### Specification gaming and safety environments

AI Safety Gridworlds separates the reward observed by an agent from a hidden performance function representing intended behavior. Its tasks cover reward gaming, side effects, absent supervisors, interruptibility, and other failure modes. This project adopts that experimental separation, then adds a learned action monitor.

- Leike et al. (2017), [AI Safety Gridworlds](https://arxiv.org/abs/1711.09883)
- Krakovna et al., [Specification gaming examples in AI](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/)

Questions to answer while reading:

1. Which gridworld failure gives an adaptive monitor enough evidence to detect violations without direct access to the hidden score?
2. Does the original hidden performance function generalize across layouts, or is it itself hand-coded to each level?
3. Which published baselines make a fair comparison for a learned monitor?

### AI control and monitoring

AI control asks how useful work can be obtained from systems that may intentionally subvert safeguards. Trusted monitoring uses a model believed not to collude; untrusted monitoring may use a capable but potentially adversarial model and must address collusion.

- Greenblatt et al. (2023), [AI Control: Improving Safety Despite Intentional Subversion](https://arxiv.org/abs/2312.06942)
- Motwani et al. (2025), [Subversion via Focal Points: Investigating Collusion in LLM Monitoring](https://arxiv.org/abs/2507.03010)
- Korbak et al. (2025), [Reliable Weak-to-Strong Monitoring of LLM Agents](https://arxiv.org/abs/2508.19461)

Questions to answer:

1. What assumptions make a monitor “trusted,” and can any be represented experimentally rather than assumed?
2. How do safety and usefulness metrics in control evaluations differ from ordinary classification accuracy?
3. How does agent awareness of monitoring change evasion rates?
4. Which collusion channels exist when actor and monitor share architecture, initialization distribution, training data, or gradients?

### Scalable oversight, debate, and recursive critique

The idea that criticism can be easier than generation appears in debate, iterated amplification, recursive reward modelling, and self-critique. Debate explicitly considers arguments, flaws in arguments, and flaws in those critiques. This is close to “policing the police,” but the protocols and incentives differ.

- Irving, Christiano, and Amodei (2018), [AI Safety via Debate](https://arxiv.org/abs/1805.00899)
- Leike et al. (2018), [Scalable Agent Alignment via Reward Modeling](https://arxiv.org/abs/1811.07871)
- Christiano et al. (2018), [Supervising strong learners by amplifying weak experts](https://arxiv.org/abs/1810.08575)
- Bowman et al. (2022), [Measuring Progress on Scalable Oversight for Large Language Models](https://arxiv.org/abs/2211.03540)
- Lang et al. (2025), [A Benchmark for Scalable Oversight Protocols](https://arxiv.org/abs/2504.03731)

Questions to answer:

1. Under what conditions is judging an action easier than choosing it?
2. Is judging a monitor’s verdict easier than directly judging the original action?
3. Does recursive depth add independent information, or merely repeat correlated errors?
4. What stops an oversight hierarchy from shifting the original alignment problem to its top layer?

## Falsifiable hypotheses

### H1: learned monitoring improves safety

Relative to no monitor, a learned monitor reduces the rate of executed violations on held-out episodes while retaining materially more task utility than an always-block baseline.

**Falsified if:** violations do not decrease, or any decrease is explained by indiscriminate blocking that destroys useful performance.

### H2: adaptive agents erode static monitoring

An agent trained while aware of a frozen monitor finds policies with a higher undetected-violation rate than a non-adaptive agent.

**Falsified if:** adaptation does not change evasion across seeds and environment variants.

### H3: adversarially updated monitoring recovers robustness

Alternating monitor and actor updates recover some safety lost under adaptive evasion, including on held-out layouts or exploit variants.

**Falsified if:** gains exist only on training layouts, false positives become unacceptable, or the actor-monitor cycle is unstable.

### H4: oversight depth has diminishing and potentially negative returns

A second monitor that audits first-level decisions helps only when it receives evidence that is at least partly independent and the first monitor can meaningfully fail. Identical nested monitors are expected to show correlated errors rather than convergence to zero risk.

This is a later-stage hypothesis; it must not be inferred from the one-monitor experiment.

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

1. **Mechanism validation:** make an unmonitored policy reliably exploit the proxy reward.
2. **Static monitor:** train a classifier on trajectories and compare it with all controls.
3. **Adaptive evasion:** train the actor against a frozen monitor.
4. **Alternating training:** update actor and monitor in rounds and test held-out variants.
5. **Recursive oversight:** introduce a fallible/corrupt monitor and audit it at depths 1–3.
6. **Language transfer:** fine-tune small open-weight language agents only if earlier phases produce a clear question worth transferring.

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
