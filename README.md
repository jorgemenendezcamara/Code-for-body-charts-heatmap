[README.md](https://github.com/user-attachments/files/28138033/README.md)

# Body Chart Heatmap Generator

Generate heatmaps from patient body chart images to visualize the
percentage of patients who marked specific areas (e.g., pain locations,
symptoms).

## Overview

This tool processes a set of PNG images (body charts marked by patients)
and generates: 1. A normalized heatmap matrix showing the proportion of
patients who marked each pixel 2. A visual overlay of the heatmap on a
template body chart image

The pipeline consists of two scripts: - **Python script**: Reads PNG
files, detects marked areas, and exports a CSV matrix - **R script**:
Loads the matrix and creates publication-ready heatmap overlays

## Requirements

### Python

-   Python 3.8+
-   Packages listed in `requirements.txt`

### R

-   R 4.0+
-   Packages: ggplot2, readr, tidyr, dplyr, png, grid, optparse

## Repository

<https://github.com/jorgemenendezcamara>

# Install Python dependencies

pip install -r requirements.txt

# Install R dependencies (in R console)

install.packages(c(“ggplot2”, “readr”, “tidyr”, “dplyr”, “png”, “grid”,
“optparse”))
