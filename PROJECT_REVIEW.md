# OFFICE-COPILOT Project Review (Current State)

## Product Purpose

OFFICE-COPILOT is a tenant-aware operations intelligence platform for office teams.  
Its primary value is:

1. Analyze real business datasets uploaded by users (`.csv`, `.xlsx`, `.xls`).
2. Produce analyst-style outputs (cleaned data, profiling, pivots, charts, dashboard workbook).
3. Convert uploaded documents (`.txt`, `.md`, `.docx`, `.pdf`) into PowerPoint report decks.
4. Present operational metrics and pipeline health on a web dashboard.

This is not a task-priority analytics tool. Tasks remain a workflow module, while data analysis lives in Reporting.

---

## Implemented Capability Snapshot

## 1) Multi-Tenant Foundation

- Tenant model and tenant resolution middleware are active.
- Tenant is resolved by:
  - `X-Tenant` header
  - host domain
  - authenticated user fallback
- Access checks enforce tenant boundaries for dashboard/reporting/task/presentation flows.

## 2) Reporting Data Lab (Core Excel Intelligence)

Implemented in `apps/reporting`:

- Data upload + analysis workflow (`DataAnalysisRun`)
- Accepted dataset formats: `.csv`, `.xlsx`, `.xls`
- Processing pipeline:
  - schema normalization
  - dtype inference
  - missing-value handling
  - duplicate removal
  - outlier scanning (IQR)
  - pivot generation
  - category frequency profiling
  - numeric stats + correlations
- Workbook generation with sheets such as:
  - `Dashboard`
  - `Column_Profile`
  - `Missing_Before_Clean`
  - `Cleaned_Data` (auto-split into multiple sheets for large datasets)
  - `Pivot_1`, `Pivot_2`
  - `Numeric_Stats`, `Correlation`
  - `Top_Categories`, `Top_Category_Chart`
  - `Analyst_Notes`
- Large-file safeguard:
  - respects Excel row limit (1,048,576)
  - splits cleaned data across multiple sheets to prevent row overflow errors

## 3) Document-to-PowerPoint Reporting

Implemented via `DocumentReportRun`:

- Accepted formats: `.txt`, `.md`, `.docx`, `.pdf`
- Extracts text and generates PowerPoint report decks
- Produces:
  - executive snapshot slide
  - AI key points slide
  - section slides from content chunks
- Persists generated `.pptx` for tenant-scoped downloads

## 4) Dashboard (Web)

Dashboard now includes:

- KPI cards (tasks, meetings, reports, presentations, run success rates)
- Chart panels:
  - Data Quality Trend
  - Document Output Trend
  - Pipeline Health
  - Keyword Radar
- Runtime profile panel:
  - CPU count
  - CPU target
  - worker threads
  - device/GPU name (if available)
  - embedding model identifier

## 5) Auth and UX

- Styled login/register/logout flow
- Shared visual system (`static/css/app.css`)
- Workspace navigation:
  - Dashboard
  - Tasks
  - Reporting Lab
  - Presentations

---

## Runtime/Performance Profile

Current runtime controls:

- `OFFICE_CPU_TARGET` (default `0.75`)
- thread caps set for numerical workloads (`OMP`, `MKL`, etc.)
- GPU-aware detection path (CUDA/`nvidia-smi` when available)

Semantic summarization path:

- primary hook for embedding-model backend
- robust fallback keyword/sentence scoring path for compatibility

---

## Known Constraints

1. Native Excel slicer objects are not authored directly via `openpyxl`.
   - Pivot sheets are generated and ready for slicer insertion in desktop Excel.
2. Python 3.14 ecosystem compatibility is still evolving for some heavy NLP stacks.
   - fallback summarization path remains stable and production-safe.
3. Dashboard is now substantially richer, but can still be pushed further:
   - drill-down pages
   - cross-filter interactions
   - scheduled report jobs

---

## Suggested Next Priorities

1. Add asynchronous job execution (Celery/RQ) for very large files.
2. Add data-domain presets (healthcare, logistics, finance) with domain-specific KPI templates.
3. Add interactive dashboard filtering (date range, run type, source filename, domain tag).
4. Add report versioning + diff summaries between analysis runs.
5. Add enterprise observability: run durations, failure taxonomy, per-tenant usage quotas.
