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
