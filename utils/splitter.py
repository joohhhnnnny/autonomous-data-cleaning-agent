"""
Dataset splitter utility — splits a folder-structured image dataset
into train / val / test partitions.
"""
import random
import shutil
from pathlib import Path


def split_dataset(
    input_dir,
    output_dir,
    train_ratio=0.7,
    val_ratio=0.2,
    test_ratio=0.1,
    seed=42,
):
    """Split a class-folder dataset into train/val/test sets.

    Expected input structure::

        input_dir/
            class_a/
                img1.jpg
                img2.jpg
            class_b/
                ...

    Output structure::

        output_dir/
            train/class_a/...
            val/class_a/...
            test/class_a/...
    """
    random.seed(seed)

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    for class_dir in input_dir.iterdir():
        if not class_dir.is_dir():
            continue

        images = list(class_dir.glob("*"))
        random.shuffle(images)

        n = len(images)
        train_end = int(train_ratio * n)
        val_end = train_end + int(val_ratio * n)

        splits = {
            "train": images[:train_end],
            "val": images[train_end:val_end],
            "test": images[val_end:],
        }

        for split, files in splits.items():
            target_dir = output_dir / split / class_dir.name
            target_dir.mkdir(parents=True, exist_ok=True)

            for img in files:
                shutil.copy(img, target_dir / img.name)
