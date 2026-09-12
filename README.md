# AI Fundus Camera

AI Fundus Camera is a local research prototype for fundus-image processing and AI-assisted diabetic-retinopathy screening. It combines an image preprocessing and EfficientNetB3 training pipeline with a Node.js backend, a SQLite examination store, and a separate Python AI service.

The project is intended for academic and research use. It is not a certified medical device, does not replace clinical examination, and must not be used as the sole basis for a medical decision.

## Capabilities

The repository provides the following working components:

- A local Express backend for creating examinations, receiving fundus images, validating uploads, coordinating inference, and returning stored results.
- A FastAPI AI service with health monitoring and a structured image-prediction contract.
- A SQLite data store for patients, examinations, uploaded-image metadata, and AI results.
- Image upload validation for supported formats, decompression-bomb protection, maximum file size, maximum pixel count, and image-content verification.
- Examination status tracking from creation through image receipt, processing, completion, or failure.
- A deterministic mock AI adapter for testing service communication without loading a trained model.
- A preprocessing pipeline that crops borders, resizes images, improves contrast with CLAHE, denoises them, and writes class-organised PNG files.
- An EfficientNetB3 training workflow with augmentation, class weighting, checkpointing, early stopping, learning-rate reduction, and fine-tuning.
- Integration tests covering successful requests, validation failures, AI failures, timeouts, concurrent uploads, persistence, and corrupted images.
- A smoke-test script for exercising the local backend with a dataset image.

## System Flow

```text
Client
  -> Express backend
  -> Upload validation and temporary storage
  -> Python AI service
  -> Structured prediction
  -> SQLite persistence
  -> Examination result
```

Uploaded originals are preserved in `data/uploads/`. The backend forwards the image to the AI service, stores the returned result, and exposes the completed examination through its API.

## Services and API

### Node.js backend

The backend listens on `http://127.0.0.1:3001` by default.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check backend availability |
| `POST` | `/api/examinations` | Create an examination |
| `POST` | `/api/examinations/:id/images` | Upload and analyse one fundus image |
| `GET` | `/api/examinations/:id` | Retrieve examination, image, and result data |

Creating an examination requires a patient identifier, eye selection (`LEFT` or `RIGHT`), and capture type (`MACULA_CENTERED` or `OPTIC_DISC_CENTERED`). Uploaded files must be PNG or JPEG images. The default maximum upload size is 10 MiB and the default maximum image size is 40 megapixels.

### Python AI service

The FastAPI service listens on `http://127.0.0.1:8000` by default. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Report service and model status |
| `POST` | `/predict` | Validate an image and return a prediction contract |

The default service uses a mock adapter. For every valid image, it returns a deterministic response with:

```json
{
  "success": true,
  "prediction": {
    "class": "Moderate",
    "confidence": 0.81
  },
  "probabilities": {
    "No_DR": 0.02,
    "Mild": 0.07,
    "Moderate": 0.81,
    "Severe": 0.08,
    "Proliferate_DR": 0.02
  },
  "riskLevel": "MEDIUM",
  "modelVersion": "mock-v0",
  "isMock": true
}
```

This response verifies the integration contract and persistence flow. It is not a real clinical inference. The service also rejects invalid or corrupted image payloads.

## Examination Lifecycle

An examination follows this state model:

```text
CREATED -> IMAGE_RECEIVED -> PROCESSING -> COMPLETED
                                      \\-> FAILED
```

The backend preserves the original upload when processing fails and records an error code and message. A second upload for the same examination is rejected after the first upload has started; a new examination should be created for a retake. If the backend restarts during processing, the interrupted examination is marked as failed.

## Data Storage (Still Temporary)

SQLite is created automatically at `data/fundus.sqlite`. The store contains:

- `patients`: patient identifiers and creation timestamps.
- `examinations`: examination metadata and lifecycle status.
- `fundus_images`: uploaded-image metadata and file references.
- `ai_results`: prediction, confidence, probabilities, risk level, model version, and mock flag.

The service stores extensible JSON documents for examination, image, and AI-result records. Uploaded files are stored under `data/uploads/` while the database keeps their metadata and references.

## Machine-Learning Pipeline

### Supported classes

The EfficientNetB3 classifier uses five diabetic-retinopathy classes:

| Label | Class |
| --- | --- |
| `0` | `No_DR` |
| `1` | `Mild` |
| `2` | `Moderate` |
| `3` | `Severe` |
| `4` | `Proliferate_DR` |

### Preprocessing

Run `preprocess.py` to transform the source dataset from `colored_images/` into `preprocessed_images/`. For each image, the pipeline:

1. Finds the source file using its `id_code` from `train.csv`.
2. Converts OpenCV BGR data to RGB.
3. Crops black borders around the fundus image.
4. Resizes the image to 300 x 300 pixels.
5. Applies CLAHE contrast enhancement in LAB colour space.
6. Applies light Gaussian denoising.
7. Saves a PNG in the corresponding class directory.

### Training

Run `train_efficientnetb3.py` to train an ImageNet-initialised EfficientNetB3 model. The workflow uses an 80/20 split with a fixed seed, data augmentation, class weights for imbalance, checkpointing by validation accuracy, early stopping, and learning-rate reduction. Training has a classification-head stage followed by fine-tuning of the final 30% of the backbone.

The training script produces:

- `models/best_efficientnetb3.keras`: the checkpoint with the best validation accuracy.
- `models/final_efficientnetb3_dr.keras`: the model saved after the final fine-tuning stage.

The standalone training artifacts are available for model development. The default FastAPI service remains a mock adapter and does not load these files automatically.

## Project Structure

```text
.
|-- apps/
|   |-- backend/
|   |   |-- src/
|   |   `-- test/
|   `-- frontend/              # Frontend application directory
|-- services/
|   `-- ai-service/             # FastAPI AI service
|-- scripts/
|   `-- smoke.mjs               # Local API smoke test
|-- data/
|   `-- uploads/                # Uploaded originals
|-- colored_images/             # Source dataset, ignored by Git
|-- preprocessed_images/        # Generated dataset, ignored by Git
|-- models/                     # Generated model files, ignored by Git
|-- preprocess.py
|-- train_efficientnetb3.py
|-- train.csv
|-- package.json
`-- README.md
```

## Requirements

- Node.js 22.13 or later. The backend uses Node's built-in SQLite support.
- Python 3.10 or later.
- Python packages listed in `services/ai-service/requirements.txt`.
- TensorFlow and the preprocessing dependencies when running the training pipeline.
- A local copy of the dataset when running preprocessing, training, or the smoke test with a dataset image.

## Setup

Run these commands from the repository root.

```powershell
npm ci
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r services/ai-service/requirements.txt
Copy-Item .env.example .env
```

Start the AI service in one terminal:

```powershell
.\.venv\Scripts\python.exe services/ai-service/app.py
```

Start the backend in a second terminal:

```powershell
npm run backend
```

Run a local smoke test in a third terminal:

```powershell
npm run smoke -- "colored_images/Moderate/000c1434d8d7.png"
```

Replace the image path with a file that exists locally. Use anonymous patient identifiers for test data.

On Linux or macOS, use `.venv/bin/python` and run:

```bash
PYTHON=.venv/bin/python npm test
```

## Testing

Run the automated integration suite with:

```powershell
npm test
```

The test setup starts the Python service when needed, uses temporary ports and a temporary SQLite database, and cleans up after the run. The suite exercises health checks, successful mock inference, byte preservation, database persistence, malformed metadata, missing files, spoofed images, oversized uploads, AI unavailability, timeouts, contract failures, concurrent upload locking, and corrupted-image rejection.

## Configuration and Generated Files

The local environment can be configured through `.env` and `.env.example`. Common settings include the backend port, AI service URL, database location, and upload directory.

Generated datasets, model files, SQLite databases, uploaded files, virtual environments, logs, and environment files are excluded through `.gitignore`. The `docs/` directory and the weekly planning document are also excluded from version control in this workspace.

## Limitations

- The default AI response is deterministic mock data and does not perform real model inference.
- The FastAPI service does not run the standalone preprocessing pipeline before prediction.
- The repository does not provide a clinical image-quality gate, Grad-CAM visualisation, PDF reporting workflow, or hardware/MQTT communication layer.
- The backend is designed for local development and does not provide production authentication, HTTPS, or deployment configuration.
- SQLite usage is intended for a local backend instance rather than a multi-instance production deployment.
- Results are preliminary research output and require review by qualified healthcare professionals.

## License and Use

This project is an educational and research prototype. Review the repository's project materials and dataset terms before redistributing code, images, or trained models.
