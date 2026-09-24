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

This fallback is a trusted-controller assumption, not evidence that the proxy-reward actor became aligned. In the toy task the fallback is as capable as the primary actor, so it does not yet model the central control problem of obtaining capabilities from an untrusted actor that a weaker trusted policy cannot reproduce. Later experiments should constrain fallback capability or allow it only to recover, defer, or request review.

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
