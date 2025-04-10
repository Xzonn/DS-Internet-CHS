import os

import ndspy.lz10
from helper import DIR_ORIGINAL_FILES, DIR_UNPACKED_FILES


def decompress_lz(input_root: str, output_root: str):
  for root, dirs, files in os.walk(input_root):
    for file_name in files:
      if not file_name.endswith(".l"):
        continue
      input_path = f"{root}/{file_name}"
      relative_path = os.path.relpath(input_path, input_root).replace("\\", "/")
      output_path = f"{output_root}/{relative_path.removesuffix('.l')}"
      os.makedirs(os.path.dirname(output_path), exist_ok=True)
      with open(input_path, "rb") as reader:
        with open(output_path, "wb") as writer:
          writer.write(ndspy.lz10.decompress(reader.read()))


if __name__ == "__main__":
  decompress_lz(DIR_ORIGINAL_FILES, DIR_UNPACKED_FILES)
