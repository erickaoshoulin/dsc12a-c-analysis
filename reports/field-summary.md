# Field summary

Roles are per-field proposals. No complete `dsc_cfg_t` or `dsc_state_t` is treated as static configuration.

## `ANONYMOUS.c`

- Type: `unsigned char[4]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_write, write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `ANONYMOUS.ui`

- Type: `unsigned int`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: hdr_dpx_write, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_DpxFileFormat.FileHeader`

- Type: `GENERICFILEHEADER`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl, dpx_read_hl, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Written by: write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_DpxFileFormat.FilmHeader`

- Type: `INDUSTRYFILMINFOHEADER`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Written by: write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_DpxFileFormat.ImageHeader`

- Type: `GENERICIMAGEHEADER`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, write_dpx_ver, write_dpx_ver
- Written by: dpx_read_hl, dpx_read_hl, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_DpxFileFormat.OrientHeader`

- Type: `GENERICORIENTATIONHEADER`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl, dpx_read_hl, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Written by: write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_DpxFileFormat.TvHeader`

- Type: `INDUSTRYTELEVISIONINFOHEADER`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl, dpx_read_hl
- Written by: write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericFileHeader.Copyright`

- Type: `char[200]`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_GenericFileHeader.Creator`

- Type: `char[100]`
- Role proposal: **UNKNOWN**
- Read by: write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_GenericFileHeader.DittoKey`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericFileHeader.EncryptKey`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericFileHeader.FileName`

- Type: `char[100]`
- Role proposal: **UNKNOWN**
- Read by: write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_GenericFileHeader.FileSize`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericFileHeader.GenericSize`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericFileHeader.ImageOffset`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericFileHeader.IndustrySize`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericFileHeader.Magic`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericFileHeader.Project`

- Type: `char[200]`
- Role proposal: **UNKNOWN**
- Read by: write_dpx_ver, write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_GenericFileHeader.TimeDate`

- Type: `char[24]`
- Role proposal: **UNKNOWN**
- Read by: write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_GenericFileHeader.UserSize`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericFileHeader.Version`

- Type: `char[8]`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl, write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_GenericImageHeader.ImageElement`

- Type: `IMAGEELEMENT[8]`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, write_dpx_ver, write_dpx_ver
- Written by: dpx_read_hl, dpx_read_hl, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericImageHeader.LinesPerElement`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericImageHeader.NumberElements`

- Type: `WORD`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericImageHeader.Orientation`

- Type: `WORD`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericImageHeader.PixelsPerLine`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericOrientationHeader.AspectRatio`

- Type: `DWORD[2]`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl, dpx_read_hl
- Written by: write_dpx_ver, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericOrientationHeader.Border`

- Type: `WORD[4]`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericOrientationHeader.FileName`

- Type: `char[100]`
- Role proposal: **UNKNOWN**
- Read by: write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_GenericOrientationHeader.InputName`

- Type: `char[32]`
- Role proposal: **UNKNOWN**
- Read by: write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_GenericOrientationHeader.InputSN`

- Type: `char[32]`
- Role proposal: **UNKNOWN**
- Read by: write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_GenericOrientationHeader.TimeDate`

- Type: `char[24]`
- Role proposal: **UNKNOWN**
- Read by: write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_GenericOrientationHeader.XCenter`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericOrientationHeader.XOffset`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericOrientationHeader.XOriginalSize`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericOrientationHeader.YCenter`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericOrientationHeader.YOffset`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_GenericOrientationHeader.YOriginalSize`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericFileHeader.Copyright`

- Type: `char[200]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericFileHeader.Creator`

- Type: `char[100]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericFileHeader.DatumMappingDirection`

- Type: `BYTE`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericFileHeader.FileName`

- Type: `char[100]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericFileHeader.FileSize`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: hdr_dpx_write
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericFileHeader.GenericSize`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericFileHeader.ImageOffset`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_compute_offsets, hdr_dpx_compute_offsets, hdr_dpx_compute_offsets, hdr_dpx_write
- Written by: hdr_dpx_compute_offsets
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericFileHeader.IndustrySize`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericFileHeader.Magic`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericFileHeader.Project`

- Type: `char[200]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericFileHeader.StandardsBasedMetadataOffset`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_read, hdr_dpx_read, hdr_dpx_write, hdr_dpx_write
- Written by: hdr_dpx_compute_offsets, hdr_dpx_write
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericFileHeader.TimeDate`

- Type: `char[24]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericFileHeader.UserSize`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_compute_offsets, hdr_dpx_fill_core_fields, hdr_dpx_read, hdr_dpx_read, hdr_dpx_read, hdr_dpx_read, hdr_dpx_write, hdr_dpx_write
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericFileHeader.Version`

- Type: `char[8]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_determine_file_type, hdr_dpx_determine_file_type, hdr_dpx_determine_file_type, hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericImageHeader.ChromaSubsampling`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericImageHeader.ImageElement`

- Type: `HDRDPX_IMAGEELEMENT[8]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_pic_to_datum_list, hdr_dpx_write
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericImageHeader.LinesPerElement`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericImageHeader.NumberElements`

- Type: `WORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_get_pic_data, hdr_dpx_map_datum_to_pic, hdr_dpx_pic_to_datum_list, hdr_dpx_write, hdr_dpx_write
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericImageHeader.Orientation`

- Type: `WORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericImageHeader.PixelsPerLine`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericSourceInfoHeader.AspectRatio`

- Type: `DWORD[2]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericSourceInfoHeader.InputName`

- Type: `char[32]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericSourceInfoHeader.InputSN`

- Type: `char[32]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericSourceInfoHeader.SourceFileName`

- Type: `char[100]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_GenericSourceInfoHeader.SourceTimeDate`

- Type: `char[24]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_HiLoCode.d`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_HiLoCode.f`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_ImageElement.BitSize`

- Type: `BYTE`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_ImageElement.Colorimetric`

- Type: `BYTE`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_ImageElement.DataOffset`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_get_pic_data, hdr_dpx_write
- Written by: hdr_dpx_write
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_ImageElement.DataSign`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_ImageElement.Description`

- Type: `char[32]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_ImageElement.Descriptor`

- Type: `BYTE`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_ImageElement.Encoding`

- Type: `WORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_pic_to_datum_list
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_pic_to_datum_list
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_ImageElement.EndOfImagePadding`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields, hdr_dpx_write
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_ImageElement.EndOfLinePadding`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields, hdr_dpx_get_pic_data, hdr_dpx_write
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_ImageElement.HighData`

- Type: `HDRDPX_HILOCODE`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_ImageElement.LowData`

- Type: `HDRDPX_HILOCODE`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_ImageElement.Packing`

- Type: `WORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_write, hdr_dpx_write
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_ImageElement.Transfer`

- Type: `BYTE`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_IndustryFilmInfoHeader.Count`

- Type: `char[4]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_IndustryFilmInfoHeader.FilmMfgId`

- Type: `char[2]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_IndustryFilmInfoHeader.FilmType`

- Type: `char[2]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_IndustryFilmInfoHeader.Format`

- Type: `char[32]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_IndustryFilmInfoHeader.FrameId`

- Type: `char[32]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_IndustryFilmInfoHeader.FramePosition`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_IndustryFilmInfoHeader.FrameRate`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_IndustryFilmInfoHeader.OffsetPerfs`

- Type: `char[2]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_IndustryFilmInfoHeader.Prefix`

- Type: `char[6]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_IndustryFilmInfoHeader.SequenceLen`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_IndustryFilmInfoHeader.SlateInfo`

- Type: `char[100]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_IndustryTelevisionInfoHeader.FieldNumber`

- Type: `BYTE`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_IndustryTelevisionInfoHeader.FrameRate`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HDRDPX_IndustryTelevisionInfoHeader.Interlace`

- Type: `BYTE`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HdrDpxFileFormat.FileHeader`

- Type: `HDRDPX_GENERICFILEHEADER`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_compute_offsets, hdr_dpx_compute_offsets, hdr_dpx_compute_offsets, hdr_dpx_compute_offsets, hdr_dpx_determine_file_type, hdr_dpx_determine_file_type, hdr_dpx_determine_file_type, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_read, hdr_dpx_read, hdr_dpx_read, hdr_dpx_read, hdr_dpx_read, hdr_dpx_read, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write
- Written by: hdr_dpx_compute_offsets, hdr_dpx_compute_offsets, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_write, hdr_dpx_write
- Evidence:
  - No role taxonomy proof was available

## `_HdrDpxFileFormat.FilmHeader`

- Type: `HDRDPX_INDUSTRYFILMINFOHEADER`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HdrDpxFileFormat.ImageHeader`

- Type: `HDRDPX_GENERICIMAGEHEADER`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_pic_to_datum_list, hdr_dpx_write
- Evidence:
  - No role taxonomy proof was available

## `_HdrDpxFileFormat.SourceInfoHeader`

- Type: `HDRDPX_GENERICSOURCEINFOHEADER`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HdrDpxFileFormat.TvHeader`

- Type: `HDRDPX_INDUSTRYTELEVISIONINFOHEADER`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Written by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields
- Evidence:
  - No role taxonomy proof was available

## `_HdrDpxSbmData.SbmData`

- Type: `uint8_t *`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_write
- Written by: hdr_dpx_read, hdr_dpx_read
- Evidence:
  - No role taxonomy proof was available

## `_HdrDpxSbmData.SbmFormatDescriptor`

- Type: `char[128]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_write, hdr_dpx_write
- Written by: hdr_dpx_read
- Evidence:
  - No role taxonomy proof was available

## `_HdrDpxSbmData.SbmLength`

- Type: `uint32_t`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_read, hdr_dpx_read, hdr_dpx_read, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write
- Written by: hdr_dpx_read
- Evidence:
  - No role taxonomy proof was available

## `_HdrDpxUserData.UserData`

- Type: `uint8_t *`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_write
- Written by: hdr_dpx_read, hdr_dpx_read
- Evidence:
  - No role taxonomy proof was available

## `_HdrDpxUserData.UserIdentification`

- Type: `char[32]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_write, hdr_dpx_write
- Written by: hdr_dpx_read
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.BitSize`

- Type: `BYTE`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.Colorimetric`

- Type: `BYTE`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl
- Written by: write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.DataOffset`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.DataSign`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.Description`

- Type: `char[32]`
- Role proposal: **UNKNOWN**
- Read by: write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.Descriptor`

- Type: `BYTE`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl
- Written by: write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.Encoding`

- Type: `WORD`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.EndOfImagePadding`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.EndOfLinePadding`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.HighData`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl
- Written by: dpx_read_hl, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.HighQuantity`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.LowData`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl
- Written by: dpx_read_hl, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.LowQuantity`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.Packing`

- Type: `WORD`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl
- Written by: write_dpx_ver, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_ImageElement.Transfer`

- Type: `BYTE`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl
- Written by: write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryFilmInfoHeader.Format`

- Type: `char[32]`
- Role proposal: **UNKNOWN**
- Read by: write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_IndustryFilmInfoHeader.FrameId`

- Type: `char[32]`
- Role proposal: **UNKNOWN**
- Read by: write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_IndustryFilmInfoHeader.FramePosition`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryFilmInfoHeader.FrameRate`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryFilmInfoHeader.HeldCount`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryFilmInfoHeader.SequenceLen`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryFilmInfoHeader.ShutterAngle`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryFilmInfoHeader.SlateInfo`

- Type: `char[100]`
- Role proposal: **UNKNOWN**
- Read by: write_dpx_ver
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.BlackGain`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.BlackLevel`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.Breakpoint`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.FieldNumber`

- Type: `BYTE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.FrameRate`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.Gamma`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.HorzSampleRate`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.IntegrationTimes`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.Interlace`

- Type: `BYTE`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_read_hl
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.TimeCode`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.TimeOffset`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.UserBits`

- Type: `DWORD`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.VertSampleRate`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.VideoSignal`

- Type: `BYTE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver, write_dpx_ver, write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_IndustryTelevisionInfoHeader.WhiteLevel`

- Type: `SINGLE`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: write_dpx_ver
- Evidence:
  - No role taxonomy proof was available

## `_datum.d`

- Type: `uint32_t[2]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data
- Written by: hdr_dpx_get_datum, hdr_dpx_get_datum, hdr_dpx_get_datum, hdr_dpx_get_datum
- Evidence:
  - No role taxonomy proof was available

## `_datum_list_s.bit_depth`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_rle_encode, hdr_dpx_rle_encode
- Written by: hdr_dpx_pic_to_datum_list, hdr_dpx_rle_encode
- Evidence:
  - No role taxonomy proof was available

## `_datum_list_s.d`

- Type: `uint32_t *`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write
- Written by: hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode
- Evidence:
  - No role taxonomy proof was available

## `_datum_list_s.eol_flag`

- Type: `uint8_t *`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_write, hdr_dpx_write
- Written by: hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode
- Evidence:
  - No role taxonomy proof was available

## `_datum_list_s.ndatum`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_write
- Written by: hdr_dpx_pic_to_datum_list, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode
- Evidence:
  - No role taxonomy proof was available

## `cmdarg_s.cmd`

- Type: `const char *`
- Role proposal: **UNKNOWN**
- Read by: assign_val, distinguish_dist, distinguish_dist, distinguish_dist, distinguish_dist, error_check, error_check, error_check, error_check, error_check, error_check, error_check, error_check, merge_cmd_args, merge_cmd_args, order_cmds, order_cmds, order_cmds, order_cmds, order_cmds, order_keys, order_keys, parse_cmd, parse_cmd, parse_cmd_usage, parse_cmd_usage, parse_cmd_usage, parse_cmd_usage, parse_key_usage, retrieve_cmds_var, test_cmd, test_cmd
- Written by: merge_cmd_args, merge_cmd_args
- Evidence:
  - No role taxonomy proof was available

## `cmdarg_s.key`

- Type: `const char *`
- Role proposal: **UNKNOWN**
- Read by: assign_val, error_check, error_check, error_check, error_check, error_check, error_check, error_check, error_check, merge_cmd_args, merge_cmd_args, order_keys, order_keys, order_keys, parse_key_usage, parse_key_usage, parse_key_usage, parse_line, parse_line, parse_line, parse_line, retrieve_keys_var
- Written by: merge_cmd_args, merge_cmd_args
- Evidence:
  - No role taxonomy proof was available

## `cmdarg_s.type`

- Type: `argtype_t`
- Role proposal: **UNKNOWN**
- Read by: appendarg, assign_val, assign_val, assign_val, assign_val, assign_val, error_check, error_check, error_check, error_check, error_check, error_check, error_check, error_check, error_check, error_check, error_check, error_check, error_check, error_check, error_check, error_check, error_check, error_check, merge_cmd_args, merge_cmd_args, parse_cmd, parse_cmd, parse_cmd, parse_cmd, parse_cmd, parse_line, test_cmd, test_cmd
- Written by: merge_cmd_args, merge_cmd_args
- Evidence:
  - No role taxonomy proof was available

## `cmdarg_s.value`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: assign_val, merge_cmd_args, merge_cmd_args
- Written by: error_check, merge_cmd_args, merge_cmd_args
- Evidence:
  - No role taxonomy proof was available

## `cmdarg_s.var_ptr`

- Type: `void *`
- Role proposal: **UNKNOWN**
- Read by: assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, merge_cmd_args, merge_cmd_args, merge_cmd_args, merge_cmd_args, parse_cmd, parse_cmd_usage, parse_key_usage, parse_line, retrieve_cmds_var, retrieve_cmds_var, retrieve_keys_var, retrieve_keys_var
- Written by: main, main, main, main, merge_cmd_args, merge_cmd_args
- Evidence:
  - No role taxonomy proof was available

## `cmdarg_s.vct_lng`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, assign_val, error_check, error_check, error_check, error_check, error_check, error_check, merge_cmd_args, merge_cmd_args
- Written by: merge_cmd_args, merge_cmd_args
- Evidence:
  - No role taxonomy proof was available

## `data_u.gc`

- Type: `int **[8]`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, pcopy, pdestroy, pdestroy
- Written by: convertbits, pcopy, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `data_u.gc_d`

- Type: `double **[8]`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits
- Evidence:
  - No role taxonomy proof was available

## `data_u.gc_s`

- Type: `float **[8]`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits
- Evidence:
  - No role taxonomy proof was available

## `data_u.rgb`

- Type: `rgb_t`
- Role proposal: **UNKNOWN**
- Read by: compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convertbits, convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, pcopy, pcopy, pcopy, pcopy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, readppm, readppm, readppm, rgb2ycocg, rgb2ycocg, rgb2ycocg, rgb2yuv, rgb2yuv, rgb2yuv, rgba_read, rgba_read, rgba_read, rgba_read, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, writeppm, writeppm, writeppm, writeppm, writeppm, writeppm
- Written by: convert_rgb_2020_to_709, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convertbits, convertbits, convertbits, convertbits, pcopy, pcopy, pcopy, pcopy, pcreate, pcreate, pcreate, pcreate, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, rgba_read, rgba_read, rgba_read, rgba_read, rgba_read, rgba_read, rgba_read, rgba_read, ycocg2rgb, ycocg2rgb, ycocg2rgb, yuv2rgb, yuv2rgb, yuv2rgb
- Evidence:
  - No role taxonomy proof was available

## `data_u.rgb_d`

- Type: `rgb_d_t`
- Role proposal: **UNKNOWN**
- Read by: convertbits, convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits, convertbits, convertbits, convertbits
- Evidence:
  - No role taxonomy proof was available

## `data_u.rgb_s`

- Type: `rgb_s_t`
- Role proposal: **UNKNOWN**
- Read by: convertbits, convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits, convertbits, convertbits, convertbits
- Evidence:
  - No role taxonomy proof was available

## `data_u.yuv`

- Type: `yuv_t`
- Role proposal: **UNKNOWN**
- Read by: PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, main, main, main, main, main, main, main, main, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, simple422to444, simple422to444, simple422to444, simple422to444, simple422to444, simple422to444, simple422to444, simple444to422, simple444to422, simple444to422, uyvy_write, uyvy_write, uyvy_write, uyvy_write, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, ycocg2rgb, ycocg2rgb, ycocg2rgb, ycocg2rgb, ycocg2rgb, yuv2rgb, yuv2rgb, yuv2rgb, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_422_420, yuv_422_420, yuv_422_420, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_read, yuv_read, yuv_read, yuv_read, yuv_write, yuv_write, yuv_write, yuv_write, yuv_write, yuv_write, yuv_write, yuv_write, yuv_write
- Written by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, ErrorHandler, ErrorHandler, ErrorHandler, ErrorHandler, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, create_dpx_pic, create_dpx_pic, create_dpx_pic, create_dpx_pic, create_dpx_pic, create_dpx_pic, main, main, main, main, main, main, main, main, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, rgb2ycocg, rgb2ycocg, rgb2ycocg, rgb2ycocg, rgb2ycocg, rgb2yuv, rgb2yuv, rgb2yuv, simple422to444, simple422to444, simple422to444, simple422to444, simple422to444, simple444to422, simple444to422, simple444to422, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_422_420, yuv_422_420, yuv_422_420, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_read, yuv_read, yuv_read, yuv_read, yuv_read, yuv_read, yuv_read, yuv_read
- Evidence:
  - No role taxonomy proof was available

## `data_u.yuv_d`

- Type: `yuv_d_t`
- Role proposal: **UNKNOWN**
- Read by: convertbits, convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits
- Evidence:
  - No role taxonomy proof was available

## `data_u.yuv_s`

- Type: `yuv_s_t`
- Role proposal: **UNKNOWN**
- Read by: convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits
- Evidence:
  - No role taxonomy proof was available

## `datum_ptrs_s.alt_chroma`

- Type: `int **[8]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list
- Written by: hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Evidence:
  - No role taxonomy proof was available

## `datum_ptrs_s.datum`

- Type: `int **[8][8]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_pic_to_datum_list
- Written by: hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Evidence:
  - No role taxonomy proof was available

## `datum_ptrs_s.hbuff`

- Type: `int[8]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_get_pic_data, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list
- Written by: hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Evidence:
  - No role taxonomy proof was available

## `datum_ptrs_s.ndatum`

- Type: `int[8]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_map_datum_to_pic, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list
- Written by: hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Evidence:
  - No role taxonomy proof was available

## `datum_ptrs_s.offset`

- Type: `int[8][8]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_get_pic_data, hdr_dpx_pic_to_datum_list
- Written by: hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Evidence:
  - No role taxonomy proof was available

## `datum_ptrs_s.stride`

- Type: `int[8][8]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_pic_to_datum_list
- Written by: hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Evidence:
  - No role taxonomy proof was available

## `datum_ptrs_s.wbuff`

- Type: `int[8]`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list, hdr_dpx_pic_to_datum_list
- Written by: hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Evidence:
  - No role taxonomy proof was available

## `dsc_cfg_t.bits_per_component`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: BlockPredSearch, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState, IsOrigWithinQerr, PredictionLoop, PredictionLoop, Qp2Qlevel, Qp2Qlevel, RateControl, VLCGroup, VLCGroup, VLCUnit, VLCUnit, VLDUnit, VLDUnit, check_qp_for_overflow, check_qp_for_overflow, main, main, main, main, main, main, main, main, main, main, main, main, parse_pps, populate_pps, populate_pps, populate_pps, populate_pps, populate_pps, populate_pps, populate_pps, populate_pps, populate_pps, populate_pps, populate_pps, print_pps, print_pps, print_pps_v2, print_pps_v2, write_pps
- Written by: main, parse_pps, parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.bits_per_pixel`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: CalcFullnessOffset, DSC_Algorithm, RateControl, RateControl, RemoveBitsEncoderBuffer, RemoveBitsEncoderBuffer, RemoveBitsEncoderBuffer, VLCGroup, VLCGroup, compute_rc_parameters, main, print_pps, print_pps, print_pps_v2, print_pps_v2, print_pps_v2, write_pps
- Written by: parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.block_pred_enable`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: BlockPredSearch, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.chunk_size`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: RemoveBitsEncoderBuffer, VLCGroup, VLCGroup, compute_rc_parameters, compute_rc_parameters, main, main, main, print_pps, print_pps_v2, write_pps
- Written by: compute_rc_parameters, parse_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.convert_rgb`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, InitializeDSCState, InitializeDSCState, Qp2Qlevel, check_qp_for_overflow, compute_rc_parameters, main, main, main, main, main, print_pps, print_pps_v2, write_pps
- Written by: main, parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.dsc_version_minor`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: FlatnessAdjustment, IchDecision, IchDecision, MapQpToQlevel, PickBestHistoryValue, Qp2Qlevel, RateControl, RateControl, RateControl, RateControl, RateControl, RateControl, RateControl, RateControl, RateControl, RateControl, compute_rc_parameters, parse_pps, print_pps, print_pps, print_pps_v2, print_pps_v2, write_pps, write_pps
- Written by: parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.final_offset`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: CalcFullnessOffset, CalcFullnessOffset, compute_rc_parameters, compute_rc_parameters, print_pps, print_pps_v2, write_pps
- Written by: compute_rc_parameters, parse_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.first_line_bpg_ofs`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: CalcFullnessOffset, CalcFullnessOffset, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, print_pps, print_pps_v2, write_pps
- Written by: compute_rc_parameters, parse_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.flatness_det_thresh`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: IsOrigFlatHIndex, IsOrigFlatHIndex
- Written by: generate_rc_parameters, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.flatness_max_qp`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: IsFlatnessInfoSent, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: generate_rc_parameters, parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.flatness_min_qp`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: IsFlatnessInfoSent, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: generate_rc_parameters, parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.full_ich_err_precision`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: DSC_Algorithm, PredictionLoop, PredictionLoop
- Written by: populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.initial_dec_delay`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: compute_rc_parameters, main, print_pps, print_pps_v2, write_pps
- Written by: compute_rc_parameters, parse_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.initial_offset`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: InitializeDSCState, compute_rc_parameters, compute_rc_parameters, generate_rc_parameters, populate_pps, populate_pps, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.initial_scale_value`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: CalcFullnessOffset, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, populate_pps, print_pps, print_pps_v2, print_pps_v2, write_pps
- Written by: compute_rc_parameters, compute_rc_parameters, parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.initial_xmit_delay`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: CalcFullnessOffset, CalcFullnessOffset, DSC_Algorithm, RateControl, VLCGroup, compute_rc_parameters, compute_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, main, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: generate_rc_parameters, generate_rc_parameters, parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.linebuf_depth`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: SampToLineBuf, SampToLineBuf, parse_pps, populate_pps, populate_pps, print_pps, print_pps, print_pps_v2, print_pps_v2, write_pps
- Written by: parse_pps, parse_pps, populate_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.mux_word_size`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: InitializeDSCState, InitializeDSCState, InitializeDSCState, ProcessGroupDec, ProcessGroupEnc, VLCGroup, VLCGroup, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters
- Written by: main, populate_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.native_420`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: BlockPredSearch, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, ErrorHandler, HistoryLookup, HistoryLookup, InitializeDSCState, InitializeDSCState, IsOrigWithinQerr, IsOrigWithinQerr, IsOrigWithinQerr, MapQpToQlevel, PickBestHistoryValue, PickBestHistoryValue, PopulateOrigLine, PredictionLoop, Qp2Qlevel, RateControl, UpdateHistoryElement, compute_rc_parameters, main, main, main, main, main, main, main, main, main, main, main, main, main, main, main, main, populate_pps, populate_pps, print_pps, print_pps_v2, print_pps_v2, write_pps
- Written by: main, main, parse_pps, parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.native_422`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, ErrorHandler, ErrorHandler, HistoryLookup, HistoryLookup, InitializeDSCState, InitializeDSCState, PickBestHistoryValue, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, RateControl, RateControl, check_qp_for_overflow, check_qp_for_overflow, compute_rc_parameters, compute_rc_parameters, main, main, main, main, main, main, main, main, main, main, main, populate_pps, print_pps, print_pps_v2, print_pps_v2, write_pps
- Written by: ErrorHandler, main, main, parse_pps, parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.nfl_bpg_offset`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: CalcFullnessOffset, CalcFullnessOffset, check_qp_for_overflow, compute_offset, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, print_pps, print_pps_v2, print_pps_v2, write_pps
- Written by: compute_rc_parameters, compute_rc_parameters, parse_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.nsl_bpg_offset`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: CalcFullnessOffset, CalcFullnessOffset, compute_offset, compute_offset, compute_offset, compute_rc_parameters, compute_rc_parameters, print_pps, print_pps_v2, print_pps_v2, write_pps
- Written by: compute_rc_parameters, compute_rc_parameters, parse_pps, parse_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.pic_height`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: main, main, main, main, main, main, main, populate_pps, populate_pps, populate_pps, populate_pps, populate_pps, populate_pps, populate_pps, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: main, main, parse_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.pic_width`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: UpdateICHistory, main, main, main, main, main, main, main, populate_pps, populate_pps, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: main, main, parse_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.pps_identifier`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: print_pps, print_pps_v2, write_pps
- Written by: parse_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.rc_buf_thresh`

- Type: `int[14]`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: RateControl, populate_pps, populate_pps, print_pps, print_pps_v2, print_pps_v2, write_pps
- Written by: parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.rc_edge_factor`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: RateControl, RateControl, populate_pps, print_pps, print_pps_v2, print_pps_v2, write_pps
- Written by: parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.rc_model_size`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: RateControl, RateControl, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, populate_pps, populate_pps, populate_pps, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.rc_quant_incr_limit0`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: RateControl, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: generate_rc_parameters, parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.rc_quant_incr_limit1`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: RateControl, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: generate_rc_parameters, parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.rc_range_parameters`

- Type: `dsc_range_cfg_t[15]`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: FlatnessAdjustment, FlatnessAdjustment, RateControl, check_qp_for_overflow, check_qp_for_overflow, generate_rc_parameters, generate_rc_parameters, populate_pps, populate_pps, populate_pps, populate_pps, print_pps, print_pps, print_pps, print_pps_v2, print_pps_v2, print_pps_v2, print_pps_v2, write_pps, write_pps, write_pps
- Written by: generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, parse_pps, parse_pps, parse_pps, populate_pps, populate_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.rc_tgt_offset_hi`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: RateControl, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.rc_tgt_offset_lo`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: RateControl, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.rcb_bits`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: RateControl, RateControl, VLCGroup, VLCGroup, VLDGroup, VLDGroup
- Written by: compute_rc_parameters, main, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.scale_decrement_interval`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: CalcFullnessOffset, compute_rc_parameters, print_pps, print_pps_v2, write_pps
- Written by: compute_rc_parameters, compute_rc_parameters, parse_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.scale_increment_interval`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: CalcFullnessOffset, CalcFullnessOffset, compute_rc_parameters, print_pps, print_pps_v2, write_pps
- Written by: compute_rc_parameters, compute_rc_parameters, parse_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.second_line_bpg_ofs`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: CalcFullnessOffset, CalcFullnessOffset, compute_rc_parameters, compute_rc_parameters, print_pps, print_pps_v2, write_pps
- Written by: compute_rc_parameters, parse_pps, parse_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.second_line_ofs_adj`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: CalcFullnessOffset, InitializeDSCState, print_pps, print_pps_v2, write_pps
- Written by: generate_rc_parameters, parse_pps, parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.simple_422`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: main, main, main, main, main, main, main, main, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: main, parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.slice_bpg_offset`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: CalcFullnessOffset, CalcFullnessOffset, check_qp_for_overflow, compute_offset, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, print_pps, print_pps_v2, print_pps_v2, write_pps
- Written by: compute_rc_parameters, parse_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.slice_height`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, ErrorHandler, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, compute_rc_parameters, main, main, main, populate_pps, print_pps, print_pps_v2, rgb2ycocg, write_pps, ycocg2rgb
- Written by: parse_pps, populate_pps, populate_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.slice_width`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: InitializeDSCState, InitializeDSCState, UpdateICHistory, compute_rc_parameters, generate_rc_parameters, generate_rc_parameters, main, main, main, main, main, main, populate_pps, print_pps, print_pps_v2, rgb2ycocg, write_pps, ycocg2rgb
- Written by: parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.somewhat_flat_qp_delta`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: FlatnessAdjustment, FlatnessAdjustment, FlatnessAdjustment, IsOrigFlatHIndex
- Written by: main, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.somewhat_flat_qp_thresh`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: FlatnessAdjustment, FlatnessAdjustment, VLCUnit, VLDUnit
- Written by: main, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.vbr_enable`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, RemoveBitsEncoderBuffer, VLCGroup, main, main, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: parse_pps, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.very_flat_qp`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: FlatnessAdjustment, FlatnessAdjustment, FlatnessAdjustment
- Written by: main, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.xstart`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, ErrorHandler, ErrorHandler, PopulateOrigLine, rgb2ycocg, rgb2ycocg, ycocg2rgb, ycocg2rgb
- Written by: main, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_cfg_t.ystart`

- Type: `int`
- Role proposal: **MUTATED_CONFIGURATION_FIELD**
- Read by: DSC_Algorithm, ErrorHandler, PopulateOrigLine, PopulateOrigLine, rgb2ycocg, rgb2ycocg, ycocg2rgb, ycocg2rgb
- Written by: main, populate_pps
- Evidence:
  - Role is derived from this field's individual read/write sites

## `dsc_history_t.pixels`

- Type: `unsigned int *[4]`
- Role proposal: **UNKNOWN**
- Read by: DSC_Algorithm, HistoryLookup, UpdateHistoryElement
- Written by: DSC_Algorithm, InitializeDSCState, UpdateHistoryElement, UpdateHistoryElement
- Evidence:
  - No role taxonomy proof was available

## `dsc_history_t.valid`

- Type: `int *`
- Role proposal: **UNKNOWN**
- Read by: DSC_Algorithm, InitializeDSCState, IsOrigWithinQerr, PickBestHistoryValue, UpdateHistoryElement
- Written by: InitializeDSCState, InitializeDSCState, IsOrigWithinQerr, UpdateHistoryElement, UpdateHistoryElement, UpdateICHistory, UpdateICHistory
- Evidence:
  - No role taxonomy proof was available

## `dsc_range_cfg_t.range_bpg_offset`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: RateControl, RateControl, populate_pps, print_pps, print_pps_v2, print_pps_v2, write_pps
- Written by: generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, parse_pps, populate_pps
- Evidence:
  - No role taxonomy proof was available

## `dsc_range_cfg_t.range_max_qp`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: FlatnessAdjustment, FlatnessAdjustment, RateControl, RateControl, RateControl, check_qp_for_overflow, check_qp_for_overflow, generate_rc_parameters, generate_rc_parameters, populate_pps, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, parse_pps, populate_pps
- Evidence:
  - No role taxonomy proof was available

## `dsc_range_cfg_t.range_min_qp`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: RateControl, RateControl, populate_pps, print_pps, print_pps_v2, write_pps
- Written by: generate_rc_parameters, generate_rc_parameters, generate_rc_parameters, parse_pps, populate_pps
- Evidence:
  - No role taxonomy proof was available

## `dsc_state_t.bitSaveMode`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: RateControl, RateControl, RateControl, RateControl
- Written by: RateControl, RateControl, RateControl, RateControl, RateControl
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.bitsClamped`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: RemoveBitsEncoderBuffer, RemoveBitsEncoderBuffer
- Written by: DSC_Algorithm, DSC_Algorithm, RemoveBitsEncoderBuffer
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.bpCount`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: BlockPredSearch
- Written by: BlockPredSearch, BlockPredSearch, BlockPredSearch
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.bpgFracAccum`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: RemoveBitsEncoderBuffer, RemoveBitsEncoderBuffer
- Written by: RemoveBitsEncoderBuffer, RemoveBitsEncoderBuffer, RemoveBitsEncoderBuffer
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.bufferFullness`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, RateControl, RateControl, RateControl, RateControl, RateControl, RateControl, RateControl, RateControl, RateControl, VLCGroup, VLCGroup, VLCGroup, VLDGroup, VLDGroup
- Written by: DSC_Algorithm, DSC_Algorithm, InitializeDSCState, RemoveBitsEncoderBuffer, RemoveBitsEncoderBuffer, RemoveBitsEncoderBuffer, VLCGroup, VLDGroup
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.chunkCount`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm
- Written by: DSC_Algorithm, RemoveBitsEncoderBuffer, RemoveBitsEncoderBuffer
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.chunkPixelTimes`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: RemoveBitsEncoderBuffer
- Written by: RemoveBitsEncoderBuffer, RemoveBitsEncoderBuffer
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.chunkSizes`

- Type: `int *`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm
- Written by: DSC_Algorithm, DSC_Algorithm, RemoveBitsEncoderBuffer
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.codedGroupSize`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: RateControl, RateControl, RateControl, RateControl, VLDGroup
- Written by: VLCGroup, VLDGroup
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.cpntBitDepth`

- Type: `int[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: BlockPredSearch, BlockPredSearch, BlockPredSearch, DSC_Algorithm, EscapeCodeSize, FindMidpoint, MapQpToQlevel, MapQpToQlevel, MaxResidualSize, PopulateOrigLine, PredictionLoop, RateControl, RateControl, SampToLineBuf, SamplePredict, SamplePredict, UsingMidpoint, VLCUnit, VLCUnit, VLCUnit, VLCUnit, VLDUnit
- Written by: DSC_Algorithm, DSC_Algorithm
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.currLine`

- Type: `int *[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, PredictionLoop, PredictionLoop, PredictionLoop, PredictionLoop
- Written by: DSC_Algorithm, PredictionLoop
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.currentScale`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: CalcFullnessOffset, CalcFullnessOffset
- Written by: CalcFullnessOffset, CalcFullnessOffset, CalcFullnessOffset, CalcFullnessOffset
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.edgeDetected`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: BlockPredSearch
- Written by: BlockPredSearch, BlockPredSearch
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.encBalanceFifo`

- Type: `fifo_t[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: AddBits, DSC_Algorithm, InitializeDSCState, ProcessGroupEnc, ProcessGroupEnc, ProcessGroupEnc, VLCGroup, VLCGroup, VLCGroup, VLCGroup, VLCGroup, VLCGroup, WriteEntryToBitstream, WriteEntryToBitstream, WriteEntryToBitstream
- Written by: NONE
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.errorOccurred`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm
- Written by: DSC_Algorithm, RateControl, RateControl, VLDGroup
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.firstFlat`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: FlatnessAdjustment, FlatnessAdjustment, FlatnessAdjustment, RateControl, VLCUnit, VLCUnit, VLCUnit, VLDGroup, VLDUnit
- Written by: FlatnessAdjustment, InitializeDSCState, VLDUnit, VLDUnit
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.flatnessType`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: FlatnessAdjustment, FlatnessAdjustment, VLCUnit, VLCUnit, VLDUnit
- Written by: FlatnessAdjustment, FlatnessAdjustment, VLCUnit, VLDUnit, VLDUnit
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.forceMpp`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: VLCUnit, VLCUnit
- Written by: VLCGroup, VLCGroup, VLCGroup
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.groupCount`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: FlatnessAdjustment, FlatnessAdjustment, FlatnessAdjustment, FlatnessAdjustment, VLCGroup, VLCGroup, VLCUnit, VLCUnit, VLDGroup, VLDUnit, VLDUnit
- Written by: DSC_Algorithm, DSC_Algorithm
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.groupCountLine`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: NONE
- Written by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, VLCGroup, VLDGroup
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.hPos`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: EstimateBitsForGroup, IchDecision, UpdateHistoryElement, UseICHistory
- Written by: DSC_Algorithm, DSC_Algorithm
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.history`

- Type: `dsc_history_t`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, HistoryLookup, InitializeDSCState, IsOrigWithinQerr, PickBestHistoryValue, UpdateHistoryElement, UpdateHistoryElement
- Written by: DSC_Algorithm, InitializeDSCState, InitializeDSCState, InitializeDSCState, IsOrigWithinQerr, UpdateHistoryElement, UpdateHistoryElement, UpdateHistoryElement, UpdateHistoryElement, UpdateICHistory, UpdateICHistory
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.ichIndexUnitMap`

- Type: `int[6]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: VLCUnit, VLCUnit, VLDUnit, VLDUnit
- Written by: InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.ichIndicesInGroup`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: IchDecision, UseICHistory, VLCUnit, VLCUnit, VLCUnit, VLCUnit, VLCUnit, VLDUnit, VLDUnit, VLDUnit, VLDUnit
- Written by: InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.ichLookup`

- Type: `int[6]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, UseICHistory, VLCUnit, VLCUnit, VLCUnit, VLDUnit
- Written by: DSC_Algorithm, DSC_Algorithm, VLDUnit, VLDUnit
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.ichPixels`

- Type: `unsigned int[6][4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, UseICHistory, UseICHistory, UseICHistory, UseICHistory
- Written by: NONE
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.ichSelected`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, RateControl, RateControl, RateControl, UpdateHistoryElement, UseICHistory, VLCUnit, VLCUnit, VLDUnit, VLDUnit
- Written by: InitializeDSCState, VLCUnit, VLCUnit, VLDUnit, VLDUnit
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.isEncoder`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, FlatnessAdjustment, PredictionLoop, PredictionLoop, PredictionLoop, ProcessGroupEnc, RateControl, RateControl, RateControl, RemoveBitsEncoderBuffer, UpdateHistoryElement, UpdateHistoryElement
- Written by: DSC_Algorithm
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.lastEdgeCount`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: BlockPredSearch
- Written by: BlockPredSearch, BlockPredSearch, BlockPredSearch
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.lastErr`

- Type: `int[4][3][13]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: BlockPredSearch
- Written by: BlockPredSearch, BlockPredSearch, InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.leftRecon`

- Type: `int[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: FindMidpoint
- Written by: DSC_Algorithm, DSC_Algorithm
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.maxError`

- Type: `int[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: IchDecision, PredictionLoop
- Written by: DSC_Algorithm, PredictionLoop
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.maxIchError`

- Type: `int[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, IchDecision
- Written by: DSC_Algorithm, DSC_Algorithm
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.maxMidError`

- Type: `int[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: IchDecision, PredictionLoop
- Written by: DSC_Algorithm, PredictionLoop
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.maxSeSize`

- Type: `int[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: ProcessGroupDec, ProcessGroupEnc, VLCGroup, VLCGroup
- Written by: InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.midpointRecon`

- Type: `int[4][6]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: PredictionLoop, PredictionLoop, UpdateMidpoint
- Written by: PredictionLoop
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.midpointSelected`

- Type: `int[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: RateControl, RateControl, RateControl, RateControl, UpdateMidpoint
- Written by: DSC_Algorithm, VLCGroup, VLCUnit, VLCUnit
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.mppState`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: RateControl
- Written by: RateControl, RateControl, RateControl
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.native420`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: NONE
- Written by: InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.nonFirstLineBpgTarget`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: NONE
- Written by: InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.numBits`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: ProcessGroupEnc, VLCGroup, VLCGroup, VLCGroup, VLDGroup, VLDGroup
- Written by: AddBits, GetBits, InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.numBitsChunk`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: RemoveBitsEncoderBuffer, RemoveBitsEncoderBuffer, RemoveBitsEncoderBuffer, VLCGroup, VLCGroup
- Written by: RemoveBitsEncoderBuffer, RemoveBitsEncoderBuffer
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.numComponents`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: BlockPredSearch, BlockPredSearch, BlockPredSearch, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, ErrorHandler, HistoryLookup, InitializeDSCState, InitializeDSCState, IsOrigFlatHIndex, IsOrigFlatHIndex, IsOrigFlatHIndex, IsOrigWithinQerr, IsOrigWithinQerr, PopulateOrigLine, UpdateHistoryElement, UpdateHistoryElement, UpdateICHistory, UseICHistory
- Written by: InitializeDSCState, InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.numSsps`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: ProcessGroupDec, ProcessGroupEnc, VLCGroup, VLCGroup, VLCGroup, VLCGroup, WriteEntryToBitstream
- Written by: InitializeDSCState, InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.origIsFlat`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: FlatnessAdjustment, FlatnessAdjustment
- Written by: FlatnessAdjustment, FlatnessAdjustment, FlatnessAdjustment, VLDGroup, VLDGroup
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.origLine`

- Type: `int *[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, IsOrigFlatHIndex, IsOrigFlatHIndex, IsOrigWithinQerr, PredictionLoop
- Written by: DSC_Algorithm, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.origWithinQerr`

- Type: `int[6]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: VLCUnit
- Written by: DSC_Algorithm, IsOrigWithinQerr, IsOrigWithinQerr
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.pixelCount`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: CalcFullnessOffset, CalcFullnessOffset, CalcFullnessOffset, CalcFullnessOffset, CalcFullnessOffset, RateControl, VLCGroup
- Written by: RateControl
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.pixelsInGroup`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: CalcFullnessOffset, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, EstimateBitsForGroup, FlatnessAdjustment, HistoryLookup, HistoryLookup, HistoryLookup, InitializeDSCState, UpdateICHistory, UpdateMidpoint, UseICHistory, VLCGroup
- Written by: InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.postMuxNumBits`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, ProcessGroupDec, ProcessGroupEnc, WriteEntryToBitstream, WriteEntryToBitstream
- Written by: NONE
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.predErr`

- Type: `int[4][13]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: BlockPredSearch
- Written by: BlockPredSearch, BlockPredSearch
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.predictedSize`

- Type: `int[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: GetQpAdjPredSize, RateControl, RateControl, RateControl, RateControl, RateControl, RateControl, RateControl, RateControl
- Written by: InitializeDSCState, VLCUnit, VLDUnit
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.prevFirstFlat`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: FlatnessAdjustment, VLCUnit, VLDUnit, VLDUnit
- Written by: FlatnessAdjustment, FlatnessAdjustment, FlatnessAdjustment, InitializeDSCState, VLDUnit, VLDUnit, VLDUnit
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.prevFlatnessType`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: FlatnessAdjustment
- Written by: FlatnessAdjustment
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.prevIchSelected`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: EstimateBitsForGroup, IchDecision, UpdateHistoryElement, VLCUnit, VLCUnit, VLCUnit, VLCUnit, VLDUnit, VLDUnit
- Written by: VLCUnit, VLDUnit
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.prevIsFlat`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: FlatnessAdjustment
- Written by: FlatnessAdjustment, FlatnessAdjustment, FlatnessAdjustment
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.prevLine`

- Type: `int *[5]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: ErrorHandler, ErrorHandler, ErrorHandler, ErrorHandler, HistoryLookup, HistoryLookup, HistoryLookup, HistoryLookup, HistoryLookup, HistoryLookup, HistoryLookup, HistoryLookup, HistoryLookup, HistoryLookup, HistoryLookup, HistoryLookup, HistoryLookup, HistoryLookup, HistoryLookup, HistoryLookup, HistoryLookup, PredictionLoop, PredictionLoop, PredictionLoop, PredictionLoop
- Written by: DSC_Algorithm, DSC_Algorithm
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.prevLinePred`

- Type: `PRED_TYPE *`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, InitializeDSCState, InitializeDSCState, PredictionLoop
- Written by: BlockPredSearch, BlockPredSearch, InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.prevNumBits`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: VLCGroup, VLCGroup
- Written by: InitializeDSCState, VLCGroup
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.prevPixelCount`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: CalcFullnessOffset
- Written by: CalcFullnessOffset
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.prevPrimaryQp`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: GetQpAdjPredSize
- Written by: InitializeDSCState, VLCGroup, VLDGroup
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.prevQp`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, FlatnessAdjustment, RateControl, RateControl, RateControl, RateControl
- Written by: FlatnessAdjustment, FlatnessAdjustment, InitializeDSCState, RateControl
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.prevRange`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: RateControl
- Written by: RateControl
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.primaryQp`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, EstimateBitsForGroup, EstimateBitsForGroup, EstimateBitsForGroup, FlatnessAdjustment, FlatnessAdjustment, FlatnessAdjustment, FlatnessAdjustment, GetQpAdjPredSize, GetQpAdjPredSize, IsOrigFlatHIndex, UsingMidpoint, VLCGroup, VLCUnit, VLCUnit, VLCUnit, VLCUnit, VLCUnit, VLCUnit, VLDGroup, VLDUnit, VLDUnit, VLDUnit, VLDUnit, VLDUnit, VLDUnit
- Written by: DSC_Algorithm, DSC_Algorithm, InitializeDSCState, PredictionLoop
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.quantTableChroma`

- Type: `int *`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: MapQpToQlevel
- Written by: InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.quantTableLuma`

- Type: `int *`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: MapQpToQlevel, MapQpToQlevel
- Written by: InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState, InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.quantizedResidual`

- Type: `int[4][3]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: EstimateBitsForGroup, PredictionLoop, SamplePredict, SamplePredict, SamplePredict, SamplePredict, UsingMidpoint, VLCGroup, VLCGroup, VLDGroup, VLDGroup, VLDGroup
- Written by: DSC_Algorithm, DSC_Algorithm, InitializeDSCState, PredictionLoop
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.quantizedResidualMid`

- Type: `int[4][3]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: PredictionLoop, PredictionLoop, PredictionLoop, PredictionLoop, VLCUnit, VLCUnit
- Written by: DSC_Algorithm, PredictionLoop, PredictionLoop, PredictionLoop
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.rcOffsetClampEnable`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: CalcFullnessOffset
- Written by: CalcFullnessOffset
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.rcSizeGroup`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: RateControl
- Written by: InitializeDSCState, RateControl
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.rcSizeUnit`

- Type: `int[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: RateControl
- Written by: InitializeDSCState, VLCUnit, VLCUnit, VLCUnit, VLDUnit, VLDUnit, VLDUnit
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.rcXformOffset`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: CalcFullnessOffset, CalcFullnessOffset, CalcFullnessOffset, DSC_Algorithm, DSC_Algorithm
- Written by: CalcFullnessOffset, CalcFullnessOffset, CalcFullnessOffset, InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.scaleAdjustCounter`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: CalcFullnessOffset, CalcFullnessOffset
- Written by: CalcFullnessOffset, CalcFullnessOffset, CalcFullnessOffset, CalcFullnessOffset, CalcFullnessOffset, CalcFullnessOffset
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.scaleIncrementStart`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: CalcFullnessOffset, CalcFullnessOffset
- Written by: CalcFullnessOffset
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.seSizeFifo`

- Type: `fifo_t[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, InitializeDSCState, ProcessGroupEnc, VLCGroup, VLCGroup, WriteEntryToBitstream
- Written by: NONE
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.secondOffsetApplied`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: CalcFullnessOffset
- Written by: CalcFullnessOffset
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.shifter`

- Type: `fifo_t[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, GetBits, InitializeDSCState, ProcessGroupDec, ProcessGroupDec, ProcessGroupEnc, ProcessGroupEnc, ProcessGroupEnc
- Written by: NONE
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.sliceWidth`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, ErrorHandler, EstimateBitsForGroup, FlatnessAdjustment, HistoryLookup, HistoryLookup, InitializeDSCState, InitializeDSCState, IsOrigFlatHIndex, IsOrigFlatHIndex, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, RemoveBitsEncoderBuffer, UpdateMidpoint, VLCGroup
- Written by: InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.stQp`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, FlatnessAdjustment, FlatnessAdjustment, RateControl, RateControl
- Written by: FlatnessAdjustment, FlatnessAdjustment, FlatnessAdjustment, FlatnessAdjustment, InitializeDSCState, RateControl
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.throttleFrac`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: CalcFullnessOffset, CalcFullnessOffset
- Written by: CalcFullnessOffset, CalcFullnessOffset, InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.throttleInt`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: NONE
- Written by: InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.unitCType`

- Type: `int[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, EstimateBitsForGroup, EstimateBitsForGroup, GetQpAdjPredSize, IchDecision, PredictionLoop, SamplePredict, UpdateMidpoint, VLCUnit, VLDUnit
- Written by: InitializeDSCState, InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.unitSspMap`

- Type: `int[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: VLCUnit, VLDUnit
- Written by: InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.unitStartHPos`

- Type: `int[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: EstimateBitsForGroup, PredictionLoop, UpdateMidpoint
- Written by: InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.unitsPerGroup`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, EstimateBitsForGroup, EstimateBitsForGroup, IchDecision, IchDecision, IchDecision, PredictionLoop, RateControl, RateControl, UpdateMidpoint, VLCGroup, VLCGroup, VLCGroup, VLCGroup, VLCGroup, VLCGroup, VLDGroup, VLDGroup, VLDGroup, VLDGroup, VLDUnit, VLDUnit
- Written by: InitializeDSCState, InitializeDSCState, InitializeDSCState
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.useMidpoint`

- Type: `int[4]`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: PredictionLoop, PredictionLoop, RateControl, RateControl, RateControl, RateControl
- Written by: VLDUnit
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `dsc_state_t.vPos`

- Type: `int`
- Role proposal: **RUNTIME_STATE_INPUT_CANDIDATE**
- Read by: IsOrigWithinQerr, IsOrigWithinQerr, PickBestHistoryValue, PickBestHistoryValue, PickBestHistoryValue, RateControl, UpdateHistoryElement, UpdateHistoryElement, UpdateHistoryElement
- Written by: DSC_Algorithm, DSC_Algorithm
- Evidence:
  - Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim

## `fifo_s.byte_ctr`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: fifo_clear, fifo_init
- Evidence:
  - No role taxonomy proof was available

## `fifo_s.data`

- Type: `unsigned char *`
- Role proposal: **UNKNOWN**
- Read by: fifo_flip_get_bits, fifo_free, fifo_get_bits
- Written by: fifo_flip_put_bits, fifo_flip_put_bits, fifo_init, fifo_put_bits, fifo_put_bits
- Evidence:
  - No role taxonomy proof was available

## `fifo_s.fullness`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: DSC_Algorithm, ProcessGroupDec, ProcessGroupEnc, ProcessGroupEnc, VLCGroup, VLCGroup, VLCGroup, VLCGroup, VLCGroup, VLCGroup, WriteEntryToBitstream, fifo_clone, fifo_clone, fifo_clone, fifo_clone, fifo_clone, fifo_clone, fifo_flip_get_bits, fifo_flip_put_bits, fifo_flip_put_bits, fifo_flip_put_bits, fifo_get_bits, fifo_put_bits, fifo_put_bits, fifo_put_bits, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_get_pic_data, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, hdr_dpx_write, read_dpx_image_data, read_dpx_image_data, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Written by: fifo_clear, fifo_flip_get_bits, fifo_flip_put_bits, fifo_get_bits, fifo_init, fifo_put_bits
- Evidence:
  - No role taxonomy proof was available

## `fifo_s.max_fullness`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: fifo_flip_put_bits, fifo_put_bits
- Written by: fifo_clear, fifo_flip_put_bits, fifo_init, fifo_put_bits
- Evidence:
  - No role taxonomy proof was available

## `fifo_s.read_ptr`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: fifo_flip_get_bits, fifo_flip_get_bits, fifo_flip_get_bits, fifo_flip_get_bits, fifo_get_bits, fifo_get_bits, fifo_get_bits
- Written by: fifo_clear, fifo_flip_get_bits, fifo_flip_get_bits, fifo_get_bits, fifo_get_bits, fifo_init
- Evidence:
  - No role taxonomy proof was available

## `fifo_s.size`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: fifo_clone, fifo_clone, fifo_flip_get_bits, fifo_flip_put_bits, fifo_flip_put_bits, fifo_get_bits, fifo_put_bits, fifo_put_bits
- Written by: fifo_init
- Evidence:
  - No role taxonomy proof was available

## `fifo_s.write_ptr`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: fifo_flip_put_bits, fifo_flip_put_bits, fifo_flip_put_bits, fifo_flip_put_bits, fifo_put_bits, fifo_put_bits, fifo_put_bits, fifo_put_bits, fifo_put_bits
- Written by: fifo_clear, fifo_flip_put_bits, fifo_flip_put_bits, fifo_init, fifo_put_bits, fifo_put_bits
- Evidence:
  - No role taxonomy proof was available

## `fir_s.coeff`

- Type: `float[256]`
- Role proposal: **UNKNOWN**
- Read by: conv
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `fir_s.sub`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: conv, conv, conv
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `fir_s.tap`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: conv, conv
- Written by: NONE
- Evidence:
  - No role taxonomy proof was available

## `frange_s.end`

- Type: `float`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: str2frange
- Evidence:
  - No role taxonomy proof was available

## `frange_s.start`

- Type: `float`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: str2frange
- Evidence:
  - No role taxonomy proof was available

## `fxy_dim_s.x`

- Type: `float`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: str2fdim
- Evidence:
  - No role taxonomy proof was available

## `fxy_dim_s.y`

- Type: `float`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: str2fdim
- Evidence:
  - No role taxonomy proof was available

## `pic_s.alpha`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, pcopy_header, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Written by: hdr_dpx_create_pic, main, main, pcopy_header, pcreate, pcreate_ext, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, rgba_read
- Evidence:
  - No role taxonomy proof was available

## `pic_s.ar1`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: dpx_write, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, pcopy_header, read_dpx
- Written by: dpx_read_hl, dpx_read_hl, hdr_dpx_create_pic, pcopy_header, pcreate, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `pic_s.ar2`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: dpx_write, hdr_dpx_fill_core_fields, pcopy_header, read_dpx
- Written by: dpx_read_hl, dpx_read_hl, hdr_dpx_create_pic, pcopy_header, pcreate, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `pic_s.bits`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: DSC_Algorithm, compute_and_display_PSNR, compute_and_display_PSNR, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, dpx_write, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, main, main, main, main, main, main, main, main, main, main, main, main, main, main, main, main, main, main, main, pcopy, pcopy, ppm_write, ppm_write, ppm_write, ppm_write, ppm_write, ppm_write, ppm_write, ppm_write, ppm_write, ppm_write, ppm_write, read_dpx, rgb2ycocg, rgb2ycocg, rgb2yuv, rgb2yuv, rgb2yuv, rgb2yuv, rgb2yuv, rgb2yuv, rgba_read, uyvy_read, uyvy_read, uyvy_write, uyvy_write, writeppm, writeppm, writeppm, writeppm, ycocg2rgb, ycocg2rgb, ycocg2rgb, yuv2rgb, yuv2rgb, yuv2rgb, yuv_420_422, yuv_422_420, yuv_422_444, yuv_444_422, yuv_write
- Written by: dpx_read_hl, main, pcreate_ext, ppm_write
- Evidence:
  - No role taxonomy proof was available

## `pic_s.chroma`

- Type: `chroma_t`
- Role proposal: **UNKNOWN**
- Read by: compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, create_dpx_pic, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, main, main, main, main, main, main, pcopy, pcopy, pcopy, pdestroy, ppm_write, ppm_write, rgb2ycocg, rgb2ycocg, rgb2yuv, rgb2yuv, simple422to444, simple422to444, simple444to422, simple444to422, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, ycocg2rgb, ycocg2rgb, yuv2rgb, yuv2rgb, yuv_422_420, yuv_444_422, yuv_444_422
- Written by: pcreate, pcreate_ext, yuv_422_420, yuv_444_422
- Evidence:
  - No role taxonomy proof was available

## `pic_s.chroma_siting`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields, pcopy_header
- Written by: hdr_dpx_create_pic, main, main, pcopy_header, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `pic_s.color`

- Type: `color_t`
- Role proposal: **UNKNOWN**
- Read by: compute_and_display_PSNR, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convertbits, convertbits, convertbits, convertbits, convertbits, create_dpx_pic, create_dpx_pic, dpx_read_hl, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, main, main, main, main, main, main, main, main, main, main, main, main, main, main, pcopy, pcopy, pcopy, pcopy, pcopy, pdestroy, pdestroy, pdestroy, pdestroy, ppm_write, ppm_write, ppm_write, ppm_write, rgb2ycocg, rgb2ycocg, rgb2ycocg, rgb2yuv, rgb2yuv, rgb2yuv, rgb2yuv, rgb2yuv, simple422to444, simple444to422, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, ycocg2rgb, ycocg2rgb, ycocg2rgb, yuv2rgb, yuv2rgb, yuv2rgb, yuv2rgb, yuv2rgb
- Written by: dpx_read_hl, pcreate, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `pic_s.colorimetry`

- Type: `colorimetry_t`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, pcopy_header
- Written by: dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, main, main, pcopy_header, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `pic_s.data`

- Type: `union data_u`
- Role proposal: **UNKNOWN**
- Read by: PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, main, main, main, main, main, main, main, main, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, readppm, readppm, readppm, rgb2ycocg, rgb2ycocg, rgb2ycocg, rgb2yuv, rgb2yuv, rgb2yuv, rgba_read, rgba_read, rgba_read, rgba_read, simple422to444, simple422to444, simple422to444, simple422to444, simple422to444, simple422to444, simple422to444, simple444to422, simple444to422, simple444to422, uyvy_write, uyvy_write, uyvy_write, uyvy_write, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, writeppm, writeppm, writeppm, writeppm, writeppm, writeppm, ycocg2rgb, ycocg2rgb, ycocg2rgb, ycocg2rgb, ycocg2rgb, yuv2rgb, yuv2rgb, yuv2rgb, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_422_420, yuv_422_420, yuv_422_420, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_read, yuv_read, yuv_read, yuv_read, yuv_write, yuv_write, yuv_write, yuv_write, yuv_write, yuv_write, yuv_write, yuv_write, yuv_write
- Written by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, ErrorHandler, ErrorHandler, ErrorHandler, ErrorHandler, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, create_dpx_pic, create_dpx_pic, create_dpx_pic, create_dpx_pic, create_dpx_pic, create_dpx_pic, main, main, main, main, main, main, main, main, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, pcreate_ext, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, readppm, rgb2ycocg, rgb2ycocg, rgb2ycocg, rgb2ycocg, rgb2ycocg, rgb2yuv, rgb2yuv, rgb2yuv, rgba_read, rgba_read, rgba_read, rgba_read, rgba_read, rgba_read, rgba_read, rgba_read, simple422to444, simple422to444, simple422to444, simple422to444, simple422to444, simple444to422, simple444to422, simple444to422, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, ycocg2rgb, ycocg2rgb, ycocg2rgb, yuv2rgb, yuv2rgb, yuv2rgb, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_422_420, yuv_422_420, yuv_422_420, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_read, yuv_read, yuv_read, yuv_read, yuv_read, yuv_read, yuv_read, yuv_read
- Evidence:
  - No role taxonomy proof was available

## `pic_s.format`

- Type: `format_t`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_fill_core_fields, pcopy
- Written by: dpx_read_hl, pcreate, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `pic_s.framerate`

- Type: `float`
- Role proposal: **UNKNOWN**
- Read by: dpx_read_hl, dpx_write, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, pcopy_header, read_dpx
- Written by: dpx_read_hl, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, pcopy_header, pcreate, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `pic_s.frm_no`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: dpx_write, hdr_dpx_fill_core_fields, pcopy_header, read_dpx
- Written by: dpx_read_hl, dpx_read_hl, hdr_dpx_create_pic, pcopy_header, pcreate, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `pic_s.h`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: DSC_Algorithm, ErrorHandler, PopulateOrigLine, PopulateOrigLine, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, convert_rgb_2020_to_709, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, create_dpx_pic, create_dpx_pic, create_dpx_pic, hdr_dpx_fill_core_fields, hdr_dpx_map_datum_to_pic, main, main, main, main, main, main, main, main, main, main, main, main, main, main, main, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pcopy, pdestroy, pdestroy, pdestroy, pdestroy, pdestroy, ppm_write, ppm_write, ppm_write, ppm_write, ppm_write, ppm_write, rgb2ycocg, rgb2ycocg, rgb2ycocg, rgb2yuv, rgb2yuv, rgb2yuv, rgba_read, simple422to444, simple422to444, simple422to444, simple444to422, simple444to422, simple444to422, uyvy_read, uyvy_write, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, writeppm, writeppm, ycocg2rgb, ycocg2rgb, ycocg2rgb, yuv2rgb, yuv2rgb, yuv2rgb, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_422_420, yuv_422_420, yuv_422_420, yuv_422_420, yuv_422_420, yuv_422_420, yuv_422_420, yuv_422_444, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_write
- Written by: main, pcreate, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `pic_s.interlaced`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: dpx_write, hdr_dpx_fill_core_fields, pcopy_header, read_dpx
- Written by: dpx_read_hl, dpx_read_hl, hdr_dpx_create_pic, pcopy_header, pcreate, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `pic_s.limited_range`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields, pcopy_header
- Written by: hdr_dpx_create_pic, hdr_dpx_create_pic, pcopy_header, pcreate_ext, readppm, rgba_read, yuv_read
- Evidence:
  - No role taxonomy proof was available

## `pic_s.seq_len`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: dpx_write, hdr_dpx_fill_core_fields, pcopy_header, read_dpx
- Written by: dpx_read_hl, dpx_read_hl, hdr_dpx_create_pic, pcopy_header, pcreate, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `pic_s.transfer`

- Type: `transfer_t`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, hdr_dpx_fill_core_fields, pcopy_header
- Written by: dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, dpx_read_hl, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, hdr_dpx_create_pic, main, main, pcopy_header, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `pic_s.w`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: DSC_Algorithm, DSC_Algorithm, ErrorHandler, ErrorHandler, PopulateOrigLine, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, compute_and_display_PSNR, convert_rgb_2020_to_709, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, create_dpx_pic, create_dpx_pic, create_dpx_pic, hdr_dpx_fill_core_fields, hdr_dpx_map_datum_to_pic, main, main, main, main, main, main, main, main, main, main, main, main, main, main, main, pcopy, pcopy, pcopy, ppm_write, ppm_write, ppm_write, ppm_write, ppm_write, ppm_write, rgb2ycocg, rgb2ycocg, rgb2ycocg, rgb2yuv, rgb2yuv, rgb2yuv, rgba_read, simple422to444, simple422to444, simple422to444, simple422to444, simple444to422, simple444to422, simple444to422, uyvy_read, uyvy_write, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, writeppm, writeppm, ycocg2rgb, ycocg2rgb, ycocg2rgb, yuv2rgb, yuv2rgb, yuv2rgb, yuv_420_422, yuv_422_420, yuv_422_420, yuv_422_420, yuv_422_420, yuv_422_420, yuv_422_420, yuv_422_420, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_444_422, yuv_write
- Written by: main, pcreate, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `range_s.end`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: str2prange, str2range
- Evidence:
  - No role taxonomy proof was available

## `range_s.start`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: str2prange, str2range
- Evidence:
  - No role taxonomy proof was available

## `rgb_d_s.a`

- Type: `double **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits
- Evidence:
  - No role taxonomy proof was available

## `rgb_d_s.b`

- Type: `double **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits
- Evidence:
  - No role taxonomy proof was available

## `rgb_d_s.g`

- Type: `double **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits
- Evidence:
  - No role taxonomy proof was available

## `rgb_d_s.r`

- Type: `double **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits
- Evidence:
  - No role taxonomy proof was available

## `rgb_s.a`

- Type: `int **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, pcopy, pdestroy, pdestroy, read_dpx_image_data, read_dpx_image_data, rgba_read, write_dpx_ver
- Written by: convertbits, pcopy, pcreate, pcreate_ext, rgba_read, rgba_read
- Evidence:
  - No role taxonomy proof was available

## `rgb_s.b`

- Type: `int **`
- Role proposal: **UNKNOWN**
- Read by: compute_and_display_PSNR, compute_and_display_PSNR, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, pcopy, pdestroy, pdestroy, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, readppm, rgb2ycocg, rgb2yuv, rgba_read, write_dpx_ver, write_dpx_ver, writeppm, writeppm
- Written by: convert_rgb_2020_to_709, convertbits, pcopy, pcreate, pcreate_ext, readppm, readppm, readppm, readppm, readppm, rgba_read, rgba_read, ycocg2rgb, yuv2rgb
- Evidence:
  - No role taxonomy proof was available

## `rgb_s.g`

- Type: `int **`
- Role proposal: **UNKNOWN**
- Read by: compute_and_display_PSNR, compute_and_display_PSNR, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, pcopy, pdestroy, pdestroy, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, readppm, rgb2ycocg, rgb2yuv, rgba_read, write_dpx_ver, write_dpx_ver, writeppm, writeppm
- Written by: convert_rgb_2020_to_709, convertbits, pcopy, pcreate, pcreate_ext, readppm, readppm, readppm, readppm, readppm, rgba_read, rgba_read, ycocg2rgb, yuv2rgb
- Evidence:
  - No role taxonomy proof was available

## `rgb_s.r`

- Type: `int **`
- Role proposal: **UNKNOWN**
- Read by: compute_and_display_PSNR, compute_and_display_PSNR, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convert_rgb_2020_to_709, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, pcopy, pdestroy, pdestroy, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, readppm, rgb2ycocg, rgb2yuv, rgba_read, write_dpx_ver, write_dpx_ver, writeppm, writeppm
- Written by: convert_rgb_2020_to_709, convertbits, pcopy, pcreate, pcreate_ext, readppm, readppm, readppm, readppm, readppm, rgba_read, rgba_read, ycocg2rgb, yuv2rgb
- Evidence:
  - No role taxonomy proof was available

## `rgb_s_s.a`

- Type: `float **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits
- Evidence:
  - No role taxonomy proof was available

## `rgb_s_s.b`

- Type: `float **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits
- Evidence:
  - No role taxonomy proof was available

## `rgb_s_s.g`

- Type: `float **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits
- Evidence:
  - No role taxonomy proof was available

## `rgb_s_s.r`

- Type: `float **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits
- Evidence:
  - No role taxonomy proof was available

## `rle_ll_s.count`

- Type: `int32_t`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode
- Written by: hdr_dpx_rle_encode, hdr_dpx_rle_encode
- Evidence:
  - No role taxonomy proof was available

## `rle_ll_s.d`

- Type: `uint32_t *`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode
- Written by: hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode
- Evidence:
  - No role taxonomy proof was available

## `rle_ll_s.eol_flag`

- Type: `uint8_t`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_rle_encode, hdr_dpx_rle_encode
- Written by: hdr_dpx_rle_encode, hdr_dpx_rle_encode
- Evidence:
  - No role taxonomy proof was available

## `rle_ll_s.f`

- Type: `uint8_t`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_rle_encode, hdr_dpx_rle_encode
- Written by: hdr_dpx_rle_encode, hdr_dpx_rle_encode
- Evidence:
  - No role taxonomy proof was available

## `rle_ll_s.next`

- Type: `struct rle_ll_s *`
- Role proposal: **UNKNOWN**
- Read by: hdr_dpx_rle_encode, hdr_dpx_rle_encode, hdr_dpx_rle_encode
- Written by: hdr_dpx_rle_encode, hdr_dpx_rle_encode
- Evidence:
  - No role taxonomy proof was available

## `xy_dim_s.x`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: str2dim, str2pdim
- Evidence:
  - No role taxonomy proof was available

## `xy_dim_s.y`

- Type: `int`
- Role proposal: **UNKNOWN**
- Read by: NONE
- Written by: str2dim, str2pdim
- Evidence:
  - No role taxonomy proof was available

## `yuv_d_s.a`

- Type: `double **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits
- Evidence:
  - No role taxonomy proof was available

## `yuv_d_s.u`

- Type: `double **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits, convertbits, convertbits
- Evidence:
  - No role taxonomy proof was available

## `yuv_d_s.v`

- Type: `double **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits, convertbits, convertbits
- Evidence:
  - No role taxonomy proof was available

## `yuv_d_s.y`

- Type: `double **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits
- Evidence:
  - No role taxonomy proof was available

## `yuv_s.a`

- Type: `int **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, pcopy, pcopy, pdestroy, pdestroy, pdestroy, pdestroy, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, write_dpx_ver, write_dpx_ver, write_dpx_ver
- Written by: convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, pcopy, pcopy, pcreate, pcreate, pcreate, pcreate_ext, pcreate_ext, pcreate_ext
- Evidence:
  - No role taxonomy proof was available

## `yuv_s.u`

- Type: `int **`
- Role proposal: **UNKNOWN**
- Read by: PopulateOrigLine, PopulateOrigLine, compute_and_display_PSNR, compute_and_display_PSNR, convertbits, convertbits, convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, main, main, pcopy, pcopy, pcopy, pdestroy, pdestroy, pdestroy, pdestroy, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, simple422to444, simple422to444, simple422to444, simple444to422, uyvy_write, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, ycocg2rgb, ycocg2rgb, yuv2rgb, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_422_420, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_444_422, yuv_444_422, yuv_write, yuv_write, yuv_write
- Written by: DSC_Algorithm, DSC_Algorithm, ErrorHandler, convertbits, convertbits, convertbits, create_dpx_pic, create_dpx_pic, create_dpx_pic, main, main, pcopy, pcopy, pcopy, pcreate, pcreate, pcreate, pcreate_ext, pcreate_ext, pcreate_ext, rgb2ycocg, rgb2ycocg, rgb2yuv, simple422to444, simple422to444, simple444to422, uyvy_read, uyvy_read, uyvy_read, yuv_420_422, yuv_420_422, yuv_422_420, yuv_422_444, yuv_422_444, yuv_444_422, yuv_444_422, yuv_read, yuv_read
- Evidence:
  - No role taxonomy proof was available

## `yuv_s.v`

- Type: `int **`
- Role proposal: **UNKNOWN**
- Read by: PopulateOrigLine, PopulateOrigLine, compute_and_display_PSNR, compute_and_display_PSNR, convertbits, convertbits, convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, main, main, main, pcopy, pcopy, pcopy, pdestroy, pdestroy, pdestroy, pdestroy, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, simple422to444, simple422to444, simple422to444, simple444to422, uyvy_write, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, ycocg2rgb, ycocg2rgb, yuv2rgb, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_422_420, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_422_444, yuv_444_422, yuv_444_422, yuv_write, yuv_write, yuv_write
- Written by: DSC_Algorithm, DSC_Algorithm, ErrorHandler, convertbits, convertbits, convertbits, create_dpx_pic, create_dpx_pic, create_dpx_pic, main, main, main, pcopy, pcopy, pcopy, pcreate, pcreate, pcreate, pcreate_ext, pcreate_ext, pcreate_ext, rgb2ycocg, rgb2ycocg, rgb2yuv, simple422to444, simple422to444, simple444to422, uyvy_read, uyvy_read, uyvy_read, yuv_420_422, yuv_420_422, yuv_422_420, yuv_422_444, yuv_422_444, yuv_444_422, yuv_444_422, yuv_read, yuv_read
- Evidence:
  - No role taxonomy proof was available

## `yuv_s.y`

- Type: `int **`
- Role proposal: **UNKNOWN**
- Read by: PopulateOrigLine, PopulateOrigLine, PopulateOrigLine, compute_and_display_PSNR, compute_and_display_PSNR, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, main, main, main, pcopy, pcopy, pcopy, pcopy, pdestroy, pdestroy, pdestroy, pdestroy, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, read_dpx_image_data, simple422to444, simple444to422, uyvy_write, uyvy_write, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, write_dpx_ver, ycocg2rgb, yuv2rgb, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_422_420, yuv_422_444, yuv_422_444, yuv_444_422, yuv_444_422, yuv_read, yuv_read, yuv_read, yuv_read, yuv_write, yuv_write, yuv_write
- Written by: DSC_Algorithm, DSC_Algorithm, DSC_Algorithm, ErrorHandler, ErrorHandler, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, main, main, main, pcopy, pcopy, pcopy, pcopy, pcreate, pcreate, pcreate, pcreate_ext, pcreate_ext, pcreate_ext, rgb2ycocg, rgb2yuv, simple422to444, simple444to422, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, uyvy_read, yuv_420_422, yuv_420_422, yuv_420_422, yuv_420_422, yuv_422_420, yuv_422_444, yuv_422_444, yuv_444_422, yuv_444_422, yuv_read, yuv_read, yuv_read, yuv_read
- Evidence:
  - No role taxonomy proof was available

## `yuv_s_s.a`

- Type: `float **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits
- Evidence:
  - No role taxonomy proof was available

## `yuv_s_s.u`

- Type: `float **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits, convertbits, convertbits
- Evidence:
  - No role taxonomy proof was available

## `yuv_s_s.v`

- Type: `float **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits, convertbits, convertbits
- Evidence:
  - No role taxonomy proof was available

## `yuv_s_s.y`

- Type: `float **`
- Role proposal: **UNKNOWN**
- Read by: convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic, hdr_dpx_map_datum_to_pic
- Written by: convertbits, convertbits, convertbits, convertbits, convertbits, convertbits, convertbits
- Evidence:
  - No role taxonomy proof was available

## dsc_state_t role split

- Constant-initializer array globals and their pointer uses are recorded in `value-ranges.json` and field facts.
- Production-reachable state fields: runtime-state input candidate based on observed access sites; fields outside that path remain model-only-or-runtime UNKNOWN.
- This report does not infer sequential hardware from state access.

## Quant table initialization and use

- Constant-initializer table declarations, observed readers, and value ranges are emitted without a function-name allowlist.
