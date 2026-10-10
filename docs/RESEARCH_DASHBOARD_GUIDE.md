# ECHO — Research Dashboard Guide

**URL Route:** [http://localhost:3000/research-dashboard](http://localhost:3000/research-dashboard)  
**Component:** `frontend/src/app/research-dashboard/page.tsx`  
**Backend Endpoints:** `/api/v1/research/...`

---

## 1. Purpose & Architecture

The **Research Dashboard** provides an empirical interface for researchers, archivists, and memorial trustees to inspect quantitative benchmarks and live operational telemetry.

Unlike typical analytics pages that show hardcoded mock numbers, the Research Dashboard connects to actual backend evaluation engines, dynamically runs tests across labeled evaluation fixtures, and strictly enforces the Anti-Fabrication Rule (displaying `"Not yet evaluated"` until benchmark execution is triggered).

---

## 2. Interface Anatomy

```
┌────────────────────────────────────────────────────────────────────────┐
│ Topbar: Research & Benchmark Dashboard                                │
├────────────────────────────────────────────────────────────────────────┤
│ Environment Badges: [D:\ECHO Volume] [Zero Cloud Egress] [Mock Active] │
├────────────────────────────────────────────────────────────────────────┤
│ Protocol Status: EVALUATED / NOT EVALUATED    [Run Benchmark] [Refresh]│
├────────────────────────────────────────────────────────────────────────┤
│ KPI Cards:                                                             │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│ │ Faithfulness │ │ Hallucination│ │ Boundary Viol│ │ Precision/Rec│   │
│ │   100.0%     │ │     0.0%     │ │     0.0%     │ │    100.0%    │   │
│ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
├────────────────────────────────────────────────────────────────────────┤
│ Operational Telemetry: Active Sessions, Preserved Records, Guardian    │
├────────────────────────────────────────────────────────────────────────┤
│ Labeled Evaluation Cases Table: Query ID, Category, Verdict, Latency  │
├────────────────────────────────────────────────────────────────────────┤
│ Mathematical Formulations: Formula Definitions & Targets               │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Interactive Workflows

### 3.1 Initial Un-Evaluated State
When the system has not run the evaluation suite against active memory records, the status banner displays:
- Status: `NOT EVALUATED`
- Value Badges: `"Not yet evaluated"`
- Note: *"Benchmark suite has not yet been executed. Showing Not yet evaluated."*

### 3.2 Executing Benchmark Evaluation
1. Click the **"Run Benchmark Evaluation"** button in the header bar.
2. The frontend triggers `POST /api/v1/research/benchmarks/run`.
3. The backend executes all 8 labeled test cases through `MemoryGuardian` and `ClaimExtractor`.
4. Mathematical metrics are computed in real time and cached in `D:\ECHO\research\benchmark_results.json`.
5. The UI updates instantaneously to display calculated percentages, conformance results, and individual query breakdowns.

---

## 4. Visual Badges & Provenance Indicators

To maintain complete transparency for academic peer review, the dashboard explicitly labels all environmental constraints:

- `[D:\ECHO (Strict Local Volume)]`: Confirms all database, vector, media, and benchmark assets reside strictly on the local USB volume.
- `[Zero Cloud Egress Active]`: Confirms zero network packets are transmitted to external cloud inference endpoints.
- `[Offline Mock Providers & Labeled Fixtures]`: Clearly marks that evaluation uses deterministic offline providers and curated human-annotated fixtures.
- `[Live Session Data]`: Highlights operational telemetry collected from live conversational RAG records.

---

## 5. Connected Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/research/status` | GET | Framework title, anti-fabrication status, and target goals |
| `/api/v1/research/benchmarks` | GET | Returns current benchmark status and calculated aggregate metrics |
| `/api/v1/research/benchmarks/run` | POST | Triggers empirical execution of evaluation suite and calculates metrics |
| `/api/v1/research/metrics` | GET | Aggregates live conversational telemetry and memory vault statistics |
| `/api/v1/research/fixtures` | GET | Returns the standardized labeled test cases |
| `/api/v1/research/methodology` | GET | Returns formal research questions and metric formulas |
