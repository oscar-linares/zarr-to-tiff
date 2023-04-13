import xarray as xr
import zarr
import rasterio
import os
from rasterio import transform
import sys


# UDFs
def zarr_to_tiff(zarr_path, tif_path, scale):
    print(f"Processing folder: {zarr_path}")

    # define vars
    year = int(zarr_path[-4:])
    anchor_var = "GPP_mean"  # assumes GPP mean is always available, should check for data vars available
    out_path = tif_path + f"/gpp_cte_st_nt_{year}.tif"

    # load zarr to xarray
    zarr_obj = zarr.convenience.open(zarr_path)
    zarr.consolidate_metadata(zarr_obj.store)
    ds = xr.open_zarr(zarr_path)

    # set coordinate reference system
    ds_out = (
        ds.sel(time=(ds.time.dt.year == year))
        .squeeze("time")
        .rio.write_crs("epsg:4326")
    )
    ds_out = ds_out * scale
    ds_out = ds_out.rio.set_spatial_dims(x_dim="x", y_dim="y")

    # Make transform matrix
    west = ds_out.x[0]  # first x coord
    east = ds_out.x[-1]  # last x coord
    south = ds_out.y[0]  # first y coord
    north = ds_out.y[-1]  # last y coord
    width = ds[anchor_var].shape[1]  # x shape
    height = ds[anchor_var].shape[2]  # y shape
    transform_mx = transform.from_bounds(
        west=west, south=south, east=east, north=north, width=width, height=height
    )

    # apply transformation matrix
    affine_transformer = rasterio.Affine(
        transform_mx[0].data,
        transform_mx[1].data,
        transform_mx[2].data,
        transform_mx[3].data,
        transform_mx[4].data,
        transform_mx[5].data,
    )

    ds_out = ds_out.rio.write_transform(affine_transformer)

    # export as tif
    ds_out.rio.to_raster(out_path)

    return f"zarr for {year} was successfully converted to tif"


def zarr_to_tiff_to_all_folders(root_folder, out_folder, scale):
    cedar_scale = scale
    for folder_name in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder_name)
        if os.path.isdir(folder_path):
            zarr_to_tiff(zarr_path=folder_path, tif_path=out_folder, scale=cedar_scale)


# set directories
zar_dir = "./" + sys.argv[1]
tif_dir = "./" + sys.argv[2]

# unpack zarr
zarr_to_tiff_to_all_folders(root_folder=zar_dir, out_folder=tif_dir, scale=1)
