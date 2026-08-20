"""S11 design verification: confirm the 126->129 frame completion is an exact
antipodal spherical 5-design (deg-4 quadrature error identically 0) via the
exact projective-2-design 4th-moment (Welch) identity.

126 frames = phased-Hadamard indices [2:128] (the frozen v3 sampler set).
Completion adds 3 frames: phased-Hadamard indices 0 and 1 (the 2 trimmed off
the 128-frame Kerdock set) + the standard/coordinate basis.

Unit directions only (radius and Haar rotation are irrelevant to the angle
set / design strength, which is rotation-invariant). READ-ONLY on the asset.
"""
from __future__ import annotations
import numpy as np
from pathlib import Path

V3 = Path(r"C:\Users\strid\Documents\Codex\2026-08-02"
          r"\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation"
          r"\kerdock_l1_owned_buffer\candidate_source_validator_v3")
W = 256

def hadamard_norm():
    H = np.array([[1.0]])
    while H.shape[0] < W:
        H = np.block([[H, H], [H, -H]])
    return H / 16.0            # unit rows (256 * (1/16)^2 = 1)

def phased_frames():
    packed = np.load(V3 / "kerdock_phases.npz")["negative_bits"]
    neg = np.unpackbits(packed, axis=1, bitorder="little")[:, :W]
    return (1.0 - 2.0 * neg.astype(np.float64))   # (128, 256) in +/-1

def frame_units(phase_row, hN):
    # 256 unit directions of a phased-Hadamard frame: hN[i] * phase
    return hN * phase_row[None, :]                 # (256, 256), unit rows

def main():
    hN = hadamard_norm()
    phases = phased_frames()
    std = np.eye(W)                                # coordinate frame, unit rows

    # 126-frame set (the frozen sampler) and the 3 completion frames
    idx126 = list(range(2, 128))
    frames126 = [frame_units(phases[f], hN) for f in idx126]
    add_frames = [frame_units(phases[0], hN),
                  frame_units(phases[1], hN),
                  std]
    frames129 = frames126 + add_frames

    def stack(fr):
        return np.concatenate(fr, axis=0)          # (nframes*256, 256)

    V126 = stack(frames126)                        # (32256, 256)
    V129 = stack(frames129)                        # (33024, 256)
    # sanity: unit norms
    assert np.allclose(np.linalg.norm(V126, axis=1), 1.0, atol=1e-12)
    assert np.allclose(np.linalg.norm(V129, axis=1), 1.0, atol=1e-12)

    d = W
    welch = 3.0 / (d * (d + 2.0))                  # projective-2-design 4th moment

    def per_line_sum4(V, sample_rows):
        # sum_j <v_i, v_j>^4 over ALL lines j, for i in sample_rows
        G = V[sample_rows] @ V.T                    # (|sample|, N_L)
        return (G ** 4).sum(axis=1)

    def frame_potential(V, sample_rows):
        # (1/N_L) * mean_i sum_j <v_i,v_j>^4  == Phi_4 estimate on sample
        pls = per_line_sum4(V, sample_rows)
        return pls, pls.mean() / V.shape[0]

    rng = np.random.default_rng(0)
    # sample lines: force-include frame 0, frame 1, and standard-basis lines
    # (rows within V129: 126 frames -> [0:32256); add0 [32256:32512);
    #  add1 [32512:32768); std [32768:33024))
    sample129 = np.concatenate([
        np.array([32256, 32257, 32300,       # frame-0 (all-ones Hadamard)
                  32512, 32513, 32600,        # frame-1
                  32768, 32769, 32900]),      # standard basis
        rng.integers(0, 32256, size=200)      # spread over the 126 base frames
    ])
    pls129, phi129 = frame_potential(V129, sample129)

    sample126 = rng.integers(0, 32256, size=200)
    pls126, phi126 = frame_potential(V126, sample126)

    # exact distinct inner-product values across all cross pairs from frame-0,
    # frame-1, std against everything (the "one assumption" unbiasedness check)
    def cross_vals(block_rows, V):
        G = V[block_rows] @ V.T
        # zero out self (diagonal within the block) then look at |values|
        return G
    g0 = cross_vals(np.arange(32256, 32512), V129)   # frame-0 vs all 129
    g1 = cross_vals(np.arange(32512, 32768), V129)
    gs = cross_vals(np.arange(32768, 33024), V129)

    def summarize(G, name, self_offset):
        # within own frame block the off-diagonal should be 0; cross should be +-1/16
        absv = np.abs(np.round(G, 10))
        uniq = np.unique(np.round(np.abs(G), 6))
        print(f"  {name}: distinct |<.,.>| (rounded 6dp) = {uniq[:12]}"
              f"{' ...' if len(uniq) > 12 else ''}")
        # count how many cross-frame products deviate from {0, 1/16, 1}
        allowed = {0.0, round(1/16, 6), 1.0}
        bad = np.array([u for u in uniq if round(u, 6) not in allowed])
        print(f"    off-set values (not in {{0,1/16,1}}): {bad}")

    print("=== Unbiasedness of the 3 completion frames vs all 129 ===")
    summarize(g0, "frame-0 (all-ones Hadamard) vs all", 0)
    summarize(g1, "frame-1 vs all", 0)
    summarize(gs, "standard basis vs all", 0)

    print("\n=== 4th-moment / 5-design certificate ===")
    print(f"  Welch (projective-2-design) target 3/(d(d+2)) = {welch:.10e}")
    print(f"  126-frame per-line sum4: mean {pls126.mean():.10f} "
          f"(theory 1.48828), min {pls126.min():.6f} max {pls126.max():.6f}")
    print(f"  126-frame Phi_4 = {phi126:.10e}  ratio/Welch = {phi126/welch:.6f}")
    print(f"  129-frame per-line sum4: mean {pls129.mean():.12f} "
          f"(theory 1.5), min {pls129.min():.10f} max {pls129.max():.10f}")
    print(f"  129-frame Phi_4 = {phi129:.12e}  ratio/Welch = {phi129/welch:.10f}")
    # per-frame breakdown for the 3 added frames (must each be exactly 1.5)
    for lo, nm in [(0, "frame-0"), (3, "frame-1"), (6, "standard")]:
        print(f"    {nm} sample per-line sum4 = {pls129[lo:lo+3]}")

    # deg-4 variance excess in Haar/iid terms:
    # excess frame potential over Welch, normalized; 129 should be ~0.
    print("\n=== deg-4 error (frame-potential excess over the 2-design floor) ===")
    print(f"  126: Phi_4/Welch - 1 = {phi126/welch - 1:.6e}")
    print(f"  129: Phi_4/Welch - 1 = {phi129/welch - 1:.6e}")

if __name__ == "__main__":
    main()
