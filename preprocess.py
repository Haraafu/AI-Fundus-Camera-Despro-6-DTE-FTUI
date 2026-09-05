from pathlib import Path
import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

# =========================
# KONFIGURASI PATH
# =========================

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "train.csv"
INPUT_DIR = BASE_DIR / "colored_images"
OUTPUT_DIR = BASE_DIR / "preprocessed_images"

IMG_SIZE = 300

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# MAPPING LABEL DATASET
# =========================
# Sesuaikan dengan nama folder dataset Anda

label_map = {
    0: "No_DR",
    1: "Mild",
    2: "Moderate",
    3: "Severe",
    4: "Proliferate_DR"
}


# =========================
# FUNGSI BANTU
# =========================

def find_image_path(folder: Path, image_id: str):
    """
    Mencari file gambar dengan beberapa kemungkinan ekstensi.
    """
    for ext in [".png", ".jpg", ".jpeg"]:
        path = folder / f"{image_id}{ext}"
        if path.exists():
            return path
    return None


def crop_black_border(image, threshold=10):
    """
    Menghapus area hitam di sekitar citra fundus.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    mask = gray > threshold

    if mask.sum() == 0:
        return image

    coords = np.argwhere(mask)

    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)

    cropped = image[y_min:y_max + 1, x_min:x_max + 1]
    return cropped


def apply_clahe(image):
    """
    Meningkatkan kontras citra menggunakan CLAHE pada channel luminance.
    """
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    l_clahe = clahe.apply(l)
    lab_clahe = cv2.merge((l_clahe, a, b))

    enhanced = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2RGB)
    return enhanced


def preprocess_fundus_image(image_path: Path, img_size=300):
    """
    Pipeline preprocessing:
    1. Membaca gambar
    2. Mengubah BGR ke RGB
    3. Menghapus border hitam
    4. Resize gambar
    5. Meningkatkan kontras dengan CLAHE
    6. Reduksi noise ringan
    """
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(f"Gambar tidak dapat dibaca: {image_path}")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image = crop_black_border(image)

    image = cv2.resize(
        image,
        (img_size, img_size),
        interpolation=cv2.INTER_AREA
    )

    image = apply_clahe(image)

    # Reduksi noise ringan
    image = cv2.GaussianBlur(image, (3, 3), 0)

    return image


# =========================
# MAIN PROGRAM
# =========================

def main():
    print("Base directory:", BASE_DIR)
    print("CSV path:", CSV_PATH)
    print("Input folder:", INPUT_DIR)
    print("Output folder:", OUTPUT_DIR)

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"File train.csv tidak ditemukan di: {CSV_PATH}")

    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Folder colored_images tidak ditemukan di: {INPUT_DIR}")

    df = pd.read_csv(CSV_PATH)

    if "id_code" not in df.columns or "diagnosis" not in df.columns:
        raise ValueError("train.csv harus memiliki kolom 'id_code' dan 'diagnosis'.")

    success_count = 0
    failed_count = 0

    for _, row in tqdm(df.iterrows(), total=len(df)):
        image_id = str(row["id_code"])
        label = int(row["diagnosis"])

        class_folder = label_map.get(label)

        if class_folder is None:
            print(f"Label tidak dikenali untuk {image_id}: {label}")
            failed_count += 1
            continue

        input_class_dir = INPUT_DIR / class_folder
        output_class_dir = OUTPUT_DIR / class_folder
        output_class_dir.mkdir(parents=True, exist_ok=True)

        image_path = find_image_path(input_class_dir, image_id)

        if image_path is None:
            print(f"Gambar tidak ditemukan: {input_class_dir / image_id}")
            failed_count += 1
            continue

        try:
            processed = preprocess_fundus_image(image_path, IMG_SIZE)

            save_path = output_class_dir / f"{image_id}.png"

            # Convert RGB ke BGR sebelum disimpan oleh OpenCV
            processed_bgr = cv2.cvtColor(processed, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(save_path), processed_bgr)

            success_count += 1

        except Exception as e:
            print(f"Error pada {image_id}: {e}")
            failed_count += 1

    print("\nPreprocessing selesai.")
    print(f"Berhasil diproses : {success_count}")
    print(f"Gagal diproses    : {failed_count}")
    print(f"Hasil disimpan di : {OUTPUT_DIR}")


if __name__ == "__main__":
    main()