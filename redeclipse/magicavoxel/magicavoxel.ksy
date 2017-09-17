meta:
  id: magicavoxel
  endian: le
  file-extension: vox
  application: Magica Voxel
seq:
  - id: magic
    contents: 'VOX '
  - id: section_type
    type: u4
  - id: main_chunkre
    contents: "MAIN"
  - id: chunk_size
    type: u4
  - id: child_chunk_size
    type: u4
  - id: chunk_contents
    type: u1
    repeat: expr
    repeat-expr: chunk_size
  - id: model_size
    type: size_chunk
  - id: model_voxels
    type: xyzi_chunk
  - id: palette
    type: palette_chunk
types:
  size_chunk:
    seq:
      - id: chunk_identifier
        contents: "SIZE"
      - id: chunk_size
        type: u4
      - id: child_chunk_size
        type: u4
      - id: x
        type: u4
      - id: y
        type: u4
      - id: z
        type: u4
  palette_chunk:
    seq:
      - id: chunk_identifier
        contents: "RGBA"
      - id: chunk_size
        type: u4
      - id: child_chunk_size
        type: u4
      - id: colours
        type: colour
        repeat: expr
        repeat-expr: 256
  xyzi_chunk:
    seq:
      - id: chunk_identifier
        contents: "XYZI"
      - id: chunk_size
        type: u4
      - id: child_chunk_size
        type: u4
      - id: num_voxels
        type: u4
      - id: voxels
        type: voxels
        repeat: expr
        repeat-expr: num_voxels
  voxels:
    seq:
      - id: x
        type: u1
      - id: y
        type: u1
      - id: z
        type: u1
      - id: c
        type: u1
  colour:
    seq:
      - id: r
        type: u1
      - id: g
        type: u1
      - id: b
        type: u1
      - id: a
        type: u1