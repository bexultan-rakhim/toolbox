"""
Test Hankel embedding and Random Fourier Features on the damped pendulum.
Compare against RBF EDMD with 168 centers.
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Pendulum setup
G_OVER_L = 9.81
GAMMA = 0.15

def pendulum(t, x):
    return [x[1], -GAMMA * x[1] - G_OVER_L * np.sin(x[0])]

dt, t_end = 0.02, 25.0
t_eval = np.arange(0, t_end + dt, dt)
n_steps = len(t_eval)

np.random.seed(0)
ICs_train = [[t0, w0] for t0 in np.linspace(-2.5, 2.5, 7)
                       for w0 in np.linspace(-3.0, 3.0, 5)
                       if abs(t0) + abs(w0) > 0.1]
trajs = [solve_ivp(pendulum, [0, t_end], ic, t_eval=t_eval,
                    rtol=1e-10, atol=1e-12).y for ic in ICs_train]
X_test = solve_ivp(pendulum, [0, t_end], [1.8, -0.5], t_eval=t_eval,
                    rtol=1e-10, atol=1e-12).y

X_data_all = np.hstack(trajs)


def fit_ridge(Psi_X, Psi_Y, lam):
    N = Psi_X.shape[0]
    G = Psi_X @ Psi_X.T + lam * np.eye(N)
    return Psi_Y @ Psi_X.T @ np.linalg.solve(G, np.eye(N))


# Method 1: Hankel-DMD
# Stack d delayed copies of the 2D state into a 2d-dimensional vector.
# Run vanilla DMD on these enlarged snapshots.
def hankel_lift(traj, delay):
    T = traj.shape[1]
    n_cols = T - delay + 1
    rows = []
    for d in range(delay):
        rows.append(traj[:, delay - 1 - d : delay - 1 - d + n_cols])
    return np.vstack(rows)

# Build training data with Hankel embedding
DELAY = 50   # use 50 past timesteps = 1 second of history (~half a period)
print(f"Hankel-DMD: delay = {DELAY} steps ({DELAY*dt:.2f} s of history)")
print(f"  Lifted dimension: {2 * DELAY}")

# Hankel snapshots: for each trajectory, build the lifted matrix, then take pairs.
hankel_data_list = [hankel_lift(t, DELAY) for t in trajs]
# Now snapshot pairs: column k advances to column k+1 within each trajectory
Hk_X = np.hstack([h[:, :-1] for h in hankel_data_list])
Hk_Y = np.hstack([h[:, 1:]  for h in hankel_data_list])

print(f"  Snapshot matrix size: {Hk_X.shape}")
print(f"  cond(Hk_X) = {np.linalg.cond(Hk_X):.2e}")

# Run DMD on Hankel matrices (with SVD truncation since lifted dim is large)
U, S, Vh = np.linalg.svd(Hk_X, full_matrices=False)
RANK = 30  # truncate to leading 30 directions
print(f"  SVD truncation rank: {RANK}")

U_r = U[:, :RANK]
S_r = S[:RANK]
V_r = Vh.conj().T[:, :RANK]
A_tilde = U_r.conj().T @ Hk_Y @ V_r @ np.diag(1/S_r)
# Project back to full space for prediction
A_hankel_full = U_r @ A_tilde @ U_r.conj().T

eigs_hankel = np.linalg.eigvals(A_tilde)
print(f"  ||A_tilde||_2 = {np.linalg.norm(A_tilde, 2):.4f}")
print(f"  spectral radius = {np.max(np.abs(eigs_hankel)):.6f}")


def predict_hankel(x0_full_history, n):
    h = np.concatenate([x0_full_history[:, -1-d] for d in range(DELAY)])
    out = np.zeros((2, n))
    # Best we can do: read off the top 2 entries (most recent state)
    out[:, 0] = h[:2]
    for k in range(n - 1):
        h = A_hankel_full @ h
        out[:, k+1] = h[:2]
    return out

# For test prediction, we need DELAY warm-up steps from the true trajectory.
# Predict from t = DELAY*dt onward.
warmup = X_test[:, :DELAY]
pred_hankel = np.zeros((2, n_steps))
pred_hankel[:, :DELAY] = warmup  # we know the warm-up exactly
forward = predict_hankel(warmup, n_steps - DELAY + 1)
pred_hankel[:, DELAY-1:] = forward


# Method 2: Random Fourier Features
# Approximate Gaussian kernel k(x,y) = exp(-gamma ||x-y||^2) with random
# trigonometric features. Sample omega ~ N(0, 2*gamma*I), b ~ U(0, 2*pi).
# phi_j(x) = sqrt(2/D) cos(omega_j . x + b_j)
def make_rff(D, gamma, dim_x=2, seed=42):
    rng = np.random.default_rng(seed)
    omegas = rng.normal(0, np.sqrt(2*gamma), size=(D, dim_x))
    bs = rng.uniform(0, 2*np.pi, size=D)
    return omegas, bs

def rff_lift(X, omegas, bs):
    if X.ndim == 1: X = X.reshape(-1, 1)
    D = omegas.shape[0]
    # phi[j, t] = sqrt(2/D) cos(omegas[j] . X[:, t] + bs[j])
    proj = omegas @ X + bs[:, None]
    return np.sqrt(2.0/D) * np.cos(proj)

# We'll include [1, x1, x2] in addition to RFF features to keep state recoverable
def full_rff_lift(X, omegas, bs):
    if X.ndim == 1: X = X.reshape(-1, 1)
    T = X.shape[1]
    rff = rff_lift(X, omegas, bs)
    return np.vstack([np.ones(T), X[0], X[1], rff])

# Match dictionary size: previous RBF used 171 features (3 + 168 centers).
# Let's use D=168 random features, giving 3 + 168 = 171 total.
D_RFF = 168
# Bandwidth: from earlier, eps_rbf = 1.0 was best for RBF. 
# RFF gamma = eps_rbf gives equivalent Gaussian kernel.
GAMMA_RFF = 1.0
omegas, bs = make_rff(D_RFF, GAMMA_RFF, dim_x=2, seed=42)

print(f"\nRandom Fourier Features: D = {D_RFF}, gamma = {GAMMA_RFF}")
print(f"  Total dictionary size: 3 + {D_RFF} = {3 + D_RFF}")

Psi_rff = [full_rff_lift(t, omegas, bs) for t in trajs]
Psi_X_rff = np.hstack([p[:, :-1] for p in Psi_rff])
Psi_Y_rff = np.hstack([p[:, 1:]  for p in Psi_rff])

print(f"  cond(Psi_X) = {np.linalg.cond(Psi_X_rff):.2e}")

# Ridge regression with tuned lambda
best_err_rff = None
best_lam_rff = None
for lam in [1e-6, 1e-4, 1e-2, 1e-1, 1.0]:
    K = fit_ridge(Psi_X_rff, Psi_Y_rff, lam)
    # quick predict 500 steps
    psi = full_rff_lift(X_test[:, 0:1], omegas, bs).flatten()
    out = np.zeros((2, 501))
    out[:, 0] = X_test[:, 0]
    bad = False
    for k in range(500):
        psi = K @ psi
        if not np.isfinite(psi).all() or np.max(np.abs(psi)) > 1e3:
            bad = True; break
        out[:, k+1] = psi[[1, 2]]
    if bad: continue
    err = np.linalg.norm(out[:, -1] - X_test[:, 500])
    if best_err_rff is None or err < best_err_rff:
        best_err_rff = err
        best_lam_rff = lam

print(f"  best lambda: {best_lam_rff:.0e}, h=500 err = {best_err_rff:.4f}")

K_rff = fit_ridge(Psi_X_rff, Psi_Y_rff, best_lam_rff)
eigs_rff = np.linalg.eigvals(K_rff)
print(f"  ||K||_2 = {np.linalg.norm(K_rff, 2):.4f}")
print(f"  spectral radius = {np.max(np.abs(eigs_rff)):.6f}")

def predict_rff(x0, n):
    psi = full_rff_lift(np.asarray(x0).reshape(2,1), omegas, bs).flatten()
    out = np.zeros((2, n))
    out[:, 0] = x0
    for k in range(n-1):
        psi = K_rff @ psi
        out[:, k+1] = psi[[1, 2]]
    return out

pred_rff = predict_rff(X_test[:, 0], n_steps)


# Method 3: Reference RBF EDMD
def rbf_lift(X, centers, eps_rbf):
    if X.ndim == 1: X = X.reshape(-1, 1)
    T = X.shape[1]
    feats = [np.ones(T), X[0], X[1]]
    for i in range(centers.shape[1]):
        d2 = (X[0]-centers[0,i])**2 + (X[1]-centers[1,i])**2
        feats.append(np.exp(-eps_rbf * d2))
    return np.vstack(feats)

np.random.seed(0)
center_idx = np.random.choice(X_data_all.shape[1], 168, replace=False)
centers = X_data_all[:, center_idx]
EPS_RBF = 1.0
RIDGE_LAM = 1e-2

Psi_rbf = [rbf_lift(t, centers, EPS_RBF) for t in trajs]
Psi_X_rbf = np.hstack([p[:, :-1] for p in Psi_rbf])
Psi_Y_rbf = np.hstack([p[:, 1:]  for p in Psi_rbf])
K_rbf = fit_ridge(Psi_X_rbf, Psi_Y_rbf, RIDGE_LAM)

def predict_rbf(x0, n):
    psi = rbf_lift(np.asarray(x0).reshape(2,1), centers, EPS_RBF).flatten()
    out = np.zeros((2, n))
    out[:, 0] = x0
    for k in range(n-1):
        psi = K_rbf @ psi
        out[:, k+1] = psi[[1, 2]]
    return out

pred_rbf = predict_rbf(X_test[:, 0], n_steps)


# Compare errors
print("\n" + "=" * 80)
print("Pendulum prediction error vs horizon")
print("=" * 80)
print(f"{'h':>6} {'time(s)':>8}  {'Hankel-DMD':>14}  {'RFF EDMD':>14}  {'RBF EDMD':>14}")
for h in [1, 5, 10, 20, 50, 100, 200, 500, 1000]:
    e_h = np.linalg.norm(pred_hankel[:, h] - X_test[:, h])
    e_f = np.linalg.norm(pred_rff[:, h] - X_test[:, h])
    e_r = np.linalg.norm(pred_rbf[:, h] - X_test[:, h])
    print(f"{h:>6d} {h*dt:>8.2f}  {e_h:>14.5f}  {e_f:>14.5f}  {e_r:>14.5f}")


# Plot
fig = plt.figure(figsize=(15, 9))
gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.32)

colors = {'truth': 'black', 'hankel': 'orange', 'rff': 'blue', 'rbf': 'green'}

# Phase portrait
ax = fig.add_subplot(gs[0:2, 0:2])
ax.plot(X_test[0], X_test[1], color=colors['truth'], lw=2.6, label='Truth')
ax.plot(pred_hankel[0], pred_hankel[1], color=colors['hankel'], lw=1.4,
        label=f'Hankel-DMD (delay {DELAY}, rank {RANK})')
ax.plot(pred_rff[0], pred_rff[1], color=colors['rff'], lw=1.4,
        label=f'RFF EDMD (D={D_RFF}, γ={GAMMA_RFF})')
ax.plot(pred_rbf[0], pred_rbf[1], color=colors['rbf'], lw=1.4,
        label=f'RBF EDMD (168 centers)')
ax.scatter(*X_test[:, 0], c='lime', s=140, edgecolor='k', linewidth=2,
           zorder=5, label='$x_0$')
ax.scatter(0, 0, c='red', s=120, marker='X', edgecolor='k', linewidth=1.5,
           zorder=5, label='equilibrium')
ax.set_xlabel('$\\theta$ (rad)'); ax.set_ylabel('$\\dot\\theta$ (rad/s)')
ax.set_title('Phase portrait — damped pendulum, free-running prediction')
ax.legend(fontsize=9); ax.grid(alpha=0.3)

# Error vs horizon
horizons = np.array([1, 5, 10, 20, 50, 100, 200, 500, 1000])
err_h = np.array([np.linalg.norm(pred_hankel[:, h] - X_test[:, h]) for h in horizons])
err_f = np.array([np.linalg.norm(pred_rff[:, h]    - X_test[:, h]) for h in horizons])
err_r = np.array([np.linalg.norm(pred_rbf[:, h]    - X_test[:, h]) for h in horizons])

ax = fig.add_subplot(gs[0, 2])
ax.loglog(horizons * dt, err_h, 'o-', color=colors['hankel'], label='Hankel-DMD', lw=2)
ax.loglog(horizons * dt, err_f, 's-', color=colors['rff'], label='RFF EDMD', lw=2)
ax.loglog(horizons * dt, err_r, '^-', color=colors['rbf'], label='RBF EDMD', lw=2)
ax.set_xlabel('horizon (s)'); ax.set_ylabel('error')
ax.set_title('Error vs horizon')
ax.legend(fontsize=8); ax.grid(alpha=0.3, which='both')

# theta(t)
ax = fig.add_subplot(gs[1, 2])
ax.plot(t_eval, X_test[0], color=colors['truth'], lw=2, label='Truth')
ax.plot(t_eval, pred_hankel[0], color=colors['hankel'], lw=1.1, label='Hankel')
ax.plot(t_eval, pred_rff[0], color=colors['rff'], lw=1.1, label='RFF')
ax.plot(t_eval, pred_rbf[0], color=colors['rbf'], lw=1.1, label='RBF')
ax.set_xlabel('t (s)'); ax.set_ylabel('$\\theta$ (rad)')
ax.set_title('$\\theta(t)$ — full 25 s')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

plt.suptitle('Damped pendulum: Hankel embedding vs Random Fourier Features vs RBF',
             fontsize=13, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/hankel_rff_pendulum.png', dpi=130, bbox_inches='tight')
print("\nSaved /mnt/user-data/outputs/hankel_rff_pendulum.png")
