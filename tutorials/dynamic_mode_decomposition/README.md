Dynamic Mode Decomposition with Koopman Operator Theory for System Identification and Control
=============================================================================================

I am a big fan of system identification and had a chance to work on this topic a bit, and this page is a my notes on the topic. You can use this as a material for data driven control and an entry point for one way to do a system identification.

Pre-requsites:
* Familiarity with LTI Systems and Linear Algebra
* Familiarity with Discrete time systems
* Good understanding of PCA and SVD 
* Some basic familiarity of concepts such as Observability, Controllability.


So high level intuition behind this topic is this: for any arbitrary nonlinear system, we can find some mapping g(x) (where g is some function function space, usually infinite dimensional), where state transition becomes linear. Of course, no machine can work with infinite dimensional space, but turns out, for many practical use cases, we can find some limited finite dimensional mapping that captures the dominant dynamics of the system. And, we can learn this mapping ofor any system using just data! 

Why this is important? Imagine that you are implementing a low level controller for a robot. Instead of hand crafting complex dynamics, you can just learn linear model that captures most of the nonlinear behavior directly from data. And use all the tools for linear systems to control it using regular LQR. That is the promise of this journey. There is no free lunch, this pages covers cases where this techniques do not work as well.

---

## Table of Contents

1. [Mathematical Foundation](#1-mathematical-foundation)
2. [Dynamic Mode Decomposition (DMD)](#2-dynamic-mode-decomposition-dmd)
3. [Extended DMD (EDMD)](#3-extended-dmd-edmd)
4. [Dictionary Choices](#4-dictionary-choices)
   - [Polynomial Dictionaries](#41-polynomial-dictionaries)
   - [Radial Basis Functions](#42-radial-basis-functions)
   - [Random Fourier Features](#43-random-fourier-features)
   - [Hankel Embedding](#44-hankel-embedding)
5. [EDMD with Control (EDMDc)](#5-edmd-with-control-edmdc)
6. [LPV-EDMDc and Beyond Control-Affine](#6-lpv-edmdc-and-beyond-control-affine)
7. [State Estimation with Unknown Parameters](#7-state-estimation-with-unknown-parameters)
8. [Deep Koopman](#8-deep-koopman)
9. [Practical Diagnostics and the Error-vs-Horizon Plot](#9-practical-diagnostics)
10. [Key Theorems Summary](#10-key-theorems-summary)
11. [References](#11-references)

---

## 1. Mathematical Foundation

### 1.1 The Setup

Consider a discrete-time dynamical system on $M \subseteq \mathbb{R}^n$:

$$x_{k+1} = F(x_k), \qquad x_k \in M$$

with $F$ generally nonlinear. The continuous-time analog is $\dot{x} = f(x)$, with $F = \Phi^{\Delta t}$ (the time-$\Delta t$ flow map).

### 1.2 The Koopman Operator

Let $\mathcal{F}$ be a space of **observables** $g: M \to \mathbb{C}$ (typically $L^2(M, \mu)$ for some invariant measure $\mu$).

**Definition (Koopman 1931).** The Koopman operator $\mathcal{K}: \mathcal{F} \to \mathcal{F}$ is

$$(\mathcal{K} g)(x) := g(F(x))$$

**Three foundational properties:**

1. **Linearity** (regardless of nonlinearity of $F$):
$$\mathcal{K}(\alpha g + \beta h) = \alpha \mathcal{K} g + \beta \mathcal{K} h$$

2. **Infinite-dimensional**: $\mathcal{F}$ is generally infinite-dimensional.

3. **Spectral decomposition** (where applicable):
$$\mathcal{K} \phi_j = \mu_j \phi_j$$
with Koopman eigenfunctions $\phi_j$ and eigenvalues $\mu_j$. For the full-state observable $g(x) = x$:
$$x_k = \sum_j \varphi_j \mu_j^k b_j$$
where $\varphi_j$ are **Koopman modes** and $b_j = \langle \phi_j, x_0 \rangle$.

### 1.3 The Infinitesimal Generator

For continuous-time systems $\dot{x} = f(x)$, the Koopman generator is

$$\mathcal{L} g = \lim_{t \to 0^+} \frac{\mathcal{K}^t g - g}{t} = \nabla g \cdot f$$

with $\mathcal{K}^t = \exp(t \mathcal{L})$. The generator is the "Lie derivative along $f$" and is the natural object for many proofs.

Let's give some intution what Koopman generator is. So to solve the equation above, you have to find infinite number of functions that construct a "eigenfuctions" (think eigenvectors, but each scalar element is functions), that each solve the equation above. So you can use this equation to "generate" eigenfuctions. The catch is that in practice many problems do not have closed form solutions, aside small subset of cases. Many modern day approaches try to "guess" some well generalizeable "dictionary" of eigenfunctions (more on this a bit later).

### 1.4 The Trade

**Koopman trades a finite-dimensional nonlinear problem for an infinite-dimensional linear one.** All data-driven Koopman methods address the same question: how to find a *finite-dimensional approximation* to $\mathcal{K}$ that's accurate enough to be useful.

---

## 2. Dynamic Mode Decomposition (DMD)
DMD is an appraoch for learning dynamcs of linear systems. We can use theory of Koopman Operators to extend it to nonlinear systems.

### 2.1 The Linear Ansatz

DMD (Schmid 2010, Tu et al. 2014) assumes a linear operator $A \in \mathbb{R}^{n \times n}$ approximately advances snapshots:

$$x_{k+1} \approx A x_k$$

### 2.2 The Algorithm

Given snapshots, form:

$$X = [x_0\ x_1\ \cdots\ x_{m-1}] \in \mathbb{R}^{n \times m}, \qquad Y = [x_1\ x_2\ \cdots\ x_m]$$

**Direct solution:** Least Squares

$$A = \arg\min_A \|Y - AX\|_F^2 = Y X^+$$

where $X^+$ is the Moore–Penrose pseudoinverse. ($\|\|_F^2$ -> Frobenius norm)

### 2.3 Practical Exact DMD (Tu et al. 2014)

For high-dimensional state, never form $A$ explicitly. Instead:

**Step 1: SVD with rank truncation.**

$$X = U \Sigma V^*, \qquad \text{truncate to rank } r$$

**Step 2: Reduced operator.**

$$\tilde{A} = U_r^* Y V_r \Sigma_r^{-1} \in \mathbb{C}^{r \times r}$$

**Step 3: Eigendecomposition.**

$$\tilde{A} W = W \Lambda, \qquad \Lambda = \text{diag}(\mu_1, \ldots, \mu_r)$$

**Step 4: Exact DMD modes** (eigenvectors of $A$ itself):

$$\Phi = Y V_r \Sigma_r^{-1} W$$

**Step 5: Initial amplitudes.**

$$b = \Phi^+ x_0$$

**Step 6: Prediction.**

$$x_k \approx \Phi \Lambda^k b = \sum_{j=1}^r \varphi_j \mu_j^k b_j$$

The continuous-time eigenvalues are $\omega_j = \log(\mu_j)/\Delta t$. The imaginary part gives frequency; the real part gives growth/decay rate.

### 2.4 Implementation Pitfall: Modes vs. Eigenvectors

The "projected modes" $\Phi_{\text{proj}} = U_r W$ live in the column space of $U_r$. The "exact modes" $\Phi_{\text{exact}} = Y V_r \Sigma_r^{-1} W$ are true eigenvectors of $A$. **Use exact modes by default** unless you have a specific reason (e.g., guaranteed orthogonality requirement).

### 2.5 Connection to the Koopman Operator

**DMD = Koopman restricted to linear observables.** When $g(x) = x$ (the identity), the operator $A$ from DMD equals the Koopman operator restricted to the span of coordinate functions. For linear $F(x) = Mx$, DMD recovers $M$ exactly. For nonlinear $F$, DMD gives the **least-squares linear approximation** in coordinate space — which is generally inadequate.

---

## 3. Extended DMD (EDMD)
Vanilla DMD can only capture the dynamics of a Linear Time Invariant Autonomous System. We will start expanding it first to nonlinear systems, then systems with control input and adaptive parameters.

### 3.1 The Lift

EDMD (Williams, Kevrekidis, Rowley 2015) generalizes DMD to operate on a **dictionary** of nonlinear observables:

$$\Psi(x) := [\psi_1(x), \psi_2(x), \ldots, \psi_N(x)]^T$$

Ideal lifted equation is a eigenfunction solutions to the Koopman generator equations for a system f(x). The lifted snapshot matrices are:

$$\Psi_X = [\Psi(x_0)\ \cdots\ \Psi(x_{m-1})] \in \mathbb{R}^{N \times m}$$
$$\Psi_Y = [\Psi(x_1)\ \cdots\ \Psi(x_m)] \in \mathbb{R}^{N \times m}$$

### 3.2 The EDMD Operator

$$K = \Psi_Y \Psi_X^+ \in \mathbb{R}^{N \times N}$$

This solves $\min_K \|\Psi_Y - K \Psi_X\|_F^2$.

### 3.3 Convergence to Koopman

**Theorem (Korda & Mezić 2018).** Let $\mu$ be an ergodic measure for $F$. As $m \to \infty$ (more data) at fixed dictionary size $N$:

$$K_{m} \xrightarrow{a.s.} P_N \mathcal{K} P_N$$

where $P_N$ is the orthogonal projection onto $\text{span}(\Psi)$ in $L^2(\mu)$. As $N \to \infty$ (richer dictionary), $P_N \mathcal{K} P_N \to \mathcal{K}$ strongly on the relevant subspace.

**Practical interpretation:** EDMD recovers the orthogonal projection of $\mathcal{K}$ onto the dictionary's span. The error has two sources: finite data (mitigated by more samples) and finite dictionary (mitigated by richer features).

### 3.4 Prediction in State Space

After identifying $K$, prediction proceeds by iteration:

$$\psi_{k+1} = K \psi_k$$

and the state is recovered from $\psi_k$ either by:
- **Direct readout**: if $x \in \text{span}(\Psi)$, the state components are specific entries of $\psi$.
- **Linear projection**: $x_k = C \psi_k$ for a learned readout matrix $C$.

### 3.5 The Two Error Sources

EDMD's long-horizon prediction error has two structurally distinct origins:

**(1) Invariance leak.** $\text{span}(\Psi)$ is generally not $\mathcal{K}$-invariant: $\mathcal{K} \psi_i$ has components outside $\text{span}(\Psi)$. The error per step is $\|P_N^\perp \mathcal{K} \Psi\|$. Compounding over $k$ steps:

$$\|\psi_k - \Psi(x_k)\| \leq C(k) \cdot \|P_N^\perp \mathcal{K} \Psi\|$$

with $C(k)$ growing with $k$.

**(2) Lift-project inconsistency.** After many iterations, the lifted state $K^k \Psi(x_0)$ no longer corresponds to $\Psi$ of any actual state. Entries that should be consistent (e.g., the entry labeled $x_1^2$ should equal the square of the entry labeled $x_1$) drift apart. The state read off becomes inconsistent with itself.

Both errors compound. The first is fundamental to finite dictionaries; the second can be mitigated with state-inclusive lifts or autoencoder architectures.

---

## 4. Dictionary Choices

The choice of dictionary is the single most important design decision in EDMD. Different dictionaries fail in different ways and excel for different system classes.

### 4.1 Polynomial Dictionaries
Main intuition behind polynomial dictionaries is that any function can be written as a infinite Tailor series sum. For example, Hambel basis can serve as a basis for all polynomial functions with single variables exactly and approximate any continuous function with arbitrary accuracy. Although, polynomials can not serve as exact basis for all functions. So, if you are intersted to have a model that is quite good at some local areas, this is great choice, although it has few downsides.

#### 4.1.1 Monomial Basis

For 2D state, the monomial dictionary of degree $d$:

$$\Psi(x) = [1, x_1, x_2, x_1^2, x_1 x_2, x_2^2, \ldots, x_2^d]$$

with $N = \binom{d+2}{2}$ features in 2D, $\binom{d+n}{d}$ in $n$ dimensions.

**Generally bad numerically** for $d > 5$ due to extreme scale mismatch. $x_1^{10}$ on data with $|x_1| \leq 3$ ranges up to $\sim 10^4$ while $x_1$ ranges to 3. Condition number of $\Psi_X$ explodes.

#### 4.1.2 Rescaled Monomials

The single most important preprocessing step: rescale state to $\sim [-1, 1]$ before lifting.

$$\tilde{x} = x / x_{\max}, \qquad \Psi(\tilde x) = [1, \tilde x_1, \tilde x_2, \tilde x_1^2, \ldots]$$

This alone reduces the condition number from $\sim 10^{11}$ (degree 17) to $\sim 10^{9}$, and reduces $\|K\|_2$ from $\sim 10^6$ to $\sim 30$. **Always rescale state before polynomial lifting.**

#### 4.1.3 Legendre / Chebyshev Polynomials

Orthogonal under uniform / Chebyshev measure on $[-1, 1]$. Better conditioning than monomials but **not adapted to data distribution**. For most Koopman applications where data is concentrated on attractors, Legendre's orthogonality is mismatched to the empirical measure, limiting its benefit.

#### 4.1.4 Data-Orthogonal Polynomials (Cholesky Whitening)

**The right answer for polynomial dictionaries.** Orthogonalize monomials under the *empirical data measure*:

**Construction.** Let $M(x)$ be the monomial vector. Empirical Gram matrix:

$$G = \frac{1}{N_{\text{data}}} \sum_{k} M(x_k) M(x_k)^T = \frac{1}{N_{\text{data}}} M_X M_X^T$$

Cholesky factorize $G = LL^T$ and define the new basis:

$$\boxed{\Psi(x) := L^{-1} M(x)}$$

This basis satisfies:

$$\frac{1}{N_{\text{data}}} \sum_k \Psi(x_k) \Psi(x_k)^T = L^{-1} G L^{-T} = I$$

**Orthonormal under the empirical measure.** The condition number of $\Psi_X$ becomes $\approx 1$ regardless of degree.

**Pseudocode:**

```python
def build_orthogonal_basis(X_data, degree, scale):
    powers = monomial_powers(degree)
    M = eval_monomials(X_data, powers, scale)   # (N_mono, N_data)
    G = (M @ M.T) / M.shape[1]
    G += 1e-14 * trace(G)/N * I    # numerical safety
    L = cholesky(G)
    T = solve(L, I)                # T = L^{-1}
    return powers, T, scale

# Lift any state via:
def eval_lifted(x, powers, T, scale):
    return T @ eval_monomials(x, powers, scale)
```

**State readout:** the state $x_i$ is at monomial index $j_i$ (specific position). To extract $x_i$ from the orthogonal lifted vector $\Psi(x) = T M(x)$:

$$x_i = \mathbf{e}_{j_i}^T M(x) \cdot \text{scale} = (T^{-T} \mathbf{e}_{j_i})^T \Psi(x) \cdot \text{scale}$$

So the readout vector is $w_i = \text{scale} \cdot T^{-T} \mathbf{e}_{j_i}$, and $x_i = w_i^T \Psi(x)$.

### 4.2 Radial Basis Functions
High level intution behind Radial Basis Functions is that you can imagine that if discretized the state space to cells, then you can come up with a state transition matrix from adjacent cells. Then, you can imagine refining resolution of grid size to be infinitely small. Which means, you can capture the state transition matrix for any nonlinear function. However, this is generally expensive and subject to curse of dimensionality. However, you can use finite number of radial basis functions to approximate continuous space with fininte number of discrete values.

Main tradeoff of Radial Basis Functions is that they are not very accurate in local regions, but can capture the global dynamics better with smaller dictionary. 

#### 4.2.1 Gaussian RBF Construction

Choose $n_c$ **centers** $\{c_1, \ldots, c_{n_c}\} \subset \mathbb{R}^n$ and bandwidth $\varepsilon > 0$:

$$\phi_i(x) = \exp(-\varepsilon \|x - c_i\|^2)$$

State-inclusive dictionary:

$$\Psi(x) = [1, x_1, \ldots, x_n, \phi_1(x), \ldots, \phi_{n_c}(x)]^T$$

#### 4.2.2 Geometric Intuition: K as a Transport Graph

Each $\phi_i(x) \in (0, 1]$ measures proximity of state $x$ to center $c_i$. The lifted state $\Psi(x)$ is approximately a "soft indicator" of which phase-space cell the state is in. Then the Koopman matrix $K$ encodes a **directed weighted graph between centers**:

$$K_{ji} \approx \text{rate at which "activation at } c_i\text{" transports to "activation at } c_j\text{"}$$

Equivalently, **column $i$ of $K$ predicts where the flow transports $c_i$ in one step**. This is structurally similar to **Ulam's method** for Perron-Frobenius operator approximation (Ulam 1960; Dellnitz & Junge 1999), where space is partitioned into hard cells $B_i$ and the transition matrix is $P_{ij} = \mu(B_i \cap F^{-1}(B_j))/\mu(B_i)$. RBF-EDMD generalizes Ulam's method to soft, overlapping cells (Klus, Koltai, Schütte 2016).

#### 4.2.3 Conditioning Disaster Without Ridge

Densely-packed Gaussian features are nearly collinear. The Gram matrix $G = \Psi_X \Psi_X^T$ becomes essentially rank-deficient, with condition number $\sim 10^{16}$ for $n_c \sim 100$ in 2D. **The pseudoinverse explodes; the operator $K$ has spectral norm $> 10^{10}$; predictions blow up.**

**Solution: ridge regression.**

$$K = \Psi_Y \Psi_X^T \left( \Psi_X \Psi_X^T + \lambda I \right)^{-1}$$

Typical $\lambda \in [10^{-4}, 10^{-1}]$ depending on $n_c$ and $\varepsilon$. **Ridge is not optional for RBF-EDMD.**

#### 4.2.4 The Three Knobs

**(a) Number of centers $n_c$.** More centers = finer phase-space resolution, but worse conditioning. For low-dim systems in moderate phase space: $n_c \in [50, 200]$.

**(b) Bandwidth $\varepsilon$.** Rule of thumb: $\varepsilon \sim 1/d^2$ where $d$ is typical center spacing. Too small (large bandwidth): features overlap completely, lose discriminative power. Too large (small bandwidth): features don't overlap, can't interpolate between centers.

**(c) Center placement.** See §4.2.5.

#### 4.2.5 Center Placement Strategies

Empirical results on Van der Pol at $n_c = 100$:

| Strategy | $\text{cond}(\Psi_X)$ | h=500 error |
|---|---|---|
| Random sampling from data | $3.4 \times 10^{15}$ | 0.186 |
| K-means++ | $2.5 \times 10^{8}$ | 0.184 |
| Farthest Point Sampling (FPS) | $1.4 \times 10^{5}$ | 0.187 |
| Sobol sequence + project | $1.4 \times 10^{21}$ | 0.192 |
| Dynamics-aware (residual-greedy) | $2.7 \times 10^{13}$ | 0.397 (worse!) |

**Key findings:**

1. **K-means++ is the right default** (Arthur & Vassilvitskii 2007). It adapts center density to data density, gives clean spacing.

2. **FPS** (Eldar et al. 1997, Gonzalez 1985) is best for *short-horizon* prediction because it maximizes coverage. Long-horizon attractor-based prediction prefers density-weighted placement (k-means).

3. **Conditioning improves dramatically with non-random methods** (10+ orders of magnitude), but **prediction error barely changes** because ridge regularization absorbs conditioning differences. The main benefit of smart placement is interpretability (cleaner spectrum) and not needing ridge.

4. **Dynamics-aware greedy placement can hurt** because it concentrates centers in transient/error regions and neglects the attractor itself.

#### 4.2.6 K-means Implementation Note

Use k-means++ initialization (Arthur & Vassilvitskii 2007), not random initialization. With sklearn: `KMeans(init='k-means++', n_init=5)`. K-means with random init can converge to terrible local minima in 30% of trials.

For very large datasets: mini-batch k-means.

For very high dimensions: random projection + k-means (Boutsidis, Zouzias, Drineas 2010) — project data to $O(\log n_c)$ dimensions first.

#### 4.2.7 RBF as Discretized Coherent States

A useful conceptual frame: Gaussian RBFs are discretized **coherent states** from quantum mechanics. Coherent states $|\alpha\rangle$ are localized in phase space at $\alpha$, with overlap $\langle \alpha | \beta \rangle = \exp(-|\alpha - \beta|^2/2)$ — literally a Gaussian RBF kernel. RBF-EDMD is structurally analogous to working in a coherent-state basis for quantum dynamics, with the Koopman operator playing the role of the propagator. See Mauro, Gozzi (Koopman-von Neumann classical mechanics) for the formal connection.

### 4.3 Random Fourier Features (RFF)

#### 4.3.1 Construction

Approximation of shift-invariant kernel $k(x, y) = k(x - y)$ via random sampling of its Fourier transform (Rahimi & Recht 2007).

By **Bochner's theorem**: a continuous shift-invariant positive-definite kernel $k$ has a non-negative Fourier transform $p(\omega)$ that is (up to normalization) a probability density. Then:

$$k(x, y) = \int e^{i \omega^T (x - y)} p(\omega) \, d\omega = \mathbb{E}_{\omega \sim p} [\cos(\omega^T(x-y))]$$

**Monte Carlo approximation.** Sample $\omega_j \sim p(\omega)$ and $b_j \sim U[0, 2\pi]$ for $j = 1, \ldots, D$:

$$\phi_j(x) = \sqrt{\frac{2}{D}} \cos(\omega_j^T x + b_j)$$

Then $\mathbb{E}[\Psi(x)^T \Psi(y)] = k(x, y)$.

For the Gaussian kernel $k(x, y) = \exp(-\gamma \|x-y\|^2)$: sample $\omega_j \sim \mathcal{N}(0, 2\gamma I)$. Selection of p(w) is highly dependent on assumptions on the system, and effiencency of this method is direclty linked to finding good sampling probability distribution funciton.

#### 4.3.2 Geometric Intuition

Each RFF feature is a **plane wave** with random frequency $\omega_j$. Different frequencies activate at different spatial scales:
- Low $\|\omega_j\|$: smooth, slowly-varying features (broad structure)
- High $\|\omega_j\|$: rapidly oscillating features (fine details)

**RFF is the Fourier dual of RBF.** RBF localizes features in position space; RFF localizes them in frequency (momentum) space. In QM language: RBF is the coherent-state basis, RFF is the momentum basis. Both span the same Hilbert space (approximately), connected by Fourier transform.

#### 4.3.3 Sparsity Pattern Inversion

| | RBF | RFF |
|---|---|---|
| Position of "support" | one center per feature | all of space (plane wave) |
| Sparsity in $\Psi(x)$ for fixed $x$ | few nonzero entries | all entries of order $1/\sqrt{D}$ |
| Sparsity in frequency | broad spectrum per feature | one frequency per feature |
| Gram matrix structure | nearly diagonal (localized) | nearly dense (delocalized) |

#### 4.3.4 When RFF Wins

- **High-dimensional state**: RBF needs exponentially many centers; RFF needs a number set by kernel complexity, not state dimension.
- **Kernel methods at scale**: kernel DMD has $O(N^3)$ cost; RFF is $O(D^2 N)$.
- **No center placement to tune**.

#### 4.3.5 When RBF Wins

- **Low dimension with abundant data**: explicit RBF centers can adapt to data structure via k-means.
- **Interpretability**: RBF features have clear geometric meaning; RFF features are abstract plane waves.

### 4.4 Hankel Embedding
This is surprising result from Signal Processing. For any discrete time signal, it can be modeled by its infinite time delayed values. This result is often used to design FIR/IIR filters, but the same result can be also used to find a dictionary for Koopman operator. One big advantages of this technique is that you can always compbine it with other techniques and get better, richer results. So it is easiest way to expand the dictionary. Downside - larger dictionary means more computational resources needed. 

#### 4.4.1 The Construction

Stack $d$ time-delayed copies of state (or scalar observable):

$$\Psi(x_k) = \begin{bmatrix} x_k \\ x_{k-1} \\ x_{k-2} \\ \vdots \\ x_{k-d+1} \end{bmatrix}$$

For a scalar time series $y_1, y_2, \ldots, y_N$, Hankel matrix is defined as:

$$H = \begin{bmatrix} y_1 & y_2 & y_3 & \cdots \\ y_2 & y_3 & y_4 & \cdots \\ \vdots & & & \ddots \end{bmatrix}$$

This is the **Hankel matrix**. Each column is a delay-embedded snapshot. Run DMD on $H$.

#### 4.4.2 Theoretical Foundation: Takens Embedding Theorem

**Theorem (Takens 1981).** Let $F: M \to M$ be a smooth diffeomorphism on a $d$-dimensional manifold $M$, and let $g: M \to \mathbb{R}$ be a generic observable. Then the delay map

$$\Phi_{g, F}(x) := (g(x), g(F(x)), g(F^2(x)), \ldots, g(F^{2d}(x))) \in \mathbb{R}^{2d+1}$$

is generically an embedding of $M$. That is, stacking $2d+1$ delays of *any single generic observable* produces a faithful reconstruction of the attractor.

**Implication for Koopman:** even with only partial observations (one scalar measurement), Hankel-DMD recovers the dynamics on the attractor. This is critical for experimental settings where full state is unavailable.

#### 4.4.3 Willems' Fundamental Lemma
One of the most important findings in the Data-Driven control thoery. 

**Theorem (Willems 1986, Markovsky & Rapisarda 2008).** Consider a controllable LTI system. Let $(u_d, y_d)$ be a single input-output trajectory of length $T$, with $u_d$ persistently exciting of order $L + n$ (where $n$ is the system order). Then **any** length-$L$ trajectory $(u, y)$ of the system satisfies:

$$\begin{bmatrix} \mathcal{H}_L(u_d) \\ \mathcal{H}_L(y_d) \end{bmatrix} g = \begin{bmatrix} u \\ y \end{bmatrix}$$

for some vector $g$. Here $\mathcal{H}_L(\cdot)$ denotes the depth-$L$ Hankel matrix.

**Interpretation:** the column space of the Hankel matrix *is* the trajectory space of the LTI system. This is the foundation of **Data-Enabled Predictive Control (DeePC)** (Coulson, Lygeros, Dörfler 2019), which does MPC directly from Hankel matrices without state-space identification.

**Connection to Hankel-DMD:** Willems works with the trajectory subspace; Hankel-DMD identifies the time-shift operator on the same subspace. **Same mathematical object, different question.**

#### 4.4.4 Connection to Koopman: HAVOK

**Theorem (Brunton, Brunton, Proctor, Kutz 2017 — HAVOK).** For chaotic systems with continuous Koopman spectrum, the singular value decomposition of the Hankel matrix yields a closed approximation:

$$\dot{v} = Av + b f$$

where $v$ contains the dominant Hankel singular vectors and $f$ is an "intermittent forcing" representing the chaotic component that cannot be captured by point spectrum.

This is one of the most successful Koopman methods for chaotic systems (Lorenz, turbulence). Why you should care: Lorenz system has continuous spectra without distinct discrete peaks. Remember from definition that Koopman Operations are inherently spectral thoery and work.

#### 4.4.5 Implementation Subtleties

- **Choice of delay $d$**: needs to span at least one period of the slowest dynamics. Too short: doesn't reconstruct attractor. Too long: $H$ becomes huge and the higher-delay information is redundant.
- **Warm-up cost**: predicting the first $d$ steps requires $d$ past observations. There's no free prediction from a single initial condition.
- **Combinable with other dictionaries**: stack delays *and* lift each snapshot through polynomial/RBF features. This is **delay-EDMD** or "lifted Hankel DMD" — combines manifold reconstruction (Takens) with local geometry (polynomials/RBFs).

---

## 5. EDMD with Control (EDMDc)
Now, let's expand the theory for control inputs.

### 5.1 The Setup

Controlled system:

$$x_{k+1} = F(x_k, u_k), \qquad u_k \in \mathbb{R}^p$$

There is no single Koopman operator — there's a **family** indexed by $u$:

$$(\mathcal{K}_u g)(x) = g(F(x, u))$$

### 5.2 Control-Affine Systems

A system is **control-affine** if it has the form:

$$\dot{x} = f(x) + \sum_{j=1}^p g_j(x) u^{(j)}$$

**Lemma (Generator decomposition).** For a control-affine system, the Koopman generator decomposes as:

$$\mathcal{L}_u g = \mathcal{L}_0 g + \sum_{j=1}^p u^{(j)} \mathcal{L}_j g$$

where $\mathcal{L}_0 g := \nabla g \cdot f$ and $\mathcal{L}_j g := \nabla g \cdot g_j$ are **fixed linear operators independent of $u$**.

**Proof:** Direct chain rule.
$$\mathcal{L}_u g = \frac{d}{dt}\bigg|_{t=0} g(\Phi^t_u(x)) = \nabla g(x) \cdot \dot{x}|_{u} = \nabla g \cdot \left(f + \sum_j g_j u^{(j)}\right) = \mathcal{L}_0 g + \sum_j u^{(j)} \mathcal{L}_j g \quad \square$$

This is the **single most important fact** in Koopman control theory. Control-affine systems have a *finite collection* of $p+1$ Koopman operators, linearly combined by the input.

### 5.3 The EDMDc Ansatz

(Proctor, Brunton, Kutz 2016.) Lift only the state; assume linear dependence on $u$:

$$\boxed{\Psi(x_{k+1}) \approx A \Psi(x_k) + B u_k}$$

Identification: stack snapshots $\Psi_X, \Psi_Y, U$ and solve

$$\begin{bmatrix} A & B \end{bmatrix} = \Psi_Y \begin{bmatrix} \Psi_X \\ U \end{bmatrix}^+$$

(With ridge regularization for stability.)

### 5.4 Why EDMDc Works for Control-Affine Systems (Derivation)

Discrete-time evolution over $\Delta t$ with zero-order-hold input $u_k$:

$$\Psi(x_{k+1}) = \exp\big(\Delta t \cdot (L_0 + \sum_j u_k^{(j)} L_j)\big) \Psi(x_k)$$

where $L_j$ are matrix representations of $\mathcal{L}_j$ on the dictionary span (assuming joint $\mathcal{L}_j$-invariance).

Expanding the matrix exponential:

$$e^{\Delta t (L_0 + \sum u^{(j)} L_j)} = I + \Delta t L_0 + \Delta t \sum_j u^{(j)} L_j + \mathcal{O}(\Delta t^2)$$

Truncating to linear order:

$$\Psi(x_{k+1}) \approx \underbrace{(I + \Delta t L_0)}_{A} \Psi(x_k) + \Delta t \sum_j u^{(j)}_k \cdot \underbrace{L_j \Psi(x_k)}_{\text{depends on }x}$$

**The catch:** the second term has a state-dependent factor $L_j \Psi(x_k)$, but EDMDc fits it with a constant matrix $B$. This is the implicit averaging discussed in §5.5.

### 5.5 The Hidden Assumption: Constant B Means Averaged Control

EDMDc finds the **best constant** $B$ that approximates the state-dependent contribution $L_j \Psi(x)$ via least squares. Equivalently:

$$B^* = \mathbb{E}_{x \sim \mu_{\text{data}}} [L_j \Psi(x)]$$

(averaged over the empirical data distribution).

**When this averaging is exact:**

**(i) $g_j(x)$ is state-independent.** Then $L_j \psi_i = \nabla \psi_i \cdot g_j$ has its $x$-dependence absorbed into $\Psi$ itself if the dictionary contains $\nabla \psi_i$-style features. For constant $g_j$, $B$ is genuinely well-defined as a constant matrix.

**(ii) State-dependence of $L_j \Psi(x)$ has low variance over training data.** If $\|L_j \Psi(x) - \mathbb{E}[L_j \Psi]\|$ is small for $x \in \text{supp}(\mu)$, the averaging incurs small error.

**When it fails:** if $g_j(x)$ varies substantially across the operating range, a single $B$ can't capture the variation. **The model has irreducible state-dependent control error proportional to $\text{Var}_x[L_j \Psi(x)]$.**

### 5.6 Bilinear EDMDc

(Surana 2016, Peitz et al. 2020.) When constant-$B$ fails, use:

$$\boxed{\Psi(x_{k+1}) = A \Psi(x_k) + \sum_{j=1}^p u_k^{(j)} B_j \Psi(x_k)}$$

Each $B_j$ is an $N \times N$ matrix. The model is **linear in $\Psi$ at each fixed $u$, but multiplicative between $u$ and $\Psi$**.

**Identification:** stack augmented features $[\Psi_X; u^{(1)} \Psi_X; u^{(2)} \Psi_X; \ldots]$ and do least squares. Parameter count grows from $N(N+p)$ to $N(N + Np) = N^2(1+p)$ — much larger.

**Empirical evidence on a state-dependent system** ($\dot x = -x + xu$):
- EDMDc h=50 error: 0.183
- Bilinear EDMDc h=50 error: **0.0036** (51× better)

For systems with constant $g$ (like the pendulum), bilinear gives modest improvement (~3×) but with risk of overfitting due to extra parameters.

### 5.7 Convex Optimization Use of EDMDc Models

The structural advantage of EDMDc (over bilinear or deep models) is that the lifted dynamics are *linear time-invariant* in lifted state-space:

$$\psi_{k+1} = A \psi_k + B u_k$$

This enables:
- **Linear Quadratic Regulator (LQR)**: solve discrete algebraic Riccati equation in $N$ dimensions, gives feedback gain $u_k = -K_{\text{LQR}} \psi_k$.
- **Linear MPC**: convex QP at each timestep. Solvable in milliseconds.
- **Robust/H-∞ synthesis**: classical linear control theory applies.

This is what makes EDMDc the dominant practical Koopman approach for control — even when bilinear or deep models are more accurate, they lose this convex structure.

### 5.8 Persistency of Excitation

For EDMDc identification to recover both $A$ and $B$, the input $u$ must be **persistently exciting** of sufficient order. Concretely, the augmented Hankel matrix

$$\begin{bmatrix} \mathcal{H}_L(u) \\ \mathcal{H}_L(\Psi(x)) \end{bmatrix}$$

must have full row rank (Willems' lemma). In practice: random piecewise-constant inputs work well; constant inputs do not; closed-loop data correlates $u$ with $x$ and makes the regression ill-posed.

In simpler terms, you can always imagine an input's such that they will not capture anything useful. For example, if you have u=0, for any control-affine system you will fail to capture B matrix, so such data is not good for training. Similarly, there are family of bad inputs. For example, u=constant or u=sin(wt) or cos(wt) (because you can hit some resonanse frequency and exite system dynamics to some unusual response). 

---

## 6. LPV-EDMDc and Beyond Control-Affine

### 6.1 The Idea

Linear Parameter-Varying (LPV) systems generalize LTI to parameter-dependent dynamics:

$$\dot{x} = A(\rho(t)) x + B(\rho(t)) u$$

LPV control theory (Apkarian, Gahinet, Becker 1995; Wu, Yang, Packard, Becker 1996) provides decades of mature tools for global stability and gain-scheduled control.

**LPV-EDMDc** (Iannelli & Smith 2023, Cibulka & Korda 2021) data-driven analog:

$$\boxed{\Psi(x_{k+1}) = A(\rho_k) \Psi(x_k) + B(\rho_k) u_k}$$

with $\rho_k = \rho(x_k)$ or an external measured parameter.

### 6.2 Parameterizing the Dependence

**Affine-in-$\rho$:**

$$A(\rho) = A_0 + \sum_i \rho^{(i)} A_i, \quad B(\rho) = B_0 + \sum_i \rho^{(i)} B_i$$

**Identification** is one regression with stacked regressor:

$$\Psi_Y = \begin{bmatrix} A_0 & A_1 & \cdots & B_0 & B_1 & \cdots \end{bmatrix} \begin{bmatrix} \Psi_X \\ \rho^{(1)} \Psi_X \\ \vdots \\ U \\ \rho^{(1)} U \\ \vdots \end{bmatrix}$$

For more expressiveness: polynomial-in-$\rho$, RBF-in-$\rho$, or learned $A(\rho) = NN_\theta(\rho)$.

### 6.3 Scheduling Parameter Choice

**(1) Quasi-LPV**: $\rho = h(x)$ for some function of state. E.g., for pendulum: $\rho = \cos\theta$ (captures stiffness variation).

**(2) Exogenous LPV**: $\rho$ is a measured external signal (altitude, wind speed).

**(3) Latent LPV**: $\rho = h_\theta(x)$ is learned. Blurs into deep Koopman.

**Physics-informed choice.** For example, in a system with $1/m$ (inverse proportional to mass, many robotics systems model acceleration as a function of force) dependence in dynamics, $\rho = 1/m$ gives affine-in-$\rho$ structure. $\rho = m$ would give nonlinear-in-$\rho$ structure requiring more complex parameterization.

### 6.4 Stability Constraints

**Unconstrained LPV-EDMDc fits do not guarantee stable $A(\rho)$ across the operating range.** Without explicit constraints, the identified $A(\rho)$ can have spectral radius > 1 for some $\rho$, causing predictions to blow up.

**Stability via LMI synthesis** (Apkarian & Gahinet 1995): require a common Lyapunov function $P > 0$ such that

$$A(\rho)^T P A(\rho) - P \prec 0 \quad \forall \rho \in \text{operating range}$$

For polytopic $\rho$, this is a finite set of LMIs (one per vertex of the polytope). Solvable with CVXPY/SDP solvers.

**Practical observation:** uncoonstrained LPV-EDMDc gives dramatically better *local* accuracy (1-step prediction can improve by 7 orders of magnitude over EDMDc) but the operator can be unstable. For closed-loop control where MPC resets the trajectory each step, this often doesn't matter. For open-loop simulation, you need stability constraints.

### 6.5 Non-Control-Affine Systems

When the system is not control-affine — e.g., $\dot x = f(x, u)$ with $u$ entering through $u^2$, $\sin u$, saturation, etc. — the clean generator decomposition fails. Four strategies:

**(a) Polynomial expansion in $u$.** If $F(x, u)$ is smooth in $u$, Taylor expand:

$$F(x, u) = F(x, 0) + u \partial_u F(x, 0) + \frac{u^2}{2} \partial_u^2 F(x, 0) + \cdots$$

Each term is now linear in some monomial $u^\alpha$, recovering a multi-term version of bilinear EDMDc:

$$\Psi(x_{k+1}) = A \Psi(x_k) + \sum_\alpha u^\alpha B_\alpha \Psi(x_k)$$

**(b) Lift the input.** Define $\Psi_u(u)$ and identify:

$$\Psi(x_{k+1}) = A \Psi(x_k) + B \Psi_u(u_k)$$

This handles arbitrary smooth $u$-dependence but breaks MPC convexity (the QP becomes nonconvex in $u$).

**(c) Switched / Piecewise Koopman.** For non-smooth or discrete-mode inputs, fit separate Koopman models per operating mode and switch:

$$\Psi(x_{k+1}) = A_i \Psi(x_k) + b_i, \quad \text{mode } i$$

Composes naturally with hybrid control theory.

**(d) Deep Koopman with input conditioning** (Han et al. 2020). The neural network ingests $u$ as part of its input:

$$\psi_{k+1} = N_\theta(\psi_k, u_k)$$

Most flexible, hardest to use for control design — falls back to nonlinear MPC.

### 6.6 Summary Table

| Method | Operator form | Linear in | Control design |
|---|---|---|---|
| EDMDc | $A\psi + Bu$ | $(\psi, u)$ | Linear MPC, LQR |
| Bilinear EDMDc | $A\psi + \sum_j u_j B_j \psi$ | $\psi$ at fixed $u$ | Bilinear MPC |
| LPV-EDMDc | $A(\rho)\psi + B(\rho) u$ | $(\psi, u)$ at fixed $\rho$ | LPV/gain-scheduled MPC |
| Input-lifted | $A\psi + B\Psi_u(u)$ | $\Psi$ | Nonconvex MPC |
| Switched | $A_i \psi$ per mode | $\psi$ in each mode | Hybrid MPC |
| Deep Koopman | $N_\theta(\psi, u)$ | nothing | Nonlinear MPC |

---

## 7. State Estimation with Unknown Parameters

### 7.1 The Problem

A real-world frequently occurring scenario: dynamics depend on a parameter $\rho$ (mass, friction, payload) that:
- Is **constant per trajectory**
- **Varies across trajectories** (different operating conditions)
- Is **not directly observed** at test time

Training data: many trajectories with different known $\rho$. Test time: estimate $\rho$ from observed state evolution.

### 7.2 Exmaple Solution

**Step 1: Train LPV-EDMDc with $\theta$ as scheduling parameter.**

If physics suggests dependence on $1/m$ (e.g., $\dot v = u/m$): use $\rho = 1/m$. Affine model:

$$\Psi(x_{k+1}) = (A_0 + \rho A_1) \Psi(x_k) + (B_0 + \rho B_1) u_k$$

**Step 2: Joint state-parameter estimation at runtime via EKF or any other state estimator.**

Augmented state: $\xi = (x, \rho)$. Parameter evolves as random walk: $\rho_{k+1} = \rho_k + w_\rho$ with tiny $\text{Var}(w_\rho)$.

EKF prediction:

$$\hat\Psi_{k+1|k} = (A_0 + \hat\rho_k A_1) \hat\Psi_k + (B_0 + \hat\rho_k B_1) u_k$$
$$\hat\rho_{k+1|k} = \hat\rho_k$$

EKF Jacobian (key step): derivative w.r.t. $\rho$ is closed-form:

$$\frac{\partial \hat\Psi_{k+1}}{\partial \rho} = A_1 \hat\Psi_k + B_1 u_k$$

EKF update: observe state directly, $y_k = x_k$, with measurement noise $R$. Standard innovation-correction.

### 7.3 Identifiability Conditions

For $\rho$ to be observable from $(x_k, u_k)$ trajectories, two conditions:

**(a) Persistency of excitation.** The input $u$ must vary enough that the response distinguishes different $\rho$. Constant cruise gives constant response regardless of mass.

**(b) Parameter sensitivity.** The dynamics must change visibly with $\rho$ in the operating regime. Two parameters that always appear together (e.g., $\rho_1 \rho_2$ in dynamics) cannot be separately identified.

---

## 8. Deep Koopman

### 8.1 Motivation

Hand-designed dictionaries (polynomial, RBF, Hankel) have **fundamental capacity limits** set by their structural form. For high-dimensional state or unknown nonlinearities, learn the dictionary end-to-end.

### 8.2 The Koopman Autoencoder Architecture

(Lusch, Kutz, Brunton 2018; Takeishi, Kawahara, Yairi 2017; Otto, Rowley 2019)

$$x \xrightarrow{\Psi_\theta} \psi \xrightarrow{K_\theta} \psi' \xrightarrow{\Psi_\theta^{-1}} x'$$

- **Encoder** $\Psi_\theta: \mathbb{R}^n \to \mathbb{R}^N$: neural network mapping state to lifted features.
- **Koopman operator** $K_\theta \in \mathbb{R}^{N \times N}$: also learned (or solved in closed form, see §8.5).
- **Decoder** $\Psi_\theta^{-1}: \mathbb{R}^N \to \mathbb{R}^n$: neural network recovering state. Or simply a projection to specific entries (state-inclusive design).

### 8.3 Loss Function

$$\mathcal{L} = \lambda_1 \mathcal{L}_{\text{recon}} + \lambda_2 \mathcal{L}_{\text{linear}} + \lambda_3 \mathcal{L}_{\text{pred}} + \lambda_4 \mathcal{L}_{\text{stable}}$$

**(1) Reconstruction:** $\mathcal{L}_{\text{recon}} = \mathbb{E}\|\Psi_\theta^{-1}(\Psi_\theta(x)) - x\|^2$.

**(2) Linear dynamics:** $\mathcal{L}_{\text{linear}} = \mathbb{E}\|K_\theta \Psi_\theta(x_k) - \Psi_\theta(x_{k+1})\|^2$.

**(3) Multi-step prediction:** $\mathcal{L}_{\text{pred}} = \mathbb{E}\sum_{h=1}^H \|\Psi_\theta^{-1}(K_\theta^h \Psi_\theta(x_k)) - x_{k+h}\|^2$.

**(4) Stability penalty (essential):** $\mathcal{L}_{\text{stable}} = \text{ReLU}(\|K_\theta\|_2 - 1)^2$ or eigenvalue-based. This is to avoid parameters for K that can blow up, and make learn simpler more stable dictionary.

### 8.4 The State-Inclusive Encoder Trick

Constrain the architecture so the first $n$ entries of $\Psi_\theta(x)$ equal $x$ itself:

$$\Psi_\theta(x) = [\,x;\, f_\theta(x)\,]$$

This:
- Guarantees encoder is injective
- Makes decoder trivial (project to first $n$ entries)
- Eliminates reconstruction loss (automatically zero)
- Matches the structure of classical EDMD

### 8.5 The Hidden Optimization Question: Why Learn $K$ by Gradient Descent?

**Observation.** Given a fixed encoder $\Psi_\theta$, the optimal $K$ has a *closed-form* solution:

$$K^* = \Psi_\theta(Y) \Psi_\theta(X)^+$$

This is just EDMD on the features the encoder produces. Solving for $K$ by gradient descent throws this structure away.

**Why papers do gradient descent anyway:**

1. **Joint optimization simplicity** — bilevel optimization (closed-form K + SGD encoder) is harder to implement.
2. **Mini-batch noise** — closed-form $K$ on a mini-batch overfits to that batch.
3. **Easy stability regularization** — adding $\lambda \|K\|_2$ penalty is trivial for a parameter.

**DLDMD approach** (Yeung et al. 2017; closed-form-K-in-loop): solve for $K$ in closed form at each step, backprop through the pinv to update encoder. This is more principled but suffers from mini-batch noise in the closed-form solution.

**Best practice:** use slow learning rate on $K$ relative to encoder, *or* periodically solve full-batch closed-form $K$ between encoder SGD passes.

### 8.6 Critical Failure Modes

**(1) Operator instability.** Without stability regularization, training drives $\|K\|_2$ above 1. Loss looks fine over training horizon $H$ but predictions explode at $h \gg H$. **Always check spectral radius during training.**

**(2) Multiple local minima.** Loss landscape is rough. Multiple random seeds and patient training are essential.

**(3) Train/test horizon mismatch.** Training with $H=20$, testing with $h=1000$. Add a long-horizon prediction term to the loss every $K$ epochs.

**(4) Encoder collapse.** Without regularization, $\Psi_\theta$ can collapse to trivial mappings. State-inclusive design prevents this.

### 8.7 Architectural Variants

**Eigenvalue parameterization** (Lusch–Kutz–Brunton 2018): parameterize $K$ as block-diagonal $2\times 2$ rotation-scaling blocks, with learnable $(\omega_j, \mu_j)$ per block. Bakes Koopman spectral structure into the architecture.

**Continuous-time generator learning** (Otto & Rowley 2019): learn $\mathcal{L}_\theta$ directly, use $K = \exp(\mathcal{L}_\theta \Delta t)$. Handles irregular time steps.

**Equivariant Koopman**: encode symmetries (rotation, translation, permutation) into $\Psi_\theta$.

**Stochastic Koopman**: learn mean + covariance for noisy systems.

### 8.8 When Deep Koopman Actually Helps

For low-dim systems with abundant data, well-tuned classical methods (k-means RBF, data-orthogonal polynomial) are competitive and much simpler. **Deep Koopman wins when:**

- **High-dim state** ($d > 50$): can't hand-design a dictionary
- **Image/video observation**: encoder must extract relevant features
- **Partial / noisy observation**: network can learn to denoise
- **Parametric families**: train once, generalize across system parameters
- **Multi-physics systems**: heterogeneous state representations

For our Van der Pol and pendulum demos, deep Koopman did *not* outperform tuned RBF or orthogonal polynomial methods. The honest answer: deep methods are tools for problems beyond hand-engineering's reach, not free improvements on already-tractable problems.

---

## 9. Practical Diagnostics

### 9.1 The Error-vs-Horizon Plot

This is the single most informative diagnostic for any Koopman method. Plot one-step, short-horizon, medium-horizon, and long-horizon prediction errors on log-log scale.

**Slopes reveal failure modes:**

- **Slope = 1**: linear growth, uniform per-step error accumulation. Healthy.
- **Slope > 1**: super-linear, compounding. Operator $\|K\|_2 > 1$ in dynamic directions. Lift-project inconsistency.
- **Slope ≈ 0 (plateau)**: error saturated, predictions decorrelated from truth.

**Y-intercept reveals operator quality:**

- $10^{-9}$ – $10^{-6}$: near-perfect short-term operator (polynomial on smooth system).
- $10^{-4}$ – $10^{-2}$: typical good fit (RBF, well-tuned EDMD).
- $> 10^{-1}$: poor operator approximation.

**Plateau height reveals long-horizon failure type:**

- Plateau at attractor amplitude: model fully decorrelated.
- Plateau well below attractor amplitude: model tracks geometry, drifts in phase.

### 9.2 Spectral Diagnostics

For autonomous systems, plot $\mu_j$ in the complex plane along with the unit circle:

- $|\mu| < 1$: damping mode, decay rate $-\log|\mu|/\Delta t$.
- $|\mu| = 1$: conservative mode (limit cycles, oscillations).
- $|\mu| > 1$: unstable, *probably* a numerical artifact unless system is genuinely unstable.

For a limit cycle, expect: eigenvalue at exactly $\mu = 1$ (invariant measure) plus pairs near $|\mu| = 1$ at the fundamental frequency and harmonics.

### 9.3 Condition Numbers and Operator Norms

Always report:
- $\text{cond}(\Psi_X)$: regression conditioning
- $\|K\|_2$: spectral norm, predicts iteration stability
- Spectral radius $\max_j |\mu_j|$: long-horizon growth rate
- Training one-step RMSE: operator quality on training data

### 9.4 The Null Test

When proposing any "improvement" trick (rescaling, orthogonalization, ridge tuning), verify it actually helps in the regime where it should, and verify it *does not* help in regimes where theory says it shouldn't. The latter is the harder test and is what distinguishes understood methods from cargo-culted ones.

Example: whitening helps polynomial EDMD by 10× because polynomial features have variable scale. Whitening does *exactly nothing* for vanilla DMD because DMD on raw state is invariant under similarity transforms — and verifying this numerically (predictions agree to $10^{-11}$ across 1000+ steps) is what gives you confidence that the EDMD improvement is genuinely about the dictionary, not a numerical accident.

---

## 10. Key Theorems Summary

**Koopman's Theorem (1931).** The composition operator $\mathcal{K}_F: g \mapsto g \circ F$ on $L^2(M, \mu)$ for a measure-preserving $F$ is a unitary operator with spectrum on the unit circle. The dynamics of $F$ can be reconstructed from the spectral decomposition of $\mathcal{K}$ on observables.

**Mezić's Spectral Theorem (2005).** For ergodic measure-preserving systems, the Koopman operator decomposes into point spectrum (quasi-periodic dynamics) plus continuous spectrum (mixing dynamics). Finite Koopman-invariant subspaces exist for the point-spectrum part only.

**Takens Embedding Theorem (1981).** For a smooth diffeomorphism $F$ on a $d$-dimensional manifold $M$ and generic observable $g$, the delay map $\Phi_{g,F}(x) = (g(x), g(F(x)), \ldots, g(F^{2d}(x)))$ is generically an embedding of $M$.

**Willems' Fundamental Lemma (1986, Markovsky–Rapisarda 2008).** For a controllable LTI system with persistently exciting input, the column space of the Hankel matrix of any single input-output trajectory equals the set of all length-$L$ trajectories of the system.

**Korda–Mezić Convergence Theorem (2018).** EDMD with dictionary of size $N$ trained on $m$ data points converges in two stages: (1) as $m \to \infty$ at fixed $N$, the EDMD operator converges almost surely to the orthogonal projection of $\mathcal{K}$ onto $\text{span}(\Psi)$; (2) as $N \to \infty$ with dense dictionary, this projection converges strongly to $\mathcal{K}$.

**Generator Decomposition for Control-Affine Systems (folklore, formalized in Klus et al. 2020).** For $\dot x = f(x) + \sum_j g_j(x) u^{(j)}$, the Koopman generator satisfies $\mathcal{L}_u = \mathcal{L}_0 + \sum_j u^{(j)} \mathcal{L}_j$ with $\mathcal{L}_j$ independent of $u$.

**Bochner's Theorem.** A continuous function $k(x, y) = k(x-y)$ is a positive-definite kernel if and only if its Fourier transform is a non-negative measure. Basis of Random Fourier Features.

**Eckart-Young-Mirsky Theorem.** The best rank-$r$ approximation to a matrix $X$ in Frobenius norm is given by the truncated SVD. Foundation of practical DMD via SVD truncation.

---

## 11. References

### Foundational Koopman Theory

- **Koopman, B. O.** (1931). "Hamiltonian systems and transformation in Hilbert space." *Proceedings of the National Academy of Sciences*, 17(5), 315-318.
- **Mezić, I.** (2005). "Spectral properties of dynamical systems, model reduction and decompositions." *Nonlinear Dynamics*, 41(1-3), 309-325.
- **Mezić, I.** (2020). "Spectrum of the Koopman operator, spectral expansions in functional spaces, and state-space geometry." *Journal of Nonlinear Science*, 30, 2091-2145.
- **Budišić, M., Mohr, R., & Mezić, I.** (2012). "Applied Koopmanism." *Chaos*, 22(4), 047510.

### DMD

- **Schmid, P. J.** (2010). "Dynamic mode decomposition of numerical and experimental data." *Journal of Fluid Mechanics*, 656, 5-28.
- **Tu, J. H., Rowley, C. W., Luchtenburg, D. M., Brunton, S. L., & Kutz, J. N.** (2014). "On dynamic mode decomposition: Theory and applications." *Journal of Computational Dynamics*, 1(2), 391-421.
- **Kutz, J. N., Brunton, S. L., Brunton, B. W., & Proctor, J. L.** (2016). *Dynamic Mode Decomposition: Data-Driven Modeling of Complex Systems*. SIAM.

### EDMD

- **Williams, M. O., Kevrekidis, I. G., & Rowley, C. W.** (2015). "A data-driven approximation of the Koopman operator: Extending dynamic mode decomposition." *Journal of Nonlinear Science*, 25(6), 1307-1346.
- **Williams, M. O., Rowley, C. W., & Kevrekidis, I. G.** (2015). "A kernel-based method for data-driven Koopman spectral analysis." *Journal of Computational Dynamics*, 2(2), 247-265.
- **Korda, M., & Mezić, I.** (2018). "On convergence of extended dynamic mode decomposition to the Koopman operator." *Journal of Nonlinear Science*, 28(2), 687-710.
- **Klus, S., Koltai, P., & Schütte, C.** (2016). "On the numerical approximation of the Perron-Frobenius and Koopman operator." *Journal of Computational Dynamics*, 3(1), 51-79.

### Hankel / Takens / DeePC

- **Takens, F.** (1981). "Detecting strange attractors in turbulence." In *Dynamical Systems and Turbulence*, Lecture Notes in Mathematics 898, Springer, 366-381.
- **Willems, J. C., Rapisarda, P., Markovsky, I., & De Moor, B. L. M.** (2005). "A note on persistency of excitation." *Systems & Control Letters*, 54(4), 325-329.
- **Markovsky, I., & Rapisarda, P.** (2008). "Data-driven simulation and control." *International Journal of Control*, 81(12), 1946-1959.
- **Brunton, S. L., Brunton, B. W., Proctor, J. L., Kaiser, E., & Kutz, J. N.** (2017). "Chaos as an intermittently forced linear system." *Nature Communications*, 8, 19.
- **Arbabi, H., & Mezić, I.** (2017). "Ergodic theory, dynamic mode decomposition, and computation of spectral properties of the Koopman operator." *SIAM Journal on Applied Dynamical Systems*, 16(4), 2096-2126.
- **Coulson, J., Lygeros, J., & Dörfler, F.** (2019). "Data-enabled predictive control: In the shallows of the DeePC." *European Control Conference (ECC)*, 307-312.

### Control / EDMDc / LPV-EDMDc

- **Proctor, J. L., Brunton, S. L., & Kutz, J. N.** (2016). "Dynamic mode decomposition with control." *SIAM Journal on Applied Dynamical Systems*, 15(1), 142-161.
- **Proctor, J. L., Brunton, S. L., & Kutz, J. N.** (2018). "Generalizing Koopman theory to allow for inputs and control." *SIAM Journal on Applied Dynamical Systems*, 17(1), 909-930.
- **Korda, M., & Mezić, I.** (2018). "Linear predictors for nonlinear dynamical systems: Koopman operator meets model predictive control." *Automatica*, 93, 149-160.
- **Surana, A.** (2016). "Koopman operator based observer synthesis for control-affine nonlinear systems." *55th IEEE Conference on Decision and Control*, 6492-6499.
- **Peitz, S., Otto, S. E., & Rowley, C. W.** (2020). "Data-driven model predictive control using interpolated Koopman generators." *SIAM Journal on Applied Dynamical Systems*, 19(3), 2162-2193.
- **Iannelli, A., Smith, R. S.** (2023). "A linear parameter-varying perspective on the Koopman operator." Submitted, preprint at arXiv.
- **Cibulka, V., Korda, M.** (2021). "Quadratic optimization in Koopman operator framework for fault detection." *IFAC-PapersOnLine*, 54(7), 412-417.
- **Klus, S., Nüske, F., Peitz, S., Niemann, J.-H., Clementi, C., & Schütte, C.** (2020). "Data-driven approximation of the Koopman generator: Model reduction, system identification, and control." *Physica D*, 406, 132416.

### Kernel Methods / RFF / Sampling

- **Rahimi, A., & Recht, B.** (2007). "Random features for large-scale kernel machines." *Advances in Neural Information Processing Systems (NeurIPS)*, 20.
- **Arthur, D., & Vassilvitskii, S.** (2007). "k-means++: The advantages of careful seeding." *Proceedings of SODA*, 1027-1035.
- **Gonzalez, T. F.** (1985). "Clustering to minimize the maximum intercluster distance." *Theoretical Computer Science*, 38, 293-306.
- **Mahoney, M. W.** (2011). "Randomized algorithms for matrices and data." *Foundations and Trends in Machine Learning*, 3(2), 123-224.

### Deep Koopman

- **Takeishi, N., Kawahara, Y., & Yairi, T.** (2017). "Learning Koopman invariant subspaces for dynamic mode decomposition." *Advances in Neural Information Processing Systems (NeurIPS)*, 30.
- **Lusch, B., Kutz, J. N., & Brunton, S. L.** (2018). "Deep learning for universal linear embeddings of nonlinear dynamics." *Nature Communications*, 9(1), 4950.
- **Yeung, E., Kundu, S., & Hodas, N.** (2017). "Learning deep neural network representations for Koopman operators of nonlinear dynamical systems." Preprint arXiv:1708.06850.
- **Otto, S. E., & Rowley, C. W.** (2019). "Linearly recurrent autoencoder networks for learning dynamics." *SIAM Journal on Applied Dynamical Systems*, 18(1), 558-593.
- **Mardt, A., Pasquali, L., Wu, H., & Noé, F.** (2018). "VAMPnets for deep learning of molecular kinetics." *Nature Communications*, 9(1), 5.
- **Han, Y., Hao, W., & Vaidya, U.** (2020). "Deep learning of Koopman representation for control." *59th IEEE Conference on Decision and Control*, 1890-1895.

### Sparse / SINDy

- **Brunton, S. L., Proctor, J. L., & Kutz, J. N.** (2016). "Discovering governing equations from data by sparse identification of nonlinear dynamical systems." *Proceedings of the National Academy of Sciences*, 113(15), 3932-3937.
- **Kaiser, E., Kutz, J. N., & Brunton, S. L.** (2021). "Data-driven discovery of Koopman eigenfunctions for control." *Machine Learning: Science and Technology*, 2(3), 035023.
- **Jovanović, M. R., Schmid, P. J., & Nichols, J. W.** (2014). "Sparsity-promoting dynamic mode decomposition." *Physics of Fluids*, 26(2), 024103.
- **Pan, S., Arnold-Medabalimi, N., & Duraisamy, K.** (2021). "Sparsity-promoting algorithms for the discovery of informative Koopman-invariant subspaces." *Journal of Fluid Mechanics*, 917, A18.

### LPV Control Theory (foundational)

- **Apkarian, P., & Gahinet, P.** (1995). "A convex characterization of gain-scheduled H∞ controllers." *IEEE Transactions on Automatic Control*, 40(5), 853-864.
- **Becker, G., & Packard, A.** (1994). "Robust performance of linear parametrically varying systems using parametrically-dependent linear feedback." *Systems & Control Letters*, 23(3), 205-215.
- **Wu, F., Yang, X. H., Packard, A., & Becker, G.** (1996). "Induced L2-norm control for LPV systems with bounded parameter variation rates." *International Journal of Robust and Nonlinear Control*, 6(9-10), 983-998.

### Surveys

- **Brunton, S. L., Budišić, M., Kaiser, E., & Kutz, J. N.** (2022). "Modern Koopman theory for dynamical systems." *SIAM Review*, 64(2), 229-340.
- **Otto, S. E., & Rowley, C. W.** (2021). "Koopman operators for estimation and control of dynamical systems." *Annual Review of Control, Robotics, and Autonomous Systems*, 4, 59-87.

### Quantum-Classical Connection

- **Mauro, D.** (2003). "Topics in Koopman-von Neumann theory." PhD thesis, University of Trieste. arXiv:quant-ph/0301172.
- **Gozzi, E., & Mauro, D.** (2002). "A new look at the path integral for relativistic quantum field theories." Annals of Physics, 296, 152-186.

---

## Implementation Cheat Sheet

For practitioners, a single page of the most important practical advice from this document:

**Always:**
- Rescale state to $[-1, 1]$ before polynomial lifting
- Use ridge regularization with RBF dictionaries ($\lambda \in [10^{-4}, 10^{-1}]$)
- Use k-means++ instead of random sampling for RBF centers
- Check spectral radius of identified $K$ — if $> 1$, predictions will eventually diverge
- Plot error vs horizon on log-log scale as the primary diagnostic
- Verify any claimed improvement with a null test in a regime where theory says it shouldn't help

**Often:**
- Data-orthogonal polynomials (Cholesky whitening) for $d > 5$ polynomial degree
- Hankel embedding when full state is not observed or system is chaotic
- LPV-EDMDc when system has a known scheduling parameter (mass, temperature, etc.)
- EDMDc + linear MPC as the default for control of control-affine systems

**Sometimes:**
- RFF instead of explicit RBFs for high-dim state
- Bilinear EDMDc when control vector field is genuinely state-dependent
- Deep Koopman for problems where hand-engineering fails (high-dim, partial obs)

**Rarely:**
- Dynamics-aware center placement (greedy methods can hurt)
- Random sampling for any nontrivial number of centers
- Legendre polynomials (data-orthogonal is strictly better)

