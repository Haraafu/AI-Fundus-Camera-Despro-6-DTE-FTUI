# AI Fundus Camera

An open research prototype for fundus-image processing and AI-assisted retinal screening. The wider Capstone Project aims to connect an affordable fundus-camera prototype with an extensible software workflow for image acquisition, preprocessing, analysis, visualisation, and reporting.

This repository currently contains the diabetic retinopathy (DR) machine-learning pipeline. It is intended for academic and research use only and is **not** a certified medical device or a substitute for examination and diagnosis by a qualified clinician.

## Current Capability

The pipeline trains an EfficientNetB3 classifier to categorise fundus photographs into five diabetic-retinopathy severity classes:

| Label | Class |
| --- | --- |
| 0 | No_DR |
| 1 | Mild |
| 2 | Moderate |
| 3 | Severe |
| 4 | Proliferate_DR |

The preprocessing workflow:

1. Finds each source image using its `id_code` from `train.csv`.
2. Converts the OpenCV image from BGR to RGB.
3. Crops black borders around the fundus image.
4. Resizes the image to 300 x 300 pixels.
5. Improves local contrast using CLAHE in LAB colour space.
6. Applies light Gaussian denoising and stores the result as a PNG.

The training workflow uses ImageNet-initialised EfficientNetB3, data augmentation, class weighting for imbalanced data, model checkpoints, early stopping, and two training stages: classification-head training followed by fine-tuning of the final 30% of backbone layers.

## Project Structure

```text
.
|-- preprocess.py                 # Fundus image preprocessing pipeline
|-- train_efficientnetb3.py       # EfficientNetB3 training and fine-tuning
|-- train.csv                     # Image IDs and DR diagnosis labels
|-- colored_images/               # Original images grouped by class (ignored)
|-- preprocessed_images/          # Generated images grouped by class (ignored)
|-- models/                       # Generated .keras model files (ignored)
|-- Figure_1.png
`-- Figure_2.png
```

## Requirements

- Python 3.10 or later
- TensorFlow
- OpenCV
- NumPy
- pandas
- scikit-learn
- matplotlib
- tqdm

Install the required packages in a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install tensorflow opencv-python numpy pandas scikit-learn matplotlib tqdm
```

TensorFlow's hardware support depends on the installed version, Python version, operating system, and available CUDA-compatible GPU configuration.

## Dataset Preparation

Place the original fundus images in class-specific folders under `colored_images`:

```text
colored_images/
|-- No_DR/
|-- Mild/
|-- Moderate/
|-- Severe/
`-- Proliferate_DR/
```

The CSV file must contain these columns:

```csv
id_code,diagnosis
000c1434d8d7,2
```

`id_code` must match the image filename without its extension. The preprocessing script supports `.png`, `.jpg`, and `.jpeg` source files.

## Usage

### 1. Preprocess Images

```powershell
python preprocess.py
```

Processed 300 x 300 PNG images are written to `preprocessed_images`, preserving the five class folders.

### 2. Train the Model

```powershell
python train_efficientnetb3.py
```

The script creates an 80/20 training-validation split from `preprocessed_images` using a fixed seed (`42`). It produces:

- `models/best_efficientnetb3.keras`: checkpoint with the highest validation accuracy.
- `models/final_efficientnetb3_dr.keras`: model after the final fine-tuning epoch.
- Training and validation accuracy/loss plots shown after training.

## Version-Control Notes

Source images, generated preprocessed images, and trained model files are intentionally excluded through `.gitignore`:

```gitignore
colored_images/
preprocessed_images/
models/
```

This keeps the repository lightweight and prevents GitHub's 100 MB individual-file limit from blocking pushes. Store trained models using Git LFS, GitHub Releases, or suitable external storage when they need to be distributed.

## Roadmap

The Capstone Project proposal describes a broader end-to-end AI fundus-camera system. Planned development includes:

- Grad-CAM heatmaps for model interpretability.
- Fundus-camera acquisition and hardware integration.
- A dashboard for screening-result review and patient records.
- Automated PDF screening reports.
- Expanded multi-disease and health-risk analysis using appropriate open datasets.

More features are coming soon.

## Disclaimer

This work is an educational and research prototype. Any output is preliminary screening information and must be reviewed by qualified healthcare professionals. It must not be used as the sole basis for clinical decisions.