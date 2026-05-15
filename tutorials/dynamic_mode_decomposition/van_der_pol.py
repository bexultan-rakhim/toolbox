"""
Dynamic Mode Decomposition demo  polynomial (data-orthogonal), and RBF dictionary 
on the Van der Pol oscillator.

All three methods implemented from scratch with a common interface:

  1. Vanilla DMD                  — linear operator on raw state (x1, x2).
  2. Polynomial EDMD (orthogonal) — monomial basis Gram-Schmidt orthogonalized
                                    under the empirical data measure (Cholesky).
                                    Avoids the conditioning blowup of raw or
                                    Legendre polynomials at moderate-to-high degree.
  3. RBF EDMD                     — Gaussian RBF features centered on training data,
                                    with ridge regularization.
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt


# The nonlinear system: Van der Pol oscillator
EPS = 1.0


def vanderpol(t, x):
    x1, x2 = x
    return [x2, EPS * (1 - x1**2) * x2 - x1]


dt = 0.02
t_end = 25.0
t_eval = np.arange(0, t_end + dt, dt)
n_steps = len(t_eval)


# Generate training and test trajectories
ICs_train = [[x1, x2] for x1 in np.linspace(-2.5, 2.5, 5)
             for x2 in np.linspace(-2.5, 2.5, 5)
             if abs(x1) + abs(x2) > 0.1]
trajs = []
for ic in ICs_train:
    sol = solve_ivp(vanderpol, [0, t_end], ic, t_eval=t_eval,
                    rtol=1e-10, atol=1e-12)
    if sol.success:
        trajs.append(sol.y)

X_test = solve_ivp(vanderpol, [0, t_end], [1.5, -1.0],
                   t_eval=t_eval, rtol=1e-10, atol=1e-12).y

print(f"Generated {len(trajs)} training trajectories x {n_steps} snapshots.")

X_data_all = np.hstack(trajs)
X_MAX = np.max(np.abs(X_data_all))   # data scale for normalization


# Common helpers
def stack_snapshots(traj_list):
    X = np.hstack([t[:, :-1] for t in traj_list])
    Y = np.hstack([t[:, 1:] for t in traj_list])
    return X, Y


def fit_operator(Psi_X, Psi_Y, lam=0.0):
    """Solve Psi_Y ~ K Psi_X."""
    if lam == 0.0:
        return Psi_Y @ np.linalg.pinv(Psi_X)
    N = Psi_X.shape[0]
    G = Psi_X @ Psi_X.T + lam * np.eye(N)
    return Psi_Y @ Psi_X.T @ np.linalg.solve(G, np.eye(N))


# Dictionaries
def identity_lift(X):
    """Vanilla lift"""
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    return X.copy()


def monomial_powers(degree):
    return [(i, d-i) for d in range(degree+1) for i in range(d+1)]


def eval_monomials(X, powers, scale=1.0):
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    x1, x2 = X[0]/scale, X[1]/scale
    return np.vstack([(x1**i)*(x2**j) for (i, j) in powers])


def build_orthogonal_basis(X_data, degree, scale=1.0):
    powers = monomial_powers(degree)
    M = eval_monomials(X_data, powers, scale)
    N = M.shape[1]
    G = (M @ M.T) / N
    eps_chol = 1e-14 * np.trace(G) / G.shape[0]
    L = np.linalg.cholesky(G + eps_chol * np.eye(G.shape[0]))
    T = np.linalg.solve(L, np.eye(L.shape[0]))
    return powers, T, scale


def eval_orthogonal_basis(X, powers, T, scale):
    "polynomial lift"
    return T @ eval_monomials(X, powers, scale)


def rbf_lift(X, centers, eps_rbf):
    """Lift to [1, x1, x2, RBF_1(x), ..., RBF_n(x)]."""
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    T_data = X.shape[1]
    feats = [np.ones(T_data), X[0], X[1]]
    for i in range(centers.shape[1]):
        d2 = (X[0] - centers[0, i])**2 + (X[1] - centers[1, i])**2
        feats.append(np.exp(-eps_rbf * d2))
    return np.vstack(feats)


# Unified Koopman model
class KoopmanModel:
    def __init__(self, name, lift_fn, lam=0.0,
                 readout_mode='index', readout_x1=None, readout_x2=None):
        self.name = name
        self.lift_fn = lift_fn
        self.lam = lam
        self.readout_mode = readout_mode
        self.readout_x1 = readout_x1   # int or (int, scale) tuple or vector
        self.readout_x2 = readout_x2
        self.K = None

    def fit(self, traj_list):
        Psi_X, Psi_Y = stack_snapshots([self.lift_fn(t) for t in traj_list])
        self.K = fit_operator(Psi_X, Psi_Y, lam=self.lam)
        self.Psi_X, self.Psi_Y = Psi_X, Psi_Y
        return self

    def _readout(self, psi):
        if self.readout_mode == 'index':
            if isinstance(self.readout_x1, tuple):
                i, s = self.readout_x1
                x1 = psi[i] * s
                i, s = self.readout_x2
                x2 = psi[i] * s
            else:
                x1 = psi[self.readout_x1]
                x2 = psi[self.readout_x2]
        else:   # 'vector'
            x1 = self.readout_x1 @ psi
            x2 = self.readout_x2 @ psi
        return x1, x2

    def predict(self, x0, n):
        psi = self.lift_fn(np.asarray(x0).reshape(2, 1)).flatten()
        out = np.zeros((2, n))
        out[:, 0] = x0
        for k in range(n - 1):
            psi = self.K @ psi
            out[:, k+1] = self._readout(psi)
        return out

    def eigenvalues(self):
        return np.linalg.eigvals(self.K)


# Set up the three models

## Vanilla DMD
model_dmd = KoopmanModel(
    name="Vanilla DMD",
    lift_fn=identity_lift,
    lam=0.0,
    readout_mode='index',
    readout_x1=0, readout_x2=1   # state IS the lifted vector
)

## Polynomial EDMD with data-orthogonal basis
POLY_DEGREE = 17
powers_o, T_o, scale_o = build_orthogonal_basis(
    X_data_all, POLY_DEGREE, scale=X_MAX)

# Readout vectors: x1 = w_x1 @ Phi, x2 = w_x2 @ Phi.
# Recovered from: Phi(x) = T @ M(x), so to extract M[k] we need w with T.T @ w = e_k.
# x1 lives at monomial index 2 (the (1,0) monomial), value = x1/scale -> multiply by scale.
# x2 lives at monomial index 1 (the (0,1) monomial).
w_x1_poly = np.linalg.solve(T_o.T, np.eye(T_o.shape[0])[:, 2]) * scale_o
w_x2_poly = np.linalg.solve(T_o.T, np.eye(T_o.shape[0])[:, 1]) * scale_o

model_poly = KoopmanModel(
    name=f"Polynomial EDMD (deg {POLY_DEGREE}, data-orthogonal)",
    lift_fn=lambda X: eval_orthogonal_basis(X, powers_o, T_o, scale_o),
    lam=1e-10,
    readout_mode='vector',
    readout_x1=w_x1_poly, readout_x2=w_x2_poly
)

## RBF EDMD. size matched to polynomial: N_poly = 171 -> n_centers = 168
np.random.seed(0)
N_CENTERS = 168
EPS_RBF = 5.0 # you can tune paramters to find one that performs good
RIDGE_LAM = 1e-1
center_idx = np.random.choice(X_data_all.shape[1], N_CENTERS, replace=False)
centers = X_data_all[:, center_idx]

model_rbf = KoopmanModel(
    name=f"RBF EDMD ({N_CENTERS} centers, λ={RIDGE_LAM:.0e})",
    lift_fn=lambda X: rbf_lift(X, centers, EPS_RBF),
    lam=RIDGE_LAM,
    readout_mode='index',
    readout_x1=1,   # rbf_lift returns [1, x1, x2, RBFs...]
    readout_x2=2
)

models = [model_dmd, model_poly, model_rbf]


# Fit and report diagnostics
def print_matrix(M, max_show=10, fmt="{:8.4f}"):
    """Pretty-print a matrix, truncating large ones."""
    n, m = M.shape
    show_n = min(n, max_show)
    show_m = min(m, max_show)
    for i in range(show_n):
        row = "  "
        for j in range(show_m):
            v = M[i, j]
            row += fmt.format(v) + " "
        if m > max_show:
            row += f"  ...({m - max_show} more cols)"
        print(row)
    if n > max_show:
        print(f"  ... ({n - max_show} more rows)")


def print_eigenvalues(eigs, dt, top_k=8):
    order = np.argsort(-np.abs(eigs))
    eigs = eigs[order][:top_k]
    print(f"  {'idx':>4} {'|mu|':>8} {'mu (discrete)':>26} "
          f"{'omega = log(mu)/dt':>26} {'freq (Hz)':>10}")
    for i, mu in enumerate(eigs):
        if abs(mu) < 1e-15:
            omega_str = "(singular)"
            freq_str = "    -    "
        else:
            omega = np.log(complex(mu)) / dt
            omega_str = f"({omega.real:+.4f}{omega.imag:+.4f}j)"
            freq_str = f"{abs(omega.imag)/(2*np.pi):>10.4f}"
        mu_str = f"({mu.real:+.4f}{mu.imag:+.4f}j)"
        print(f"  {i:>4d} {abs(mu):>8.4f} {mu_str:>26} {omega_str:>26} {freq_str}")


print()
for m in models:
    m.fit(trajs)
    eigs = m.eigenvalues()
    print("=" * 90)
    print(f"{m.name}")
    print("=" * 90)
    print(f"  Dictionary size N = {m.Psi_X.shape[0]}")
    print(f"  cond(Psi_X)       = {np.linalg.cond(m.Psi_X):.2e}")
    print(f"  ||K||_2           = {np.linalg.norm(m.K, 2):.4f}")
    print(f"  spectral radius   = {np.max(np.abs(eigs)):.6f}")

    if m.K.shape[0] <= 10:
        print(f"\n  K matrix:")
        print_matrix(m.K)

    print(f"\n  Top eigenvalues (sorted by |mu|):")
    print_eigenvalues(eigs, dt, top_k=8)
    print()


# Evaluate predictions
preds = {m.name: m.predict(X_test[:, 0], n_steps) for m in models}


def horizon_error(model, X_traj, horizons, step=5):
    errs = []
    for h in horizons:
        starts = np.arange(0, X_traj.shape[1] - h, step)
        e = 0.0
        for s in starts:
            pred = model.predict(X_traj[:, s], h+1)
            e += np.linalg.norm(pred[:, -1] - X_traj[:, s+h])
        errs.append(e / len(starts))
    return np.array(errs)


horizons = np.array([1, 5, 10, 20, 50, 100, 200, 500, 1000])
errs_by_model = {m.name: horizon_error(m, X_test, horizons) for m in models}

print("=" * 90)
print("Free-running prediction error vs horizon (test trajectory, unseen IC)")
print("=" * 90)
header = f"{'h':>5} {'time(s)':>8}"
for m in models:
    header += f"  {m.name[:25]:>27}"
print(header)
for i, h in enumerate(horizons):
    row = f"{h:>5d} {h*dt:>8.2f}"
    for m in models:
        row += f"  {errs_by_model[m.name][i]:>27.5f}"
    print(row)


# Plot
colors = {
    model_dmd.name:  'red',
    model_poly.name: 'purple',
    model_rbf.name:  'green'
}
styles = {
    model_dmd.name:  '--',
    model_poly.name: '-',
    model_rbf.name:  '-'
}

fig = plt.figure(figsize=(15, 10))
gs = fig.add_gridspec(3, 3, hspace=0.42, wspace=0.32)

# Phase portrait
ax = fig.add_subplot(gs[0:2, 0:2])
ax.plot(X_test[0], X_test[1], 'k-', lw=2.6, label='Truth (Van der Pol)')
for m in models:
    p = preds[m.name]
    ax.plot(p[0], p[1], color=colors[m.name], ls=styles[m.name],
            lw=1.4, label=m.name, alpha=0.9)
ax.scatter(*X_test[:, 0], c='lime', s=160, edgecolor='k', linewidth=2,
           zorder=5, label='$x_0$')
ax.set_xlabel('$x_1$', fontsize=12)
ax.set_ylabel('$x_2$', fontsize=12)
ax.set_title('Phase portrait — free-running prediction from $x_0$', fontsize=12)
ax.legend(fontsize=9, loc='best')
ax.grid(alpha=0.3)
ax.set_aspect('equal')

# Error vs horizon
ax = fig.add_subplot(gs[0, 2])
for m in models:
    ax.loglog(horizons * dt, errs_by_model[m.name], 'o-',
              color=colors[m.name], label=m.name[:22], lw=2, markersize=6)
ax.set_xlabel('horizon (s)')
ax.set_ylabel('prediction error')
ax.set_title('Error vs horizon (log-log)')
ax.legend(fontsize=7)
ax.grid(alpha=0.3, which='both')

# Spectrum
ax = fig.add_subplot(gs[1, 2])
theta = np.linspace(0, 2*np.pi, 200)
ax.plot(np.cos(theta), np.sin(theta), 'k-', lw=0.5)
for m, marker, size in zip(models, ['o', 's', '^'], [120, 30, 25]):
    eigs = m.eigenvalues()
    ax.scatter(eigs.real, eigs.imag, c=colors[m.name], s=size,
               marker=marker, edgecolor='k', linewidth=0.5,
               label=f'{m.name[:18]} ({len(eigs)})', zorder=3, alpha=0.85)
ax.set_xlabel('Re $\\mu$')
ax.set_ylabel('Im $\\mu$')
ax.set_title('Discrete-time spectrum')
ax.legend(fontsize=7)
ax.grid(alpha=0.3)
ax.set_aspect('equal')
ax.set_xlim(-1.15, 1.15)
ax.set_ylim(-1.15, 1.15)

# x1(t)
ax = fig.add_subplot(gs[2, :])
ax.plot(t_eval, X_test[0], 'k-', lw=2, label='Truth')
for m in models:
    ax.plot(t_eval, preds[m.name][0], color=colors[m.name],
            ls=styles[m.name], lw=1.3, label=m.name, alpha=0.9)
ax.set_xlabel('t')
ax.set_ylabel('$x_1$')
ax.set_title('$x_1(t)$ — full 25 s prediction')
ax.legend(loc='upper right', fontsize=8, ncol=4)
ax.grid(alpha=0.3)

plt.suptitle('Van der Pol ($\\epsilon=1$): DMD vs Polynomial EDMD (orthogonal) vs RBF EDMD',
             fontsize=14, fontweight='bold', y=0.995)

import os
os.makedirs('outputs', exist_ok=True)
plt.savefig('outputs/dmd_edmd_rbf_final.png', dpi=130, bbox_inches='tight')
print("\nSaved -> outputs/dmd_edmd_rbf_final.png")
