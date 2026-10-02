# 🛡️ SENTINEL: Hybrid Anti-Money Laundering (AML) System
> **AI-Driven Financial Crime Intelligence Unit using Hybrid ML, Graph Analytics & Explainable AI**

---

## 📌 Project Overview
**SENTINEL** is an enterprise-grade Hybrid Anti-Money Laundering (AML) detection platform designed to detect complex financial fraud and illicit transactional networks. Traditional AML systems rely on static, rule-based alerts that yield high false-positive rates. SENTINEL bridges this gap by fusing **Tabular Machine Learning**, **Graph Network Topology Analytics**, and **Explainable AI (SHAP)** into a single risk scoring and decision framework.

---

## 🔑 Key Features
- **🌐 Network Topology Feature Mining:** Builds transactional graphs using NetworkX to calculate node-level centrality metrics (*PageRank, Degree Centrality, Betweenness*) to uncover structured money laundering rings and smurfing operations.
- **🤖 Multi-Layer Risk Fusion Engine:** Combines standalone behavioral signals and tabular transaction anomalies using ensemble models (*Random Forest, XGBoost, and Meta-Fusion Risk Classifier*).
- **💡 Explainable AI (XAI):** Integrated SHAP (SHapley Additive exPlanations) engine providing transparent feature importance breakdowns and natural language risk explanations for compliance officers.
- **🖥️ Interactive Command Center:** Built with Streamlit, enabling real-time transaction monitoring, interactive network graph rendering, user profile investigation, and compliance audit trail exports.

---

## 🔐 Demo Access
To access the live interactive dashboard:
- **Agent ID:** `admin`
- **Access Key:** `sentinel2025`

---

## 🏗️ Architecture & Pipeline Workflows

┌────────────────────────┐
                              │   Transaction Data     │
                              └───────────┬────────────┘
                                          │
                 ┌────────────────────────┴────────────────────────┐
                 ▼                                                 ▼
    ┌─────────────────────────┐                       ┌─────────────────────────┐
    │ Tabular Preprocessing   │                       │  NetworkX Graph Engine  │
    │ (Behavior, Amounts, IP) │                       │ (PageRank, Centrality)  │
    └────────────┬────────────┘                       └────────────┬────────────┘
                 │                                                 │
                 └────────────────────────┬────────────────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │   Risk Fusion Engine    │
                             │ (XGBoost / Meta-Fusion) │
                             └────────────┬────────────┘
                                          │
                 ┌────────────────────────┴────────────────────────┘
                 ▼                                                 ▼
    ┌─────────────────────────┐                       ┌─────────────────────────┐
    │  SHAP Explainability    │                       │  Streamlit Command Hub  │
    │  (Feature Attributions) │                       │  (Interactive Network)  │
    └─────────────────────────┘                       └─────────────────────────┘

    ---

## 📊 Performance & Evaluation Results

| Metric | Random Forest Model | XGBoost / Fusion Model | Baseline Rule-Based |
| :--- | :---: | :---: | :---: |
| **ROC-AUC Score** | **0.942** | **0.968** | 0.681 |
| **Precision** | **0.915** | **0.941** | 0.520 |
| **Recall (Sensitivity)** | **0.893** | **0.927** | 0.740 |
| **F1-Score** | **0.904** | **0.934** | 0.611 |

*Note: Graph topology features improved the detection rate of coordinated smurfing patterns by over 28% compared to non-graph tabular models.*

---

## ⚙️ Installation & Running Locally

### 1. Clone the Repository
```bash
git clone [https://github.com/Shashank240924/sentinel-aml-system.git](https://github.com/Shashank240924/sentinel-aml-system.git)
cd sentinel-aml-system
# Create environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# 1. Generate & Preprocess Data
python data_gen.py
python preprocess.py

# 2. Extract Graph Centrality Features
python graph_analysis.py

# 3. Train Models
python train_model.py
python train_fusion.py

python -m streamlit run app.py

3. Scroll down and click the green **Commit changes...** button at the top right of the page.

---

### Sync your local folder afterward
Since you created a new commit on GitHub, pull the new file down to your computer so your local repository stays up-to-date:

```
git pull origin main

<img width="966" height="719" alt="Screenshot 2025-11-25 173839" src="https://github.com/user-attachments/assets/62fae5f3-e8e7-42bc-8035-49bc28530c70" />
<img width="1195" height="733" alt="Screenshot 2025-11-25 223505" src="https://github.com/user-attachments/assets/64d18467-c182-41ac-ba9c-89fc0f2b4325" />
<img width="1872" height="1005" alt="Screenshot 2025-11-25 174313" src="https://github.com/user-attachments/assets/32b9972e-a7db-4b9d-81f3-35501a777f4c" />

