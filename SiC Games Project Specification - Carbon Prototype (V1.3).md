# SiC Games: Project Specification - Carbon Prototype (V1.3)

## I. Background & Framework: "The Active Way"
The **SiC Games** framework is a generative social simulation designed to test the **Stasis vs. Expansion** hypothesis. Traditional modeling often focuses on rational agents that optimize for efficiency, leading to a "Perfect Manual" state—a frozen, low-entropy equilibrium. 

This project emulates **Carbon-based (C) population dynamics**, characterized by high-entropy, low-fidelity, and status-driven behaviors. The central framework posits that "flaws"—such as ego, social stratification, and decision noise—are functional mechanisms that drive a population to tunnel through activation barriers and occupy diverse ecological niches.

### The Core Emulation
*   **The Environment:** A rugged fitness landscape of varying resource density and activation energy ($E_a$).
*   **The Agents:** High-energy, short-lived units motivated by metabolic survival and social prestige.
*   **The Goal:** Observe the emergence of **Social Turbulence** as a survival strategy.

---

## II. C-Pop Dynamics: Traits, Factors, & Rationale

| Trait/Factor | Description | Rationale & Literature Basis |
| :--- | :--- | :--- |
| **Ego-Noise** ($\sigma$) | Decision uncertainty scaling with social status. | Prevents local optima traps. *Roll (1986)* identifies hubris as a driver for high-variance risk-taking. |
| **Social Cred** ($\mathcal{C}$) | Non-metabolic currency gained via task success. | "Social Potential Energy" for aggregation. *Dunbar (1992)* suggests social structures have cognitive thresholds. |
| **The Matthew Effect** | Proportional reward distribution. | Drives stratification. *Merton (1968)* observed prestige facilitates further resource acquisition. |
| **Legacy Transfer** | Continuous resource pumping from parent to progeny. | Lowering "Infant Mortality." *Kaplan et al. (2000)* show human survival depends on extended subsidies. |
| **Heuristic Drift** | Lossy transfer of logic manuals. | Prevents static perfection. *Boyd & Richerson (1985)* argue imperfect transmission maintains flexibility. |

---

## III. Mathematical Framework

### 1. Agent State Vector ($S_i$)
$$S_i = \{ \vec{x}, \mathcal{R}, \mathcal{C}, \phi, H, \text{age} \}$$
*   $\vec{x}$: Spatial coordinates.
*   $\mathcal{R}, \mathcal{C}$: Resource and Cred buffers.
*   $\phi$: Genetic drive (Rationalist $[0] \leftrightarrow$ Pretender $[1]$).
*   $H$: Heuristic logic vector (task-solving weights).

### 2. Decision Logic (Softmax-Langevin)
The probability of agent $i$ choosing task $j$:
$$P(\text{task}_j) = \frac{e^{\frac{U_{i,j}}{\sigma(\mathcal{C}_i)}}}{\sum e^{\frac{U_{i,k}}{\sigma(\mathcal{C}_i)}}}$$
*   **Utility ($U$):** $U = w_R \cdot \nabla \mathcal{R} + w_C \cdot \nabla \mathcal{C}$.
*   **Ego-Noise ($\sigma$):** $\sigma(\mathcal{C}_i) = \sigma_{\text{base}} + \kappa \cdot \mathcal{C}_i$.

### 3. Task Resolution (Matthew Rule)
Effective Activation Barrier for a cluster of $N$ agents:
$$E_a^{\text{eff}} = E_a \cdot e^{-\gamma \cdot \sum \mathcal{C}_i}$$
**Reward Partition:**
$$\Delta \mathcal{R}_i = \mathcal{R}_{\text{tot}} \times \frac{\mathcal{C}_i}{\sum \mathcal{C}_j} \quad , \quad \Delta \mathcal{C}_i = \mathcal{C}_{\text{tot}} \times \frac{\mathcal{C}_i}{\sum \mathcal{C}_j}$$

---

## IV. Parameter Calibration & Stability Window

| Parameter | Sim Value | Real-World Basis / Estimation |
| :--- | :--- | :--- |
| **Lifespan** ($\tau$) | 400 - 600 steps | ~40-50 years at 1 step/month (*Leonard & Robertson, 1997*). |
| **Regrowth** ($\rho$) | 0.5% - 2.0% | Net Primary Productivity recovery rates (*Field et al., 1998*). |
| **Cred Decay** ($\delta$) | 0.5% - 2.0% | Decay of collective/personal memory (*Candia et al., 2019*). |
| **Legacy Transfer** | 10% - 30% | Parental net energy subsidy to offspring (*Kaplan et al., 2000*). |
| **Ego Coupling** ($\kappa$) | 0.1 - 0.5 | 20–40% increase in variance in successful leaders (*Roll, 1986*). |
| **Matthew Power** | $\sim 1.5$ | Standard Pareto wealth/prestige distribution (*Gabaix, 2009*). |

---

## V. Environmental Topography: The World Map
The 100 worlds are distributed along a **Connectivity Axis** using Fractal (Perlin) Noise:
*   **Resource** $R_{\text{low}}$: A seasonal traveling wave (Sine oscillation) forcing nomadic movement.
*   **Resource** $R_{\text{high}}$: Stationary "Mines" (High $E_a$) and migratory "Great Beasts" (Random Walk).
*   **Topography:** Ranges from **Pangea** (high connectivity) to **Archipelago** (isolated pockets).

---

## VI. Implementation Hierarchy

### Level 1: Stability Window & Tuning (Current Priority)
**Goal:** Identify the "Goldilocks Zone" where the system avoids both totalitarian "God-Emperors" and communal stagnation.
*   **Focus:** Find the $\kappa, \delta, \gamma$ values that allow high $E_a$ task resolution without triggering total desertification.
*   **Benchmark:** Stable Gini Coefficient between **0.3 and 0.6**.

### Level 2: Entropy & Biology (The "Humanity" Prototype)
**Goal:** Introduce aging, biparental recombination, and heuristic drift.
*   **Benchmark:** Emergence of "Sawtooth" population volatility and allopatric logic speciation.

### Level 3: Continental Scale (The 100-World Run)
**Goal:** Full deployment across the Pangea-Archipelago spectrum.
*   **Benchmark:** Proof that Carbon logic occupies more niche space and tunnels through higher "Innovation Bandgaps" than Silicon controls.

---

## VII. Coding Strategy for Robustness
*   **Data Strategy:** Use **Global State Matrices** (Flat arrays) rather than Object-Oriented agents to maximize CPU cache performance and vectorization.
*   **Spatial Optimization:** Implement **Spatial Hashing** (Grid lookup) to reduce neighbor search from $O(N^2)$ to $O(N)$.
*   **Clamping:** Hard clamps on $\sigma$ to prevent numerical instability/explosive ego jumps.

---

## VIII. Success Benchmarks: The "Humanity" Signature
1.  **Turbulence:** Non-monotonic population fluctuations.
2.  **Stratification:** Clear, functional hierarchies (Gini 0.3–0.6).
3.  **Speciation:** Distinct logical branches ($H$) in isolated regions.
4.  **Expansion:** Occupation of sub-optimal territories driven by status-noise.