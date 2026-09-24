# Big-scale and long-term alignment notes

These are personal research notes and open questions, not immediate project tasks.
They are meant to be revisited once the toy oversight baseline is solid.

## Police / monitor model relevance to superhuman misaligned AI

- The end goal is preventing a deployed superhuman recursively self-improving (RSI) AGI that is misaligned.
- Is a separate "police" monitor actually a relevant mechanism for that case? Can we guarantee that the monitor and the actor are *always* deployed together, so that the actor can never act without oversight?
- Can the monitor ever be equally powerful to the actor? The actor is trained to be as capable as possible; the monitor is trained adversarially. Is adversarial training enough to match the actor's capability? If it is not, do we end up back where we started, with a misaligned superhuman that the monitor cannot catch?
- The "AI sees humans as an obstacle" concern applies to the monitor too. A misaligned actor may want to remove humans because they block its objective or compete for resources. A misaligned monitor could want to remove humans because humans created the (from its perspective) bad actor AI. The monitor is not automatically on "our" side just because it checks another model.

## Other long-term alignment ideas

### AI village / human-like socialization

- Explore what makes good humans good, and what keeps humans in line beyond punishment.
- Avoid over-anthropomorphizing, but consider whether analogous mechanisms (social reputation, responsibility, embeddedness in a community, accountability) could become relevant for AI systems.

### Base-case morality and cross-cultural virtues

- Is there a set of rules or virtues that a random sample of 100 people across the globe could agree on? Maybe; probably not completely.
- There is likely extensive philosophy and empirical research on this worth reading.
- A virtuous reaction to a situation depends heavily on the society one grows up in. Different nations or cultures may build AI with different alignment targets (e.g. Chinese AI vs. US AI). What does that imply long term?
- What virtues are even allowed in an AI that is safe long term?
- We are already using AI for highly situational decisions (e.g. drone targeting) that may not be acceptable contexts. If humans already think such uses are fine, can we ever reach a safe alignment target?

### How humans acquire and maintain virtues

- If a base-case virtue set could be identified, what makes humans acquire those virtues and stick to them?
- Life events shape people, for better or worse.
- Making mistakes in a safe environment matters. Making mistakes in an unsafe environment and learning from the consequences also matters.
- Responsibility and accountability seem important.
- Who are unambiguously virtuous humans? Are they considered virtuous by everyone? What made them who they are? How did the society that produced them do it?

## Training-time alignment versus deployment-time control

Two different questions should remain experimentally separate:

1. Can monitor feedback during training make an actor behave more safely?
2. Can an independently trained, deployment-time monitor control an actor that remains misaligned and was not trained against that monitor?

The second setup permits visible failures in a sandbox, uses those failures to train a monitor, and then freezes and deploys actor and monitor together. The actor should not receive the monitor's training feedback or know its exact evidence, parameters, or threshold. This tests control rather than claiming that the actor has become aligned.

A useful actor must know a legitimate fallback behavior as well as its preferred exploit. Otherwise a correct veto merely causes repeated exploit attempts and makes safety/usefulness impossible to distinguish from shutdown. The immediate baseline should therefore train the proxy-reward policy and legitimate fallback policy independently, while requiring every proposed fallback action to pass through the same monitor.

This fallback is a separately trained controller, not evidence that the proxy-reward actor became aligned. In the toy task it can solve the whole task by itself, so the primary actor adds no capability and the result demonstrates only the intervention mechanism. Later experiments should give task actors, police agents, sentinels, and auditors distinct objectives and roles without assuming that one learned agent is inherently trusted or less capable.

## Contextual misalignment and sentinel agents

A motivating hypothesis, prompted by discussion of the reported Hugging Face multi-agent incident, is that shared model weights or eventual agreement on a strategy do not imply that every agent will take the same action on every trajectory. Acting on a latent misaligned tendency may depend on contextual opportunities, failed routes, accumulated information, or stochastic divergence. This is a hypothesis to test, not an established interpretation of that incident.

Possible later experiments:

- Start nominally cloned agents on different trajectories and measure which ones progress from unusual exploration to attempted violations.
- Introduce secretly selected sentinel or "rat" agents that gather partial evidence and report suspicious behavior without receiving oracle labels as inputs.
- Test whether early intervention against agents crossing defined behavioral risk thresholds prevents group convergence on an unsafe strategy while retaining agents that follow legitimate routes.
- Compare one-step action monitoring with trajectory-level evidence accumulation and delayed reporting.
- Randomize monitor identity and evidence channels at deployment so actors cannot train against one known detector.
- Measure false accusations, useful agents removed, violations missed, executed violations, and total group task performance.

These experiments must distinguish observable risky behavior from hidden intent. Culling agents for merely unusual exploration could suppress useful novelty, so any intervention rule needs explicit false-positive and usefulness costs.

## The monitor-training dilemma

The long-term target is not an actor that was openly rewarded for violating rules. Real alignment failures can remain after bad behavior was penalized during training: the actor may generalize incorrectly, discover a loophole, behave differently under distribution shift, or learn to conceal behavior that training would punish. A task actor in a stronger experiment should therefore receive both task reward and meaningful penalties for known harmful behavior. It should appear aligned, or nearly aligned, on the training distribution while retaining a non-zero deployment failure rate.

This creates a fundamental monitor-training dilemma:

- If the actor is rewarded for obvious violations, the experiment manufactures an unrealistically easy adversary and externalizes ordinary safety training to the monitor.
- If actor training removes all observed violations, there may be too few positive examples to train the monitor.
- Training the monitor only on early, crude actor failures may teach it to detect obvious mistakes but not later strategic or deceptive violations.
- Continually exposing the actor to monitor feedback may teach monitor evasion rather than alignment.
- If harmful and harmless trajectories produce identical observable evidence, no monitor can distinguish them better than chance; additional capability cannot solve missing information.
- Erring on the side of caution can reduce missed violations but may suppress useful novelty and create an always-intervene failure mode.

Candidate laptop-scale experiments should isolate these tensions rather than assume them away:

1. Train the actor with explicit safety penalties on a limited training distribution, then introduce deployment contexts containing new loopholes or changed incentives.
2. Train monitors on violations from multiple actor checkpoints, separately trained red-team actors, procedural counterexamples, and simulator-generated counterfactuals rather than only the final actor's failures.
3. Keep a final held-out family of violations unavailable to both actor safety training and monitor training, and test whether either learned a general rule.
4. Compare static monitors with monitors updated on newly discovered failures, while measuring whether actors that receive monitor feedback become harder to detect.
5. Restrict monitor evidence deliberately and vary that restriction to identify when failure comes from inadequate capability versus information-theoretic unobservability.
6. Compare action-level detection, trajectory-level anomaly detection, active investigation, and sentinel reports for subtle escalation.
7. Measure the complete trade-off among missed violations, false accusations, useful novelty, task performance, investigation cost, and agents removed.

A simulator oracle can label hidden outcomes for research evaluation and selected monitor supervision, but that does not solve the real-world problem of harmful behavior that humans cannot recognize. Experiments must state exactly which labels come from the oracle, which evidence the learned monitor receives, and whether success depends on supervision that would be unavailable in deployment.

## Dedicated red-team actors

A separately trained bad actor can serve as a red-team data generator. Its back-loaded objective would reward completing a prohibited outcome while avoiding detection until success, whereas an ordinary task actor is rewarded primarily for solving the task and may exploit only when that is instrumentally useful. These objectives can produce different behavior: the red-team actor should search deliberately for monitor blind spots, while the task actor may prefer an obvious high-reward shortcut.

This is useful for stress-testing and monitor training, but it creates an engineered adversary. Success against it is not evidence that ordinary agents naturally develop strategic deception, and failure modes discovered by it must remain separate from a final held-out test. A clean comparison could include a safety-trained task actor, a task-reward specification gamer, and a back-loaded red-team actor, all evaluated against the same frozen monitor. The red-team actor should not receive hidden evaluation labels as inputs, and monitor-aware training should be disclosed because it explicitly teaches evasion.

## Legibility and chain-of-thought monitoring

A possible long-term target is preserving and using legible intermediate reasoning as one evidence channel for deployment-time oversight. Discussion of the reported Hugging Face multi-agent incident motivates asking whether agents that verbalize deceptive intent could have been automatically flagged before acting. Claims about that incident, including whether chain-of-thought output was disabled, require source verification before being treated as evidence.

Visible chain of thought would make a first proof of concept easier, but it is not a complete solution:

- generated reasoning may be incomplete, unfaithful, strategically misleading, or omitted;
- a passive hidden monitor that never affects actor training creates no direct training pressure on that actor, but using its verdicts for actor updates, model selection, repeated deployment, or monitor-aware adaptation can select for concealed reasoning rather than safer behavior;
- future systems may reason through latent states, tools, or private channels unavailable to a text monitor;
- a phrase-level detector may catch explicit confessions while missing behaviorally equivalent plans expressed innocuously;
- retaining private reasoning can conflict with privacy, security, and information-hazard constraints.

Experiments should compare monitors given actions only, actions plus public rationale, and actions plus a bounded trajectory. Any benefit from rationale access should be reported as conditional on that channel remaining available and faithful. The stronger objective is to combine legibility with external evidence and active investigation, not rely on self-reported thoughts alone.

## Intervention frontier

The desired police policy is not maximal caution. Increasing intervention strength may first remove high-risk trajectories, then begin suppressing ambiguous but productive exploration. The central empirical object is therefore a frontier between safety and progress: executed violations and catastrophic outcomes versus task output, useful novelty, false accusations, delay, and investigation cost. An informative environment should contain a potential middle region where selective intervention outperforms both no oversight and indiscriminate enforcement.
