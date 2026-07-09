# GNSS Precursor Detector

Detection of seismic precursors through GNSS vertical deformation trend analysis

## Description

This repository contains the source code for the GNSS Precursor Detector, a methodology to detect anomalous accelerations in ground vertical deformation weeks before earthquakes of magnitude >= 7.

The method uses 30-day sliding windows and the Mann-Kendall test to identify statistically significant trends (p < 0.05) in GNSS time series.

## Methodology

The algorithm consists of four stages:

1. **Data loading**: Extracts the vertical component (height) from `.tenv3` files provided by the Nevada Geodetic Laboratory.
2. **Baseline trend calculation**: Fits a linear regression using data prior to the analysis period.
3. **Sliding windows**: Divides the series into 30-day windows with a 5-day step and calculates the anomaly slope for each window.
4. **Acceleration detection**: Applies the Mann-Kendall test to the window slopes to identify significant trends (p < 0.05).

## Validation

The algorithm has been validated in three subduction earthquakes:

- Arequipa 2001 (Mw 8.4) | Station AREQ | p = 0.0018
- Iquique 2014 (Mw 8.2) | Stations PSGA, AEDA, ATJN | p < 0.05
- Arequipa 2018 (Mw 7.1) | Station AREQ | p ≈ 0

A shuffle test with 1000 permutations confirmed that the signal is not noise. In no case did random noise replicate the observed p-value.

## Installation

Clone this repository and install the required dependencies:

```bash
git clone https://github.com/your-username/gnss-precursor-detector.git
cd gnss-precursor-detector
pip install -r requirements.txt