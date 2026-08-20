# N1 predeclared: the wipe-the-floor mechanism (wall-priced sample scaling)

Status: PREDECLARED before the result JSON is read as evidence. Response-free.
No challenge instance, target, scorer, leaderboard, submission, or champion
artifact is read or changed. Deployment of any native path remains user-gated
and organizer-clarification-gated (plan A2). This is the science-of-the-lever,
not a deployment.

## The reframe that changes the campaign objective

Prior campaign judgment (adb79aa/de9ea4e) proved: #1 requires a 4-6x raw-MSE
cut regardless of the multiplier, because the board leaders already sit on the
0.1 floor (joe_wanza mult 0.142, SKIBIDI 0.0996). The judgment then hunted for
that 4-6x cut in ANALYTIC control variates and found the corpus graveyard
(k3/k4 non-identifiable, closure caps at 8.76e-7).

**The missed lever (HYPOTHESIS under test here): the leaders' 4-6x is SAMPLE
COUNT made affordable by wall-priced native execution, not analytic
superiority.** Two signals motivate it, but neither yet confirms 1/N holds to
the needed depth (that is what N1 tests): (i) arithmetic — joe_wanza's raw MSE
is 5.21e-8; the champion's is 3.089e-7 at N=64,512 fixed-frame samples,
implying design variance v = MSE*N ~= 0.0199 (post-antipodal, post-radial-
control); if the same estimator FAMILY runs at N' and MSE ~ v/N', then 5.21e-8
needs N' ~= 382,000 (5.9x). (ii) forensics — research_top_method_forensics
records 11/12 leaders running <0.1% of arithmetic through FlopScope, i.e. most
work native and residual-wall-priced. These make the count hypothesis PLAUSIBLE;
they do not establish that MSE keeps falling as 1/N past 64k rather than hitting
a hidden bias floor, nor that the champion's radial-control variance constant
survives 8x more samples. N1's kill gate is exactly that plateau.

## Why this is legal (Rules 5.2), and the honesty boundary

Rules 5.2 explicitly permits "any other library, backend, language,
executable, or bundled file"; work outside FlopScope is charged through
residual wall time (C = billed_FLOPs + 1e11*residual_seconds). Running the
sampler's matmul through raw numpy/BLAS (or a native kernel) is the intended
use of that channel. PROHIBITED and NOT done: FlopScope tampering, hiding work
from timing, moving metered work into setup() to evade S5.5, private-target or
grader reads. A production candidate MUST carry the full inclusive disclosure
(what runs native, how residual is priced) — drafted with the organizer packet.

## The compute arithmetic (the budget that funds the samples)

Score S = MSE * max(0.1, C/B), B = 2.72e11, C = billed + 1e11*residual_s.
- Below C/B = 0.1 (C <= 27.2B) the multiplier is CLAMPED: every FLOP under
  that line is score-free. A full-budget entry may spend up to C = B = 272B
  before invalidation, i.e. up to ~2.72 s of pure residual wall (at
  1e11 FLOP-eq/s) if billed FLOPs are ~0.
- The champion's forward is 155-215 matmuls of (64512,256)@(256,256); at N'
  samples it is (2N',256)@(256,256) x 31 layers ~= 2*N'*256*256*2*31 FLOPs
  ~= 2.6e9 * (N'/64512) raw MACs. On 16 vCPU AVX2 f32 (~200-800 GFLOP/s
  sustained), N'=382k costs ~0.04-0.15 s of wall — DEEP under budget.
- So the binding question is NOT "can we afford the samples" (we can, hugely)
  but "does MSE keep falling as ~1/N, or is there a hidden bias floor". That
  is exactly the N1 premise test.

## The compounding, stated correctly (supersedes the earlier arms framing)

This is ONE lever, not two: native execution buys sample count, sample count
buys MSE, and the leftover budget under the floor optionally funds a control
variate on top. The corpus's cheap-control kills were all cost-side kills
under the INSTRUMENTED budget; under the wall-priced budget the cost side
changes and some are worth reopening — but the DOMINANT term is raw sample
count, which needs no new mathematics, only the legal cost channel.

Projected altitude IF 1/N holds (own MSE only, no new control; this is the
conditional the test either confirms or kills): champion family at N'=516,096
(8x) -> MSE ~= 0.0199/516096 ~= 3.86e-8; at N'=1,032,192 (16x) -> ~1.93e-8.
Both below the top-12 cutoff (4.09e-8) under that assumption; 16x would land
between abhinav_gorrepati (2.30e-8) and huang_chung_yi (1.98e-8). Beating
joe_wanza (5.21e-8 raw) needs ~6x = N'~=382k; passing SKIBIDI (9.24e-8 raw)
needs ~2.5x = N'~=161k. Whether the floor is reachable by count alone is
precisely the open question N1 resolves — the projection is arithmetic on an
UNVERIFIED 1/N premise, not a result.

## N1 premise (this experiment) — cheapest falsifier first

On a GENERATED He-Gaussian d=256/L=32 MLP with own 8M-sample MC truth:
1. plain antipodal Gaussian-bank MSE scales ~1/N (v=MSE*N flat within 1.5x)
   from 64k through ~516k samples — NO hidden bias plateau;
2. the raw-path forward wall at those N is a small fraction of the ~2.7 s
   budget (local laptop = lower bound on 16-vCPU grading throughput);
3. deterministic under fixed seeds.

KILL: v grows >1.5x by 516k (bias floor), or local wall > 20 s (throughput
implausible), or nondeterminism. A pass makes the count-scaling route the
campaign's PRIMARY #1 path; the exact analytic controls (M178/M179 chain)
become the ADD-ON that spends the residual budget, and the Algorithmic
Contribution paper.

## Firewall / next-step gates

- No deploy without organizer answer (native pricing legal? floor 0.1?) + user
  go. The N1 test is science, not submission.
- The champion's exact radial/antipodal control (v=0.0199) is the frame this
  scales; the SOURCE is in row_blocked_production/candidate_source. Scaling N
  is a FAMILY move, re-using the champion's variance constant, not a new
  estimator — but a graded submission is the only way to confirm the grading-
  hardware throughput and the floor, which is the highest-information step.
