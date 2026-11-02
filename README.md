# Limitations of the Student Model in High-Demand Contexts: A Structured Review of Underrepresented Functional State Variables

Supplementary materials, data, and code for the manuscript submitted to *IEEE Transactions on Learning Technologies* (L. Vera Franco, I. Tasic, R. Alcázar Corona, and M.-D. Cano).

Adaptive learning systems (ALS) and intelligent tutoring systems (ITS) personalize instruction mainly from knowledge and interaction data, while time-varying states that originate outside the system remain largely unrepresented. This structured review examines 70 ALS and ITS with identifiable student models, published between 1994 and 2024, and asks whether their student models represent six functional state variables (FSV): sleep quality, training load, mental fatigue, perceived stress, competition phase, and academic pressure. Sixty-seven of the 70 systems model none of them; three detect mental fatigue or cognitive load without acting on the estimate. A lexical verification of the complete 3,926-record search corpus and a targeted search beyond the core venues reproduce the pattern. The article proposes a six-category FSV taxonomy, a reference architecture for FSV-aware student models, and three open research questions.

## Repository structure

| Path | Content | Supports |
|---|---|---|
| `supplementary/S1_Protocolo_de_busqueda_y_trazabilidad.docx` | Search protocol: databases, execution dates (28–29 July 2026), vocabulary blocks, and the **exact executable search strings** for Scopus and Web of Science, branches A and B; de-duplication and pre-filter rules; mapping from every published figure to its source file | Section II-A, Fig. 1 |
| `supplementary/S2_raw_exports/` | Raw database exports (Scopus CSV; Web of Science XLS in three batches) — 7,474 records | Section II-A, Fig. 1 |
| `supplementary/S3_Log_de_deduplicacion.xlsx` | De-duplication log (2,970 records removed) | Fig. 1 |
| `supplementary/S4_Registros_excluidos_por_el_prefiltro.xlsx` | Records excluded by the documented pre-filter (578), with the rule applied | Fig. 1 |
| `supplementary/S5_Valoracion_de_calidad_70_sistemas.xlsx` | Quality appraisal of the 70 systems (criteria C1–C5, 0–2 each) | Section II-C, Table I |
| `supplementary/S7_Corpus_de_verificacion.xlsx` | Verification corpus (3,926 records) and the 11 records containing FSV terms, with their individual assessment | Section III-C |
| `supplementary/S8_Analisis_lexico_de_cobertura.xlsx` | Lexical coverage counts per FSV category and related constructs | Section III-C |
| `supplementary/S9_Puntuaciones_por_familia.xlsx` | Quality scores by system family | Table I |
| `supplementary/S10_Lista_comprobacion_PRISMA_ScR.docx` | PRISMA-ScR-informed reporting checklist | Section II-A |
| `data/included_studies_70.csv` | The 70 included systems: system type, application domain, FSV coverage, **identification route** (database search / citation searching), DOI, and full reference | Table IV (Appendix), Fig. 1 |
| `data/targeted_search_systems.csv` | The eight systems identified by the targeted search beyond the core venues | Section III-D, Table III |
| `code/S6_reproduce_analysis.py` | Regenerates S3, S4, S7, and S8 from the raw exports in S2 and checks that the totals match the published figures | Sections II-A and III-C |
| `figures/` | Fig. 1 (PRISMA 2020 flow), Fig. 2 (corpus composition), Fig. 3 (reference architecture), 600 dpi | — |

## Reproducing the counts

```bash
pip install pandas xlrd
python3 code/S6_reproduce_analysis.py \
  --scopus-a supplementary/S2_raw_exports/scopus_ramaA_3953.csv \
  --scopus-b supplementary/S2_raw_exports/scopus_ramaB_508.csv \
  --wos-a    supplementary/S2_raw_exports/wos_ramaA_parte1_1000.xls \
             supplementary/S2_raw_exports/wos_ramaA_parte2_1000.xls \
             supplementary/S2_raw_exports/wos_ramaA_parte3_682.xls \
  --wos-b    supplementary/S2_raw_exports/wos_ramaB_331.xls \
  --outdir   out/
```

The identification route of each included system (`data/included_studies_70.csv`) was obtained by matching the 70 systems against the verification corpus (S7) by DOI or, where the exported record has no DOI, by exact normalized title: 62 systems were retrieved by the database searches and 8 were added through citation searching.

Database counts correspond to the state of Scopus and Web of Science on the execution dates; re-running the strings later will return close but not identical figures. All analyses in the article start from the exports in S2.

## Notes

- Supplementary documents S1 and S10 are written in Spanish; the search strings in S1 are language-independent and can be pasted directly into Scopus and Web of Science.
- The targeted search beyond the core venues (Section II-E) was conducted on 2 November 2026 with general web search engines and citation chaining; it is not exhaustive and its results are listed in `data/targeted_search_systems.csv`.

## Citation

L. Vera Franco, I. Tasic, R. Alcázar Corona, and M.-D. Cano, "Limitations of the student model in high-demand contexts: A structured review of underrepresented functional state variables," submitted to *IEEE Transactions on Learning Technologies*, 2026.

## License

Code (`code/`) is released under the MIT License. Data, documents, and figures are released under the Creative Commons Attribution 4.0 International License (CC BY 4.0). The raw database exports in `supplementary/S2_raw_exports/` remain subject to the Scopus and Web of Science terms of use. See `LICENSE`.
