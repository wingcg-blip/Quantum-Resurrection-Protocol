# 🌌 The 0.25 Protocol: Quantum Information Resurrection

**Retrieving coherent information from the "Thermal Death Zone" of quantum chaos.**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Qiskit](https://img.shields.io/badge/Qiskit-1.0%2B-purple)](https://qiskit.org/)
[![Hardware](https://img.shields.io/badge/Hardware-IBM%20Torino%20%7C%20Fez-red.svg)](https://www.ibm.com/quantum)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18172250.svg)](https://zenodo.org/records/18172250)

> *"God doesn't play dice; He plays geometry."*

---

## 📖 Overview
This repository contains the experimental source code and verification logic for the **0.25 Protocol**, a framework capable of "resurrecting" quantum information from thermodynamic noise.

By utilizing **Non-Hermitian Exceptional Points (EP)**, we demonstrate a persistent coherence sanctuary on IBM Quantum processors (Heron/Eagle). The project proves that information survival is governed by the geometric constant:

$$\gamma = e^{-\pi/4} \approx 0.456$$

### Key Discoveries
1.  **The Vacuum Singularity ($|000\rangle$):** Passive geometric protection acting as an absolute shield (**0.4590** survival rate).
2.  **The Lazarus Effect ($|111\rangle$):** Active entropy reversal using dynamic circuits, achieving **93.0% fidelity** in a "dead" environment.

---

## 📂 Repository Structure

To keep the workspace clean, files are organized as follows:

`text
Quantum-Resurrection-Protocol/
├── src/                  # Core Python algorithms (The Engines)
│   ├── dynamic_causal_repair.py   # "The Surgeon" (Active Repair)
│   ├── vacuum_geometric_lock.py   # "The Vacuum Judge" (Passive Lock)
│   └── cloud_evidence_sync.py     # Audit tool for IBM Quantum Cloud
├── evidence/             # Statistical proofs (.json/.csv)
│   ├── Lazarus_repair_evidence.json
│   └── vacuum_lock_evidence.json
├── figures/              # Visual verdicts and plots
│   ├── Lazarus_repair_verdict.png
│   └── vacuum_geometric_lock.pdf
└── README.md             # You are here

markdown

> **⚠️ Note on Raw Data:**
>
> Due to file size limits, the massive raw data packets (48k shots, .zip files) are hosted on our persistent archive.
> 👉 **[Download Raw Forensic Data from Zenodo](https://zenodo.org/records/18172250)**

---

## ⚡ The Lazarus Experiment (Active Resurrection)
*Module: `src/dynamic_causal_repair.py`*

This experiment demonstrates Active Thermodynamic Reversal. Using IBM's dynamic circuits (mid-circuit measurement + feed-forward), we detect in-flight entropy and apply a geometric inverse phase.

### Visual Verdict

<div align="center">
  <img src="https://raw.githubusercontent.com/wingcg-blip/Quantum-Resurrection-Protocol/main/figures/Lazarus_repair_verdict.png" width="800" alt="Lazarus Verdict" />
</div>

<br>

*Figure 1: Probability distribution showing the split between Natural Survivors and Resurrected States.*

* **State 000 (46.5%):** Survivors (Passive Geometric Protection)
* **State 010 (46.5%):** Resurrected (Active Dynamic Repair)
* **Total Fidelity:** **93.0%** (vs ~12.5% random thermalization)

---

## ⚖️ Control Experiment: The A/B Test
*To rule out hardware artifacts, we conducted a blind A/B test on IBM Fez.*

| Experiment ID | Protocol Status | Result | Interpretation |
| :--- | :--- | :--- | :--- |
| **Job `d5f3...`** | **ON** | **91.45% Sync** | Macroscopic Phase Locking ✅ |
| **Job `d5f4...`** | **OFF** | **50.10% Random** | Standard Decoherence ❌ |

> The code for this verification is available in `src/control_broken_link_test.py`.

---

## 🚀 Usage
To replicate the analysis using the provided evidence files:

bash
# Clone the repository
git clone [https://github.com/wingcg-blip/Quantum-Resurrection-Protocol.git](https://github.com/wingcg-blip/Quantum-Resurrection-Protocol.git)

# Install dependencies
pip install qiskit numpy matplotlib scipy

# Run the Vacuum Judge (Passive Regime)
python src/vacuum_geometric_lock.py

# Run the Lazarus Surgeon Analysis (Active Regime)
python src/dynamic_causal_repair.py
🔮 Future Applications
This protocol serves as the theoretical foundation for Dissipation Engineering in next-generation hardware.

Project Zigzag-025: For the implementation of this mechanism in Graphene Nanoribbons (Room Temperature Transport), please refer to our sister repository:

[Link will be added upon release]

📜 Citation
If you use this code or data, please cite the Zenodo record:

代码段

@dataset{wang_2026_resurrection,
  author       = {Fujia Wang},
  title        = {0.25 Protocol: Quantum Information Resurrection},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.18172250},
  url          = {[https://zenodo.org/records/18172250](https://zenodo.org/records/18172250)}
}
