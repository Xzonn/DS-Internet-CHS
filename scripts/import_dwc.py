import os
import struct

import ndspy
import ndspy.lz10
from helper import DIR_IMAGE_FILES, DIR_ORIGINAL_FILES, DIR_OUT, DIR_TEMP_IMPORT


def import_dwc(input_path: str, output_path: str, replace_dirs: list[str]) -> bool:
  reader = open(input_path, "rb")
  fntOffset, fntSize, fatOffset, fatSize = struct.unpack("<IIII", reader.read(16))

  reader.seek(fatOffset)
  file_count = fatSize // 8
  fatItems = []
  for i in range(file_count):
    startOffset, endOffset = struct.unpack("<II", reader.read(8))
    fatItems.append((startOffset, endOffset))

  os.makedirs(os.path.dirname(output_path), exist_ok=True)

  writer = open(output_path, "wb")
  reader.seek(0)
  writer.write(reader.read(fatItems[0][0]))

  newOffsets = {}
  newOffset = fatItems[0][0]

  reader.seek(fntOffset)
  root = {}

  offset = 0xFFFFFFFF

  while reader.tell() < offset:
    mainOffset, firstPos, parent = struct.unpack("<IHH", reader.read(8))
    idFile = firstPos
    currentPos = reader.tell()
    reader.seek(mainOffset + fntOffset)
    if offset == 0xFFFFFFFF:
      offset = mainOffset + fntOffset
    (id,) = struct.unpack("<B", reader.read(1))
    while id != 0:
      if id & 0x80 == 0:
        fileName = reader.read(id & 0x7F).decode()
        search_path = ""
        for replace_dir in replace_dirs:
          if os.path.exists(f"{replace_dir}/{fileName.removesuffix('.l')}"):
            search_path = f"{replace_dir}/{fileName.removesuffix('.l')}"
            break
        if search_path:
          with open(search_path, "rb") as file:
            writer.write(ndspy.lz10.compress(file.read()))
          print(f"Replacing {fileName} with {search_path}")
          newOffsets[idFile] = (newOffset, writer.tell())
        else:
          _ = reader.tell()
          reader.seek(fatItems[idFile][0])
          writer.write(reader.read(fatItems[idFile][1] - fatItems[idFile][0]))
          newOffsets[idFile] = (newOffset, writer.tell())
          reader.seek(_)
        while writer.tell() % 4 != 0:
          writer.write(b"\xff")
        newOffset = writer.tell()
        idFile += 1
      else:
        folderName = reader.read(id & 0x7F).decode()
        (folderId,) = struct.unpack("<H", reader.read(2))
        root[folderId] = folderName

      (id,) = struct.unpack("<B", reader.read(1))

    reader.seek(currentPos)

  writer.seek(fatOffset)
  for startOffset, endOffset in newOffsets.values():
    writer.write(struct.pack("<II", startOffset, endOffset))

  reader.close()


if __name__ == "__main__":
  for folder in os.listdir(DIR_ORIGINAL_FILES):
    if folder == "common" or not os.path.isdir(f"{DIR_ORIGINAL_FILES}/{folder}"):
      continue

    import_dwc(
      f"{DIR_ORIGINAL_FILES}/{folder}/utility.bin",
      f"{DIR_OUT}/{folder}/utility.bin",
      [f"{DIR_TEMP_IMPORT}/{folder}", f"{DIR_TEMP_IMPORT}/common/msg", DIR_IMAGE_FILES],
    )
