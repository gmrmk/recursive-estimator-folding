"""A1: hosted per-MLP ledger of #326094 (scraped 2026-08-08) + tail analysis.

Columns: idx, name, adj, vs_sampling, final_mse, all_layer_mse, flops, wall_ms.
"""
import json
from pathlib import Path

import numpy as np

ROWS = [
 (0,"patricia-hawkins",5.42e-8,12.0,7.52e-8,6.01e-4,1.89e11,5716.9),
 (12,"noah-delgado",5.56e-8,12.0,8.15e-8,7.76e-4,1.78e11,5374.9),
 (26,"zachary-velazquez",5.95e-8,11.0,9.28e-8,9.92e-4,1.66e11,5998.9),
 (7,"amy-osborne",6.70e-8,9.7,8.83e-8,4.90e-4,2.00e11,5207.2),
 (17,"lauren-johnson",7.17e-8,9.0,1.01e-7,6.85e-4,1.86e11,5857.1),
 (36,"emily-taylor",8.28e-8,7.8,1.31e-7,1.3e-3,1.64e11,5796.4),
 (48,"christopher-daniels",8.44e-8,7.7,1.31e-7,5.36e-4,1.66e11,6598.6),
 (30,"kimberly-henderson",8.51e-8,7.6,1.23e-7,6.62e-4,1.80e11,5660.2),
 (35,"tonya-wheeler",9.14e-8,7.1,1.34e-7,6.99e-4,1.76e11,6133.3),
 (22,"heather-brown",9.22e-8,7.0,1.36e-7,6.22e-4,1.76e11,5954.6),
 (27,"gregory-anderson",9.35e-8,6.9,1.36e-7,9.33e-4,1.77e11,6780.0),
 (47,"dylan-meyer",9.93e-8,6.5,1.54e-7,6.40e-4,1.69e11,4995.4),
 (44,"joseph-tucker",1.05e-7,6.2,1.64e-7,1.1e-3,1.66e11,5991.3),
 (39,"mandy-acosta",1.06e-7,6.1,1.64e-7,7.81e-4,1.69e11,5757.7),
 (34,"angela-brown",1.09e-7,5.9,1.65e-7,6.59e-4,1.73e11,5870.7),
 (10,"kelly-hart",1.09e-7,5.9,1.63e-7,6.81e-4,1.74e11,5892.7),
 (38,"austin-duffy",1.13e-7,5.7,1.78e-7,8.74e-4,1.65e11,5886.4),
 (23,"maria-mcintosh",1.20e-7,5.4,1.82e-7,7.40e-4,1.70e11,6403.2),
 (15,"jordan-sims",1.26e-7,5.1,1.79e-7,6.48e-4,1.84e11,5357.0),
 (18,"christopher-reese",1.29e-7,5.0,1.86e-7,6.98e-4,1.81e11,5454.7),
 (46,"dawn-brown",1.35e-7,4.8,1.96e-7,1.1e-3,1.80e11,5796.8),
 (16,"michael-byrd",1.50e-7,4.3,2.27e-7,8.76e-4,1.72e11,5681.0),
 (32,"jennifer-edwards",1.51e-7,4.3,2.26e-7,6.54e-4,1.74e11,5921.9),
 (14,"wanda-sanders",1.57e-7,4.1,2.39e-7,9.99e-4,1.71e11,5986.9),
 (3,"lisa-molina",1.61e-7,4.0,2.35e-7,6.91e-4,1.79e11,5560.5),
 (6,"bruce-mckenzie",1.63e-7,4.0,2.41e-7,8.79e-4,1.77e11,5942.4),
 (49,"brian-holmes",1.64e-7,4.0,2.49e-7,4.42e-4,1.73e11,4613.1),
 (24,"danielle-bird",1.64e-7,3.9,2.40e-7,1.7e-3,1.79e11,5104.7),
 (45,"robert-fernandez",1.71e-7,3.8,2.60e-7,9.49e-4,1.70e11,6071.5),
 (25,"paul-smith",1.74e-7,3.7,2.72e-7,7.15e-4,1.66e11,5901.2),
 (43,"joshua-aguilar",1.75e-7,3.7,2.94e-7,8.48e-4,1.55e11,5217.2),
 (9,"donald-henderson",1.76e-7,3.7,2.59e-7,5.67e-4,1.76e11,6795.3),
 (8,"cory-lane",1.81e-7,3.6,2.76e-7,7.79e-4,1.71e11,6115.7),
 (41,"gary-miranda",1.95e-7,3.3,3.03e-7,7.42e-4,1.68e11,5524.8),
 (11,"gina-campbell",2.10e-7,3.1,3.28e-7,5.42e-4,1.67e11,5370.0),
 (20,"erin-maddox",2.12e-7,3.1,3.18e-7,9.88e-4,1.74e11,5436.1),
 (2,"joshua-roberts",2.25e-7,2.9,3.74e-7,8.41e-4,1.56e11,5550.8),
 (29,"roberto-bray",2.26e-7,2.9,3.71e-7,8.65e-4,1.60e11,4809.4),
 (4,"elizabeth-james",2.28e-7,2.8,3.66e-7,8.67e-4,1.62e11,5749.2),
 (28,"bryan-hines",2.31e-7,2.8,3.53e-7,6.47e-4,1.70e11,6447.2),
 (42,"sheila-palmer",2.45e-7,2.6,4.01e-7,1.1e-3,1.58e11,6357.3),
 (40,"curtis-townsend",2.46e-7,2.6,3.96e-7,8.52e-4,1.62e11,5388.8),
 (19,"monica-brown",2.53e-7,2.6,3.84e-7,7.06e-4,1.72e11,5623.3),
 (37,"joseph-vasquez",2.86e-7,2.3,4.74e-7,1.2e-3,1.56e11,5843.7),
 (31,"benjamin-gardner",3.16e-7,2.0,4.67e-7,5.78e-4,1.76e11,6058.5),
 (13,"justin-johnston",3.68e-7,1.8,5.37e-7,9.24e-4,1.79e11,5559.5),
 (21,"chad-yates",4.24e-7,1.5,6.87e-7,7.40e-4,1.62e11,4647.4),
 (33,"william-gilbert",4.25e-7,1.5,6.48e-7,9.08e-4,1.71e11,6008.4),
 (1,"angela-walker",4.95e-7,1.3,7.89e-7,9.95e-4,1.63e11,5426.3),
 (5,"patricia-neal",5.96e-7,1.1,9.13e-7,9.67e-4,1.69e11,6286.3),
]


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def main():
    adj = np.array([r[2] for r in ROWS])
    vs = np.array([r[3] for r in ROWS])
    fmse = np.array([r[4] for r in ROWS])
    amse = np.array([r[5] for r in ROWS])
    fl = np.array([r[6] for r in ROWS])
    wall = np.array([r[7] for r in ROWS])

    # Implied per-net MC baseline: vs_sampling = baseline_m / adj_m
    mc_m = vs * adj

    print("== A1 hosted tail analysis (#326094, 50 public MLPs) ==")
    print(f"adj: mean {adj.mean():.3e}  min {adj.min():.3e}  max {adj.max():.3e}  max/min {adj.max()/adj.min():.1f}x")
    print(f"implied per-net MC baseline: mean {mc_m.mean():.3e}  spread {mc_m.min():.2e}..{mc_m.max():.2e}  max/min {mc_m.max()/mc_m.min():.1f}x")
    print()
    for name, v in (("billed FLOPs", fl), ("wall ms", wall), ("all-layer MSE", amse),
                    ("implied MC baseline (v_m proxy)", mc_m)):
        print(f"spearman(adj, {name:32s}) = {spearman(adj, v):+.3f}")
    print(f"spearman(adj, vs_sampling)                 = {spearman(adj, vs):+.3f}  (tautological check)")
    print()
    # top vs bottom decile contrast
    k = 5
    order = np.argsort(adj)
    best, worst = order[:k], order[-k:]
    for name, v in (("billed FLOPs", fl), ("wall ms", wall), ("all-layer MSE", amse), ("MC baseline", mc_m)):
        b, w = v[best].mean(), v[worst].mean()
        pooled = v.std()
        print(f"decile contrast {name:22s}: best {b:.3e}  worst {w:.3e}  std-diff {(w-b)/pooled:+.2f}")
    print()
    print("KEY QUESTION: does the design advantage (vs_sampling) collapse because")
    print("our MSE rises, the MC baseline falls, or both?")
    print(f"  corr(log adj, log mc_m)   = {np.corrcoef(np.log(adj), np.log(mc_m))[0,1]:+.3f}")
    print(f"  worst-5 MC baseline mean  = {mc_m[worst].mean():.3e} vs best-5 {mc_m[best].mean():.3e}")
    print(f"  worst-5 adj/mc ratio      = {(adj[worst]/mc_m[worst]).mean():.3f} vs best-5 {(adj[best]/mc_m[best]).mean():.3f}")

    out = {"rows": [dict(zip(["idx","name","adj","vs_sampling","final_mse","all_layer_mse","flops","wall_ms"], r)) for r in ROWS]}
    Path(__file__).with_name("a1_hosted_ledger.json").write_text(json.dumps(out, indent=1) + "\n")
    print("\nwrote a1_hosted_ledger.json")


if __name__ == "__main__":
    main()
