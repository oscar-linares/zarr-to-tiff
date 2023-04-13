#!/bin/sh

# set directory paths
ZARR_DIR=data/GPP_CTE_ST_NT_HYBRID
TIF_DIR=data/geotiff/GPP_CTE_ST_NT_HYBRID
COG_DIR=${TIF_DIR}/COG

# zarr to tiff
python main.py "${ZARR_DIR}" "${TIF_DIR}"

# convert tif to cog tif
for TIF_PATH in "${TIF_DIR}"/*; do
  if [ -f "$TIF_PATH" ]; then
    FILE_NAME=${TIF_PATH##*/}
    COG_PATH=${COG_DIR}/${FILE_NAME%%.*}_cog.tif
    gdal_translate "${TIF_PATH}" "${COG_PATH}" -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW
    python validate_cloud_optimized_geotiff.py "${COG_PATH}"
  fi
done

