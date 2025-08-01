# Copyright (C) 2020-2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# | export

import os
import numpy as np
import nibabel as nib
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from skimage.transform import resize
from copy import deepcopy

def load_nii(file_path):
    img = nib.load(file_path)
    return np.asarray(img.dataobj)

def extract_data(data_path, num_slices=155, stride=5, target_size=(128, 128)):
    images = []
    labels = []
    modalities =["flair", "t1", "t1ce", "t2"]

    for patient_id in os.listdir(data_path):
        patient_path = os.path.join(data_path, patient_id)
        if not os.path.isdir(patient_path):
            continue

        volumes = []
        for mod in modalities:
            mod_path = os.path.join(patient_path, f"{patient_id}_{mod}.nii")
            if not os.path.exists(mod_path):
                print(f"Skipping {patient_id}: missing {mod}")
                break
            volumes.append(load_nii(mod_path))
        else:
            mask_path = os.path.join(patient_path, f"{patient_id}_seg.nii")
            if not os.path.exists(mask_path):
                print(f"Skipping {patient_id}: missing mask")
                continue
            mask_volume = load_nii(mask_path)

            for slice_idx in range(0, num_slices, stride):
                combined_slice = []
                for vol in volumes:
                    slice_img = vol[:, :, slice_idx]
                    if np.max(slice_img) - np.min(slice_img) == 0:
                        break

                    slice_img = resize(slice_img, target_size, preserve_range=True)
                    slice_img = (slice_img - np.min(slice_img)) / (np.max(slice_img) - np.min(slice_img))
                    combined_slice.append(slice_img)

                if len(combined_slice) == 4:
                    combined_slice = np.stack(combined_slice, axis=-1)
                    slice_mask = mask_volume[:, :, slice_idx]
                    label = 1 if np.any(slice_mask > 0) else 0
                    images.append(combined_slice)
                    labels.append(label)
    
    return np.array(images), np.array(labels)

def collect_metadata(input_data, target_data):
    modalities = ["flair", "t1", "t1ce", "t2"]
    metadata = {}

    metadata["num_samples"] = input_data.shape[0]
    metadata["resized_shape"] = input_data.shape[1:3]
    metadata["modalities"] = modalities

    # Class Ratio
    unique, counts = np.unique(target_data, return_counts=True)
    class_dist = dict(zip(map(str, unique), map(int, counts)))
    total = sum(counts)
    class_ratio = {k: float(round(v / total, 4)) for k, v in class_dist.items()}
    metadata["class_distribution"] = class_dist
    metadata["class_ratio"] = class_ratio

    # Stats
    stats = {}
    for i, mod in enumerate(modalities):
        mod_data = input_data[:, :, :, i].flatten()
        stats[mod] = {
            "mean": float(np.mean(mod_data)),
            "median": float(np.median(mod_data)),
            "min": float(np.min(mod_data)),
            "max": float(np.max(mod_data))
        }
    metadata["stats"] = stats
    return metadata

datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True,
    fill_mode='nearest'
)

dir_name = os.path.dirname(__file__)

TRAIN_DATA = f"{dir_name}/dataset/BraTS2020_TrainingData/MICCAI_BraTS2020_TrainingData"
TARGET_SIZE = (128, 128)
CHANNELS = 4
BATCH_SIZE=16

X, y = extract_data(TRAIN_DATA, target_size=TARGET_SIZE)
X = X.astype('float32')
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
y_train_cat = to_categorical(y_train, num_classes=2)
y_val_cat = to_categorical(y_val, num_classes=2)

apollo_attrs = {
    "train_data": X_train,
    "train_labels": y_train_cat,
    "test_data": X_val,
    "test_labels": y_val_cat,
    "metadata": collect_metadata(X, y),
}