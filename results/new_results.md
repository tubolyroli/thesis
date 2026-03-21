# Executive Summary of Final Empirical Findings
**Thesis:** LLM Knowledge Cutoffs and the Diffusion of Python Libraries  
**Date:** Thursday, March 19, 2026

This document summarizes the finalized empirical results, establishing the causal link between LLM knowledge cutoffs and suppressed library adoption.

---

## Part 1: Core Research Findings

### 1. The "Activation" Effect: Timing of Divergence
The diffusion gap established by the September 2021 cutoff was "activated" as a mass-market phenomenon by the release of ChatGPT.
*   **Implementation (GitHub 52w):** Statistically **insignificant** (Conventional p=0.72, Robust p=0.28). There was no inherent implementation bias between cohorts before the model became a mass interface.
*   **Adoption (PyPI 52w):** While interest-level downloads show a detectable gap, the **implementation gap** only fully emerged once LLMs began steering developer tool choice at scale.

### 2. The "Suppression" Fact: Difference-in-Discontinuities
Using a **Diff-in-RDD** design to control for historical seasonality (2018–2020), we isolate a unique downward shift in adoption for the 2021 cohort.

| Success Tier | Horizon (Outcome) | Excess Jump (Causal) | P-value | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Broad (min 10)** | Post-AI Downloads | **-9.14 (log)** | **0.000*** | Significant Suppression |
| **Successful (min 500)** | Post-AI Downloads | **-12.79 (log)** | **0.000*** | **High Suppression** |
| **Superstar (min 1000)** | Post-AI Downloads | **-0.55 (log)** | **0.000*** | Significant Suppression |

**Conclusion:** The September 2021 cutoff **uniquely suppressed** the seasonal adoption boost that libraries released in autumn usually receive. This "cutoff tax" is **40% larger for Successful libraries**, suggesting high-potential tools are most vulnerable to exclusion.

### 3. Mechanism: Implementation vs. Discovery
The diffusion gap is significantly stronger in actual code usage than in general package interest.
*   **PyPI Adoption (Downloads):** 13.1 (log-scale, p=0.0035).
*   **GitHub Usage (Imports):** 26.8 (log-scale, p=0.014).
*   **Interpretation:** The effect is **twice as large** in developer-centric GitHub usage, confirming the mechanism of AI-steered implementation described by Doshi and Hauser.

### 4. Mechanism & Heterogeneity: The AI Exposure Shield
*   **Analysis:** Using a formal **Interaction Model** with week-clustered standard errors to test if AI exposure (measured via commit AI scores) moderates the cutoff effect.
*   **Outcomes:** log(1 + 52-week downloads) and log(1 + 52-week imports).
*   **Finding:** Libraries with **High AI Exposure** show directionally smaller suppression than **Low AI Exposure** libraries.
*   **Statistical Verdict:** The interaction coefficient for 52-week downloads is **0.396** ($p = 0.179$). While suggestive of a "bridging" mechanism where AI exposure can partially offset model exclusion, the difference is **not statistically significant** at conventional levels.
*   **Interpretation:** The "Knowledge Wall" created by the training cutoff appears to be a broad ecosystem effect that is not easily bypassed by high AI usage alone.

---

## Part 2: Technical Rationale & Defensibility

### 1. The "Pre-GPT Success" Filter
To avoid selection bias, we identify "Successful" libraries based on their **26-week cumulative downloads**. For the 2021 cohort, this period ends by March 2022, strictly before the LLM "activation" point, ensuring we are comparing high-quality tools as judged by human developers alone.

### 2. Donut RDD & Bandwidth Stability
*   **Donut (9 weeks):** We exclude August and September 2021 to ensure a clean comparison between "definitely known" (July) and "definitely unknown" (October) libraries.
*   **Bandwidth ($h=13$):** The effect is locally concentrated within a one-quarter window, though robustness tests show stability up to $h=26$.

### 3. Long-Run Persistence
Trajectory analysis through January 2026 shows **no evidence of catch-up**. The adoption gap established in 2023 remains persistent, suggesting that being "born post-cutoff" creates a durable disadvantage in the LLM-mediated software ecosystem.

---

## Part 3: Final Synthesis
The evidence supports a **"Barrier to Entry"** model where LLMs steer aggregate adoption toward established, "known" libraries, uniquely suppressing the growth of new, high-quality competitors released after the model's knowledge boundary.
