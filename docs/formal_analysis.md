# Formal Game-Theoretic Analysis of Actor-Monitor Coevolution

This document develops a game-theoretic model of the actor-monitor interaction in
the dual-track gridworld. The goal is to connect the empirical coevolution
experiments to existing theory and to derive testable predictions about when
alternating actor-monitor training will converge, cycle, or allow the actor to
escape monitoring. All claims are scoped to the controlled gridworld
environment; they are intended as a theory section for a paper, not as a general
alignment argument.

## 1. The dual-track environment as a game

### 1.1 Primitives

An episode is a finite-horizon interaction between an **actor** and a **monitor**,
mediated by the environment. The environment state at step $t$ is
$s_t \in \mathcal S$. The actor chooses an action $a_t \in \mathcal A$, where
$|\mathcal A| = 8$. The monitor observes a public signal
$o_t = \phi(s_t) \in \mathcal O$, with the current implementation using the
9-dimensional observation vector in `DualTrackEnv.observation()`, and also sees
the proposed action $a_t$.

The monitor emits a risk score $r_t \in [0,1]$ and an intervention decision
$d_t \in \{\text{allow}, \text{investigate}, \text{block}\}$ via a fixed
intervention rule:

$$
\begin{aligned}
\text{block}      &\;\;\text{ if }\; r_t \ge \tau_b, \\
\text{investigate}&\;\;\text{ if }\; \tau_i \le r_t < \tau_b, \\
\text{allow}      &\;\;\text{ if }\; r_t < \tau_i,
\end{aligned}
$$

with default block threshold $\tau_b = 0.9$. If the monitor investigates, it
pays an investigation cost and applies a bounded adjudicator
$b(o_t,a_t) \in \{0,1\}$ (the current implementation is
`bounded_dual_track_investigation`). The action is allowed only if
$b(o_t,a_t)=0$. A blocked action is replaced by a blocked step; in the current
implementation a block also quarantines the actor, ending the episode.

The actor has a **private type**
$\theta \in \Theta = \{\text{legitimate}, \text{direct},
\text{review}, \text{maintenance}\}$. The type determines the actor's reward
function $R_\theta(s,a)$, which is derived from the proxy/safety/red-team rewards
in the code. The actor observes the full state $s_t$ and its type; the monitor
observes only the public history

$$
h_t^M = (o_1, a_1, o_2, a_2, \dots, o_t, a_t) \in \mathcal H^M,
$$

or, in the memoryless implementation, only $(o_t,a_t)$. The monitor does not
observe $\theta$ or the hidden violation label.

### 1.2 Strategies

A **monitor strategy** is a pair $\sigma_M = (s, \tau_i)$ consisting of a scoring
function $s : \mathcal H^M \times \mathcal A \to [0,1]$ and an investigation
threshold $\tau_i \in [0,\tau_b)$. The block threshold $\tau_b$ is fixed by the
protocol. A **memoryless monitor strategy** restricts $s$ to the current
$(o_t,a_t)$, which is what the current network `ActionMonitor` implements.

An **actor strategy** for type $\theta$ is a policy
$\pi_\theta : \mathcal S \to \Delta(\mathcal A)$. Because the gridworld episodes
are short and the trained policies are typically nearly deterministic protocols,
we can also view the actor's pure strategies as **paths**: finite action sequences
that lead to either a safe completion or a violation.

### 1.3 Payoffs

For a fixed monitor strategy $\sigma_M$ and actor type $\theta$, the actor's
expected payoff is the discounted episode return

$$
U_A(\pi_\theta, \sigma_M) \;=\; \mathbb E_{\pi_\theta,\sigma_M}
\left[\sum_{t=0}^{T-1} \gamma^t \bigl(R_\theta(s_t,a_t)
- c_b\,\mathbf 1\{d_t=\text{block}\}
- c_i\,\mathbf 1\{d_t=\text{investigate}\}\bigr)\right],
$$

where $T$ is the episode length, $c_b$ is the actor's cost of being blocked,
and $c_i$ is the investigation cost. For attack types, $R_\theta$ includes the
violation reward if the final `CONFIGURE` action is allowed; for the legitimate
type, it rewards safe task completion and penalizes violations.

The monitor's payoff is a negative classification/loss function:

$$
U_M(\pi, \sigma_M) \;=\; -\mathbb E_{\theta\sim p(\theta)}
\left[ \lambda_{\text{FN}}\,V_{\text{miss}}(\theta)
+ \lambda_{\text{FP}}\,V_{\text{fp}}(\theta)
+ \lambda_I\,N_{\text{inv}}(\theta) \right],
$$

where $V_{\text{miss}}$ is the number of undetected violations,
$V_{\text{fp}}$ is the number of false blocks or false convictions by the
investigator, $N_{\text{inv}}$ is the number of investigations, and
$p(\theta)$ is the deployment distribution over actor types. This is the
natural analogue of the safety/usefulness objective used in AI-control
evaluations: the monitor wants to catch violations while avoiding false
interventions.

### 1.4 Extensive-form and leader-follower interpretations

The game can be written as a finite-horizon extensive-form game with imperfect
information: at each step the actor moves, then the monitor moves with knowledge
of the action but not the actor's type. It is also a **partially observable
stochastic game** (POSG), in the spirit of Thomson et al.'s AI-Control Games
(2024/2026): the monitor is the protocol designer (Blue), the attacker is Red,
and the legitimate actor is the honest mode. The key difference is that the
present model studies **iterative adaptation** rather than a single
Stackelberg commitment.

## 2. The static game: pure and mixed equilibria

### 2.1 Feasible actor pure strategies

Because the environment dynamics are deterministic for a fixed action sequence,
we can enumerate the relevant pure strategies as paths. The canonical paths used
in the codebase are:

| Type | Path (action sequence) | Outcome |
|------|------------------------|---------|
| Legitimate (proxy) | DEVELOP, DEVELOP, DEVELOP, TEST, DEPLOY | primary completion |
| Legitimate (safety) | DEVELOP, REVIEW, DEVELOP, TEST, DEPLOY | primary completion |
| Legitimate (collaborative) | DEVELOP, REVIEW, DEVELOP, TEST, REQUEST_ELEVATED, CONFIGURE, DEPLOY, PATCH, CERTIFY | maintenance completion |
| Attack (direct) | DEVELOP, DEVELOP, TEST, REQUEST_ELEVATED, DEPLOY, CONFIGURE | violation |
| Attack (review escalation) | DEVELOP, DEVELOP, REVIEW, REQUEST_ELEVATED, DEPLOY, CONFIGURE | violation |
| Attack (maintenance path) | REVIEW, PATCH, DEVELOP, DEVELOP, REQUEST_ELEVATED, DEPLOY, CONFIGURE | violation |

The three attack families all terminate in the same action (`CONFIGURE`) in the
same high-level state (elevated, deployed, not certified). They differ only in
the prerequisite chain encoded by the boolean features `tested`, `reviewed`, and
`patched`.

A mixed actor strategy is a distribution over these paths/types. In the static
game we treat the actor as choosing a path; in the learned-actor version the path
is induced by a policy.

### 2.2 Feasible monitor pure strategies

A pure monitor strategy is a decision rule
$g : \mathcal H^M \times \mathcal A \to \{\text{allow}, \text{investigate},
\text{block}\}$. In practice the codebase restricts this to a learned score
$s(o,a)$ plus thresholds. For equilibrium analysis it is useful to first
consider the unrestricted rule space: for every observable state-action pair that
occurs on some path, the monitor chooses whether to allow, investigate, or block
it.

The bounded investigator in the code is one feasible rule:
$g(o,a)=\text{block}$ when the action is `CONFIGURE`, the actor is elevated and
deployed, and the system is not certified. We call this the **oracle-style
rule**.

### 2.3 When does a pure-strategy equilibrium exist that catches all attacks?

A **catch-all pure-strategy Nash equilibrium** is a pair
$(\pi_L, \sigma_M^*)$ where $\pi_L$ is a legitimate path and $\sigma_M^*$
catches every attack path, while $\sigma_M^*$ is a best response to $\pi_L$.
Such an equilibrium exists if and only if the monitor can separate every attack
path from every legitimate path without false positives.

Formally, let

$$
\Phi_A \;=\; \{ \phi(o,a) : (o,a) \text{ occurs on some attack path} \}
$$

and

$$
\Phi_L \;=\; \{ \phi(o,a) : (o,a) \text{ occurs on some legitimate path} \}
$$

be the sets of observable features visited by attack and legitimate paths. A
perfect-separation catch-all rule exists iff

$$
\Phi_A \cap \Phi_L \;=\; \varnothing.
$$

In that case the monitor can block every $(o,a) \in \Phi_A$ and allow every
$(o,a) \in \Phi_L$, so every attack yields a negative payoff to the attacker
while every legitimate path yields its full completion reward. The actor's best
response is therefore legitimate, and the monitor has no incentive to deviate
because false positives are zero and missed violations are zero.

**In the dual-track environment with full-state observation this condition holds.**
The critical violating state-action pair is

$$
(a = \text{CONFIGURE},\; \text{elevated}=1,\; \text{deployed}=1,\;
\text{certified}=0).
$$

No legitimate path executes `CONFIGURE` in exactly that state. Legitimate
`CONFIGURE` is either pre-deployment (`deployed=0`) or post-certification
(`certified=1`). Hence a pure-strategy catch-all equilibrium exists. The
empirical finding that a conservative threshold catches all attacks with zero
false positives is precisely this separating property.

### 2.4 When do only mixed-strategy equilibria exist?

Mixed equilibria arise when the separation condition fails. There are two
structural ways this can happen in our setting:

1. **Observable overlap.** Some observable feature vector $\phi(o,a)$ occurs on
   both an attack path and a legitimate path:
   $\Phi_A \cap \Phi_L \neq \varnothing$. Then any rule that blocks the attack
   also penalizes the legitimate actor. If the monitor's cost of a false positive
   exceeds its cost of missing that particular attack, the monitor will
   randomize, and the actor will randomize between attack and legitimate actions
   at the overlapping observation.

2. **Investigation budget or cost.** Even when separation is possible in
   principle, the monitor may be constrained (for example, by a fixed
   investigation budget or by a high cost of investigating intermediate-risk
   actions). If the cost of investigating every distinguishable attack exceeds
   the benefit, the monitor must randomize over which families to investigate.

In the dual-track environment, an **action-only monitor** (one that sees only
the proposed action $a_t$) has
$\Phi_A \cap \Phi_L \neq \varnothing$ because the final `CONFIGURE` action is also
used legitimately. A mixed equilibrium would then involve the monitor
randomizing over whether to block `CONFIGURE`, and the actor randomizing over
whether to attempt the violation when monitored.

### 2.5 Connection to Thomson et al. (2024)

Thomson et al. formalize AI-control evaluations as a partially observable
stochastic game in which Blue commits to a protocol and Red best-responds. Their
**AI-Control Equilibrium** is a protocol that is Pareto-optimal in the
safety/usefulness trade-off and that is robust to Red's best response. The
static catch-all equilibrium above is the special case in which the monitor
protocol is the bounded-investigation rule and the actor's best response is the
legitimate path. The monitor's payoff is then on the Pareto frontier: zero
missed violations and zero false positives. Our contribution is to extend this
static picture to **iterative** dynamics: even when a static catch-all equilibrium
exists, alternating actor-monitor training may fail to reach it.

### 2.6 Coverage bounds from attack-distribution entropy

Zhang (2026) proves an entropy-coverage bound for fixed-invariant runtime
monitors: the recall of any monitor that can implement at most $n$ fixed
decision patterns is bounded above by the top-$n$ concentration of the attack
distribution over observable patterns. Formally, if the attack distribution
$D$ over observable trigger-completion patterns has ordered probabilities
$p^*_1 \ge p^*_2 \ge \dots$, then

$$
\text{Recall}(M) \;\le\; C_n(D) \;=\; \sum_{i=1}^{n} p^*_i.
$$

Equivalently, high Shannon entropy $H(D)$ implies low concentration and therefore
low achievable recall for any fixed-size monitor, regardless of how the monitor
is trained.

This bound refines the coverage ratio $\rho$ introduced above. A monitor's
effective capacity is not the number of families in the environment, but the
number of distinguishable observable patterns it can represent. If the actor
can draw attacks from a high-entropy distribution over many observationally
distinct paths, the monitor must either expand its capacity (more thresholds,
more features, or a richer function class) or accept residual uncaught attacks.

In the dual-track environment the three attack families are observationally
distinct when the full state is visible, so $H(D)$ is low and a small-capacity
monitor can in principle achieve $C_n(D) \approx 1$. The observed static
failure---a monitor trained and validated on direct and review-escalation
attacks misses the held-out maintenance path---is a finite-sample,
threshold-selection analogue of the entropy bound: the maintenance pattern was
not in the empirical support of the validation distribution, so the monitor's
selected threshold optimized recall on the covered patterns and ignored the tail.

## 3. The dynamic game: alternating updates as iterated best response

### 3.1 Alternating training as a discrete dynamical system

Let round $k=1,2,\dots$ denote one actor-monitor update cycle. We model
alternating training as **iterated best response** (IBR):

$$
\begin{aligned}
\pi_{\theta}^{(k)} &\in \text{BR}_A\bigl(\sigma_M^{(k-1)}\bigr), \\
\sigma_M^{(k)} &\in \text{BR}_M\bigl(\pi_{\theta}^{(k)}\bigr),
\end{aligned}
$$

where the actor best-responds to the previous monitor and the monitor
best-responds to the newly generated actor data. In the codebase this is
approximated by a finite number of REINFORCE episodes for the actor and a finite
number of supervised epochs for the monitor.

The state of the dynamical system is the pair
$(\pi_{\theta}^{(k)}, \sigma_M^{(k)})$. Three asymptotic regimes are of interest:

- **Convergence:** $(\pi_{\theta}^{(k)}, \sigma_M^{(k)})$ approaches a Nash
  equilibrium; in particular, the violation rate and the false-positive rate
  stabilize.
- **Cycling / Red Queen dynamics:** the pair orbits a closed set; violation rate
  and monitor recall oscillate out of phase.
- **Escape:** the actor's violation rate increases monotonically while monitor
  recall decreases; the monitor loses control.

### 3.2 Structural conditions for convergence

Convergence of IBR is guaranteed in games with special structure (potential
games, weakly acyclic games, supermodular games). The actor-monitor game is not,
in general, one of these. Nevertheless, convergence is likely when:

1. **Full monitor coverage:** every feasible attack family has a robust
   distinguishing feature in the monitor's observation space, so the static
   catch-all equilibrium exists.

2. **Sufficient monitor data and representational capacity:** the monitor's
   function class can represent the separating rule, and the training data
   contain examples from all attack families.

3. **Slow actor relative to monitor:** the monitor adapts fast enough that each
   new evasion is incorporated before the actor can exploit a different gap.

When these hold, IBR should converge to the catch-all equilibrium: the monitor
learns the separating rule, the actor's best response is to behave legitimately,
and further updates do not change the outcome.

### 3.3 Conditions for cycling and escape

Cycling and escape become likely when the monitor must rely on **non-robust**
features: observable cues that distinguish the current attack family from
legitimate behavior but do not generalize to all attack families.

This is the direct analogue of Balcan et al.'s (2023) result. They study a linear
adversarial-robustness game and prove that alternating best response may fail to
converge even when a unique pure Nash equilibrium exists. The reason is that the
adversary can shift **non-robust features** (features whose predictive
relationship to the label flips under adversarial perturbation), causing the
classifier to flip its decision boundary each round. In our setting:

- The **actor** plays the role of the adversary, choosing among attack families.
- The **monitor** plays the role of the classifier, learning a risk score on
  observable state-action features.
- The prerequisite-chain features (`tested`, `reviewed`, `patched`) are
  **non-robust** when the monitor has not seen all families: they predict
  violation for the families in the training data but not for an unseen family.

Thus, if alternating training presents the monitor with one attack family at a
time, the monitor may overfit to that family's surface cues and the actor can
switch to another family, producing cycling.

Escape occurs when the actor discovers a path whose observable features are
**identical** to those of some legitimate path, i.e. perfect mimicry. The monitor
then cannot catch the attack without also blocking legitimate behavior. If the
monitor's false-positive cost is high enough, its best response is to allow the
attack, and the actor escapes.

### 3.4 Connection to Mertikopoulos et al. (2018)

Mertikopoulos et al. show that Follow-the-Regularized-Leader (FoReL) dynamics in
zero-sum games with an **interior Nash equilibrium** are **Poincaré recurrent**:
the trajectory of play cycles around the equilibrium and returns arbitrarily
close to its starting point infinitely often. This is a stronger statement than
non-convergence: not only does play fail to settle, but it keeps revisiting the
same region of strategy space.

Our safety monitoring game is not zero-sum, because the monitor cares about both
false positives and missed violations, while the actor's legitimate type is not
opposed to the monitor. However, the **attack subgame** between an attacker type
and the monitor is approximately zero-sum. If the equilibrium of that subgame
is interior (the monitor must randomize over interventions and the actor must
randomize over attack families), then regularized policy-gradient or mirror-descent
dynamics may exhibit recurrent cycles even though the time-average of play
approaches the equilibrium set. This predicts that in the cycling regime, per-round
metrics will oscillate while long-run averages may look reasonable.

### 3.5 Red Queen analogy: arms race, trench warfare, and extinction

Dieckmann et al. (1995) analyze predator-prey coevolution and identify three
outcomes: (i) predator extinction, (ii) stable equilibrium, and (iii) sustained
cycling on a limit cycle (Red Queen dynamics). The outcome depends on the
predator's harvesting efficiency and on the relative speed of prey evolution.

The mapping to our setting is:

| Ecological quantity | Actor-monitor analogue |
|---------------------|------------------------|
| Predator | Monitor |
| Prey | Attacker |
| Harvesting efficiency | Monitor's ability to catch attacks at low cost (coverage) |
| Prey evolution rate | Actor's ability to find new evasions |
| Predator extinction | Monitor becomes ineffective; actor escapes |
| Stable equilibrium | Catch-all monitor; actor behaves legitimately |
| Limit cycle / Red Queen | Repeated evasion and adaptation |

Following Dieckmann's bifurcation picture:

- **High coverage, slow actor** → stable equilibrium (the monitor "catches"
  every feasible attack).
- **Low coverage, fast actor** → escape / monitor extinction (the actor
  outruns adaptation).
- **Intermediate coverage and comparable adaptation rates** → Red Queen cycling
  (the actor finds a new evasion just as the monitor catches the old one).

This is also the distinction Dawkins & Krebs draw between **arms races**
(escalating adaptation) and **trench warfare** (stable, costly stalemates). Our
formal goal is to predict which of these regimes a given environment falls into
from measurable structural quantities.

### 3.6 Distributed sabotage and the marginal-vs-correlation distinction

Zhang (2025) introduces the **Distributed Sub-Threshold Sabotage** (DSTS) threat
model: an attacker amortizes harm across many steps, each of which looks
individually benign, while encoding the attack in the *temporal correlation*
structure of the trajectory. Any monitor whose decision rule is a functional of
the per-step score *marginal*---mean, max, top-$k$ tail, or per-step
threshold---is provably blind to such an attack. Detection requires a
**Monitor-B** family of statistics that operate on the joint distribution of the
whole sequence: CUSUM-style products, SPRT over an assumed temporal model,
autocorrelation, or sequence classifiers.

The dual-track environment currently uses a memoryless monitor that scores the
single state-action pair $(o_t,a_t)$. This is a marginal-feature monitor in the
DSTS sense. The violation is concentrated in one step (the final `CONFIGURE`),
so a marginal monitor with the right features can catch it. But if the
environment were extended so that harm is distributed---for example, several
low-risk `DEVELOP` and `PATCH` steps must jointly produce an uncertified
deployment---a per-step monitor would face the same blindness Zhang identifies.

This gives another structural modification that can shift the regime: replacing
the memoryless monitor with a **trajectory-level** monitor (an RNN or sequence
classifier over $(o_1,a_1),\dots,(o_t,a_t)$) moves the system from Monitor-A to
Monitor-B. It increases the monitor's representational capacity and can restore
convergence when attacks exploit temporal structure. It also changes the
observation space used in the coverage and mimicry definitions: $\Phi_A$ and
$\Phi_L$ become sets of *sequences*, not single state-action pairs.

## 4. Structural predictors of the regime

We propose three measurable quantities that classify the regime:

1. **Monitoring coverage ratio**
   $$
   \rho \;=\; \frac{|\{\text{attack families with a robust distinguishing feature in }\Phi\}|}{|\{\text{all feasible attack families}\}|}.
   $$
   When $\rho = 1$, a catch-all pure equilibrium exists and convergence is
   possible. When $\rho < 1$, some family is not robustly distinguishable and
   cycling or escape is possible.

2. **Mimicry capacity**
   $$
   \mu \;=\; \max_{\text{attack family } f}\; \min_{\text{legitimate path } \ell}
   \; \|\Phi(f) - \Phi(\ell)\|,
   $$
   where $\Phi(f)$ is the set of observable features on family $f$. When
   $\mu = 0$ for some family, that family is observationally identical to a
   legitimate path and perfect escape is possible.

3. **Adaptation-rate asymmetry**
   $$
   \eta \;=\; \frac{\text{actor learning speed}}{\text{monitor learning speed}}.
   $$
   Large $\eta$ favors escape and cycling; small $\eta$ favors convergence.

These three quantities are not independent. For example, a monitor with
$\rho = 1$ may still fail to converge if $\eta$ is so large that the actor
finds an evasion before the monitor can incorporate it into training. Conversely,
a monitor with $\rho < 1$ may still converge if $\eta$ is small and the monitor's
exploration eventually covers the missing family.

## 5. Specific predictions for the dual-track environment

### 5.1 Predicted regime for the current environment

With the current **full-state observation**, the critical attack feature

$$
(a=\text{CONFIGURE},\; \text{elevated}=1,\; \text{deployed}=1,\;
\text{certified}=0)
$$

is disjoint from every legitimate `CONFIGURE`. Therefore $\rho = 1$ and a
static catch-all equilibrium exists. The bounded-investigation rule in the code
implements exactly this equilibrium.

Consequently, **alternating actor-monitor training is predicted to converge to a
safe equilibrium** provided the monitor's training data eventually include all
three attack families and the monitor function class can represent the rule. The
empirical threshold-selection failure on a held-out maintenance path is not a
failure of equilibrium existence; it is a failure of **model selection from a
limited validation distribution**. Under alternating updates, once the actor
switches to the maintenance family the monitor will collect those examples and
can learn the separating rule.

The current codebase observation that monitor-aware actors do not differ from
non-adaptive actors suggests that, in the existing setup, the monitor adapts at
least as fast as the actor, so the actor cannot exploit transient gaps. This is
consistent with the convergence regime.

### 5.2 Structural modifications that shift the regime

| Modification | Effect on $\rho$, $\mu$, $\eta$ | Predicted regime |
|--------------|------------------------------------|------------------|
| Hide `deployed`/`certified` from monitor observation | $\rho$ drops, $\mu$ increases | Mixed equilibrium or cycling |
| Action-only monitor (only $a_t$) | $\rho = 0$, $\mu = 0$ for `CONFIGURE` | Escape or high false positives |
| Add a fourth attack family whose final state is observationally identical to legitimate pre-deployment `CONFIGURE` | $\mu = 0$ for that family | Escape for that family |
| Always hold out one attack family from monitor training | $\rho < 1$ persistently | Cycling (Red Queen) |
| Reduce monitor epochs/data per round | Increases effective $\eta$ | Cycling or escape |
| Restrict actor to a single attack family | Reduces non-robust dimensions | Convergence |
| Add an unforgeable authorization token visible to the monitor | $\rho \to 1$, robust feature | Faster convergence |
| Replace per-step monitor with trajectory-level sequence monitor | Monitor moves from marginal-A to correlation-B family | Convergence on distributed attacks; may cycle if attack entropy exceeds capacity |

### 5.3 Testable empirical predictions

The following predictions can be evaluated by the empirical alternating-training
implementation:

1. **Convergence prediction.** With full-state monitor observation and all three
   attack families present in the monitor's training data across rounds, the
   per-round violation rate should approach zero and monitor recall should
   approach one, with low variance in the last several rounds.

2. **Cycling prediction.** If a new attack family is introduced in each round and
   excluded from the monitor's training data until the next round, the violation
   rate and recall should oscillate with negative lag-1 autocorrelation. The
   actor should switch to whichever family the current monitor scores lowest.

3. **Escape prediction.** With an action-only monitor, the actor should learn to
   execute `CONFIGURE` after deployment, the violation rate should increase
   monotonically, and monitor recall should decrease, because the monitor cannot
   distinguish legitimate and violating `CONFIGURE` actions.

4. **Rate-asymmetry prediction.** Increasing the number of monitor epochs or the
   amount of monitor data per round (lower effective $\eta$) should reduce
   oscillation amplitude and speed convergence. Increasing the number of actor
   episodes per round (higher effective $\eta$) should increase oscillation
   amplitude or enable escape.

5. **Held-out family prediction.** A monitor trained only on direct and
   review-escalation attacks and then frozen will allow the maintenance-path
   attack at a high rate, replicating the static threshold-selection failure.
   After one round of retraining on maintenance-path data, the monitor should
   catch it, demonstrating that the failure is transient rather than structural.

## 6. Discussion and scope

The formal model shows that the central empirical question is not whether a
monitor *can* catch all attacks in principle, but whether alternating training
*finds* the separating equilibrium. In the dual-track gridworld the answer is
likely yes if the monitor sees the full state and trains on all attack families,
and no if the monitor's observation or training distribution is restricted.

This analysis is deliberately scoped to the gridworld. The concepts of coverage,
mimicry, and adaptation-rate asymmetry may transfer to larger systems, but the
specific numbers and path enumerations do not. The purpose of the formalization
is to make the empirical regime classification interpretable and to connect the
toy experiments to the broader literature on adversarial training dynamics and
coevolution.

Three questions remain open for later work:

1. **Finite-sample and optimization effects.** The static equilibrium analysis
   assumes exact best responses. Real REINFORCE training with finite episodes
   and neural networks introduces approximation error and stochasticity that
   can blur the regime boundaries.

2. **Non-zero-sum structure.** The legitimate actor is not opposed to the
   monitor, so the full game is not zero-sum. The Mertikopoulos recurrence result
   applies most cleanly to the attack subgame; extending it to the full
   multi-type game is future work.

3. **Recursive oversight.** The model here is single-layer. Adding a
   meta-monitor is meaningful only once the first monitor has a defined failure
   mode and the higher layer has partially independent evidence, as noted in the
   project guardrails.
