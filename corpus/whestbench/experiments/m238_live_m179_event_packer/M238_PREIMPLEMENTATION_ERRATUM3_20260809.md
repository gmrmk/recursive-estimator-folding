# M238 preimplementation erratum 3 -- ordered embedding and gauge action

Date: 2026-08-09. Status: `SEALED_BEFORE_CODE_AND_TESTS`.

This erratum supersedes only the embedding map and corresponding digests in
erratum 1, and specifies the already-declared gauge test's tape action. No code
or test existed when it was sealed.

## Order-preserving spread embedding

For one-based layer `ell`, the canonical seven target positions are

```text
map_ell = sort(Generator(Philox(238730000+ell)).permutation(256)[:7]).
```

The sort occurs only in deterministic, untimed receipt/tape construction. It
is not a permitted packer-time sort. Because the parent local singleton labels
are canonical, `j_local<k_local` now implies target `j<k` exactly. Every frozen
receipt has zero order failures.

The canonical serialization rule from erratum 1 is unchanged. Replacement
digests are:

```text
tape a,C,mu,V,p,r:
  2012133C1CDA19C695B94F0E54A033DD3B1694AC2A009DADA9DADE68AA36FE3C

event receipt 221720001:
  CF4A9464DE22B0BB58985D51B26C133C528FDFD58BC073C9ED4C654E8FE785D0
event receipt 221720002:
  0A77C775907EF12CB9DCD4EE88F9818442EA57B8B830A3958E922D92D2CAB1A9
event receipt 221720003:
  E871DD5C844D84CF2F2F3F7CAC0AE74F2DA33060659059CDA7EB41638D8C0ACC
event receipt 221720004:
  0198644F60AD8297E3D7CC4551473AD71C116C4AD1BAF1A5F1841B96AF9E50A0
event receipt 221720005:
  50AC56BEDDE4309630C9BC457DBE1920CB7611131B700CAEEB1904F34918B418
```

The adversarial repeat uses the first replacement digest. The frozen
nondegeneracy facts remain zero exact zeros and minimum absolute selected
`Vij,Vik,Vjk` value `2.9276288362745095e-06`.

## Exact gauge action on the tape

For an arbitrary positive float64 vector `dq`, G0A constructs one transformed
tape and keeps receipt labels and `g` unchanged:

```text
a'[q]   = dq*a[q]
C'[q,r] = dq*dr*C[q,r]
mu'[q]  = dq*mu[q]
V'[q,r] = dq*dr*V[q,r]
p'[q]   = p[q]
r'[q]   = r[q]/dq.
```

Layer, epoch, shape, and provenance co-act into a new hostile-test context;
the baseline context is not mutated. These transformations imply
`eta2'[q]=eta2[q]/dq` and `eta3'[q]=eta3[q]/dq^2`, making the frozen
`di^2*dj*dk` tree degree and every other output degree directly executable.

