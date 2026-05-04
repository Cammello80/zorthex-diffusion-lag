# ZORTHEX v1.1 — Public Attention Diffusion Lag Framework

**Status:** Preliminary framework — not peer reviewed  
**Version:** 1.1 (updated May 2026)  
**Author:** Renato [Surname], Independent Researcher, Italy  
**AI Assistance:** Claude (Anthropic) — methodology, code, critique  
**Methodological critique:** ChatGPT (OpenAI)  
**Contact:** zorthex.com | @zorthex on X  

---

## What is this?

This repository contains the full implementation of the **Public Attention Diffusion Lag (L)** framework — a replicable method for measuring the time elapsed between the first public emergence of a technology and its first sustained peak of mainstream search interest.

---

## Key Finding (v1.1 — corrected)

> "The explored data show a broad distribution of diffusion times (L) across emerging technologies, with strong heterogeneity between domains. The biotech_medical subset presents the lowest variance (CV = 0.159), while the AI domain shows high heterogeneity (CV = 0.495), suggesting that domain-level categorization is more informative than a global average. However, results are limited by selection bias, small sample size, and possible censoring effects in historical data."

**What this is NOT:**
- A universal law of technology diffusion
- A tight cluster around a single value
- A prediction tool

**What this IS:**
- An empirical multi-domain framework
- A structured, replicable dataset
- A methodology with explicit uncertainty
- A first evidence of structured heterogeneity

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/zorthex2026/zorthex-diffusion-lag
cd zorthex-diffusion-lag

# 2. Install dependencies
pip install -r requirements.txt

# 3. Reproduce a single result
python pipeline.py --technology "LLM" --file llm.csv --t-start 2017-06 --regime scientific

# Expected output: L = 69 months (5.8 years)

# 4. Run full v1.1 analysis with uncertainty and domain stratification
python analysis_v1.1.py
```

---

## Definitions (Locked — v1.0, unchanged in v1.1)

**t_start** = first moment of public emergence:
- (a) Scientific: seminal paper identified via high citation count
- (b) Commercial: documented public launch date

**t_peak** = first window of >= 3 consecutive months with Google Trends >= 25/100
- Region: Worldwide | Time: full available range | Category: All

**L** = t_peak - t_start in months  
L is an empirical indicator of public attention diffusion. Not a physical constant.

---

## v1.1 Dataset Structure

| Field | Description |
|-------|-------------|
| technology | Technology name |
| domain | Domain category |
| t_start | First public emergence date |
| t_peak | First sustained mainstream peak |
| L_months | Diffusion lag in months |
| uncertainty_low | Lower bound of uncertainty range |
| uncertainty_high | Upper bound of uncertainty range |
| censoring_flag | none / left-censored / right-censored / ambiguous |
| data_quality_score | 0-1 reliability score |

---

## Results (v1.1 — 15 technologies)

| Technology | Domain | L (months) | Uncertainty | Censoring |
|------------|--------|------------|-------------|-----------|
| LLM | AI | 69 | ±3-6 | none |
| mRNA vaccine | biotech_medical | 70 | ±3-6 | none |
| CRISPR | biotech_medical | 51 | ±3-6 | none |
| Deep Learning | AI | 74 | ±4-8 | none |
| Gene Therapy | biotech_medical | 69 | ±4-9 | none |
| GLP-1 | biotech_medical | 84 | ±6-12 | none |
| mRNA cancer vaccine | biotech_medical | 67 | ±7-15 | none |
| Stem cell therapy | biotech_medical | 84 | ±6-14 | none |
| VR | consumer_tech | 71 | ±3-7 | none |
| Quantum Computing | AI | 187 | ±8-16 | none |
| iPhone | consumer_tech | 29 | ±3-7 | none |
| Cloud computing | infrastructure | 29 | ±3-8 | none |
| Facebook | consumer_tech | 59 | ±4-8 | none |
| Bitcoin | financial_tech | 109 | ±4-10 | none |
| Nanotechnology | materials_science | N/A | N/A | left-censored |

### Domain Statistics

| Domain | n | Mean L | CV | Notes |
|--------|---|--------|-----|-------|
| biotech_medical | 6 | 70.8m | 0.159 | Most stable domain |
| consumer_tech | 3 | 53.0m | 0.333 | High product variability |
| AI | 3 | 110.0m | 0.495 | High heterogeneity |
| financial_tech | 1 | 109m | N/A | Single observation |
| infrastructure | 1 | 29m | N/A | Single observation |

Mann-Whitney (biotech vs consumer_tech): not reported — n too small

---

## Explicit Limitations

1. **Survival bias** — only technologies that reached mainstream are included
2. **Selection bias** — technologies chosen for prominence, not random sampling
3. **Proxy limitation** — Google Trends ≠ understanding or adoption
4. **Small sample** — n=15 total; no robust statistical inference possible
5. **Definitional subjectivity** — t_start identification involves judgment
6. **Censoring** — technologies predating Google Trends (2004) are not observable

---

## How to Replicate

1. Choose a technology
2. Identify t_start — document source, date, criterion
3. Download Google Trends CSV: Worldwide, full range, primary keyword
4. Run: `python pipeline.py --technology "X" --file x.csv --t-start YYYY-MM --regime domain`
5. Report all applicable limitations

---

## How to Cite

```
[Surname], R. (2026). Zorthex v1.1: Public Attention Diffusion Lag Framework. 
Preliminary report. zorthex.com. 
GitHub: https://github.com/zorthex2026/zorthex-diffusion-lag
```

---

## License

CC BY 4.0 — Free to use, share, and adapt with attribution.

---

## Changelog

- **v1.0** (May 2026): Initial framework, 10 technologies, single cluster hypothesis
- **v1.1** (May 2026): Added uncertainty ranges, censoring flags, domain stratification, counter-examples. Removed cluster claim — replaced with distribution model.

---

*ZORTHEX.COM — Beyond What's Next — Powered by Claude @AnthropicAI*
