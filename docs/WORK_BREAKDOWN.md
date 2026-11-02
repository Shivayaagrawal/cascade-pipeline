# Work Breakdown and Ownership

This is a solo-friendly work allocation. If multiple people contribute, assign one owner per lane and keep interfaces stable.

| Lane | Owner | Responsibilities | Output |
|---|---|---|---|
| Research protocol | Research lead | Questions, hypotheses, baselines, dataset/license audit, evaluation design | Scope and experiment protocol |
| Data engineering | Data owner | FSC adapter, split integrity, audio QA, manifests | Dataset module and manifest |
| Speech/ASR | Speech owner | Local ASR integration, decoding config, WER, latency | ASR adapter and logs |
| NLU | NLU owner | Intent/slot prediction, schema validation, semantic metrics | NLU module |
| Failure engineering | Reliability owner | Perturbations, propagation traces, risk rules, controller | Failure and recovery modules |
| Evaluation | Evaluation owner | Experiment runner, metrics, aggregation, ablations | Reproducible results |
| Demo/report | Delivery owner | CLI/Streamlit, diagrams, case studies, report | Demo and research report |

## Solo execution

Work in this order:

1. Data
2. Metrics
3. Baseline NLU
4. ASR
5. Baseline benchmark
6. Perturbations
7. B1
8. B2
9. Evaluation
10. Demo/report

Avoid parallelizing code before module contracts are stable.

## Suggested module contracts

- DatasetAdapter.iter_split(split) -> Sample
- ASR.transcribe(audio, config) -> ASRResult
- NLU.predict(text) -> SemanticFrame
- Perturbation.apply(sample, spec, seed) -> PerturbedSample
- RiskAnalyzer.assess(asr_result, candidate_frames, schema) -> RiskReport
- Controller.decide(risk_report, policy) -> RecoveryAction
- Evaluator.evaluate(records) -> MetricsReport

Every result object should include sample ID, run ID, model/config identifier and timestamp.
