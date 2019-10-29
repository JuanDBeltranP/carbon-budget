### Creates tiles in which each pixel is the number of years that natural forest trees are believed to have been growing there between 2001 and 2015.
### While it is for use in calculating cumulative non-mangrove non-planted forest gains, it is not limited to the extent of
### non-mangrove non-planted forest gains.
### Rather, it can include plantation and mangrove pixels, but these are filtered out during the calculation of the
### non-mangrove non-planted forest cumulative gains.
### Thus, this is an overly expansive layer.
### It is based on the annual Hansen loss data and the 2000-2012 Hansen gain data (as well as the 2000 tree cover density data).
### First it calculates rasters of gain years for non-mangrove non-planted forest biomass pixels that had loss only, gain only, neither loss nor gain, and both loss and gain.
### The gain years for each of these conditions are calculated according to rules that are found in the function called by the multiprocessor command.
### Then it combines those four rasters into a single gain year raster for each tile.
### Only the merged raster is used later in the model; the 4 intermediates are saved just for checking.
### If different input rasters for loss (e.g., 2001-2017) and gain (e.g., 2000-2018) are used, the constants in create_gain_year_count_natrl_forest.py must be changed.

import multiprocessing
import gain_year_count_natrl_forest
import argparse
from functools import partial
import sys
sys.path.append('../')
import constants_and_names as cn
import universal_util as uu

def main ():

    # List of output directories and output file name patterns
    output_dir_list = [cn.gain_year_count_natrl_forest_dir]
    output_pattern_list = [cn.pattern_gain_year_count_natrl_forest]

    # The list of tiles to iterate through
    tile_list = uu.tile_list(cn.WHRC_biomass_2000_non_mang_non_planted_dir)
    # tile_list = ["00N_000E", "00N_050W", "00N_060W", "00N_010E", "00N_020E", "00N_030E", "00N_040E", "10N_000E", "10N_010E", "10N_010W", "10N_020E", "10N_020W"] # test tiles
    tile_list = ['00N_110E'] # test tile
    print tile_list
    print "There are {} tiles to process".format(str(len(tile_list))) + "\n"

    # The argument for what kind of model run is being done: standard conditions or a sensitivity analysis run
    parser = argparse.ArgumentParser(description='Create tiles of the number of years of carbon gain for mangrove forests')
    parser.add_argument('--model-type', '-t', required=True,
                        help='{}'.format(cn.model_type_arg_help))
    args = parser.parse_args()
    sensit_type = args.model_type

    # Checks whether the sensitivity analysis argument is valid
    uu.check_sensit_type(sensit_type)

    # For downloading all tiles in the folders
    download_list = [cn.loss_dir, cn.gain_dir, cn.tcd_dir, cn.WHRC_biomass_2000_non_mang_non_planted_dir,
                     cn.planted_forest_type_unmasked_dir, cn.mangrove_biomass_2000_dir]

    # If the model run isn't the standard one, the output directory and file names are changed
    if sensit_type != 'std':

        print "Changing output directory and file name pattern based on sensitivity analysis"

        output_dir_list = uu.alter_dirs(sensit_type, output_dir_list)
        output_pattern_list = uu.alter_patterns(sensit_type, output_pattern_list)
        download_list = uu.alter_dirs(sensit_type, download_list)

    # for input in download_list:
    #     uu.s3_folder_download(input, '.')

    # For copying individual tiles to s3 for testing
    for tile in tile_list:

        uu.s3_file_download('{0}{1}.tif'.format(cn.loss_dir, tile), '.', sensit_type, 'false')
        uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.gain_dir, cn.pattern_gain, tile), '.', sensit_type, 'false')
        uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.tcd_dir, cn.pattern_tcd, tile), '.', sensit_type, 'false')
        uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.WHRC_biomass_2000_non_mang_non_planted_dir, tile, cn.pattern_WHRC_biomass_2000_non_mang_non_planted), '.', sensit_type, 'false')
        uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.planted_forest_type_unmasked_dir, tile, cn.pattern_planted_forest_type_unmasked), '.', sensit_type, 'false')
        uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.mangrove_biomass_2000_dir, tile, cn.pattern_mangrove_biomass_2000), '.', sensit_type, 'false')


    # # Creates gain year count tiles using only pixels that had only loss
    # # count/3 uses about 220 GB on an r4.16xlarge machine
    # # count/2 uses about 330 GB on an r4.16xlarge machine
    # count = multiprocessing.cpu_count()
    # pool = multiprocessing.Pool(processes=36)
    # pool.map(gain_year_count_natrl_forest.create_gain_year_count_loss_only, tile_list)
    #
    # if sensit_type == 'maxgain':
    #     # Creates gain year count tiles using only pixels that had only gain
    #     # count/2 uses about 200 GB on an r4.16xlarge machine
    #     pool.map(gain_year_count_natrl_forest.create_gain_year_count_gain_only_maxgain, tile_list)
    # else:
    #     # Creates gain year count tiles using only pixels that had only gain
    #     pool.map(gain_year_count_natrl_forest.create_gain_year_count_gain_only_standard, tile_list)
    #
    # # Creates gain year count tiles using only pixels that had neither loss nor gain pixels
    # pool.map(gain_year_count_natrl_forest.create_gain_year_count_no_change, tile_list)
    #
    # if sensit_type == 'maxgain':
    #     # Creates gain year count tiles using only pixels that had both loss and gain pixels
    #     pool.map(gain_year_count_natrl_forest.create_gain_year_count_loss_and_gain_maxgain, tile_list)
    # else:
    #     # Creates gain year count tiles using only pixels that had both loss and gain pixels
    #     pool.map(gain_year_count_natrl_forest.create_gain_year_count_loss_and_gain_standard, tile_list)
    #
    # # Creates a single filename pattern to pass to the multiprocessor call
    # pattern = output_pattern_list[0]
    #
    # # Merges the four above gain year count tiles for each Hansen tile into a single output tile
    # count = multiprocessing.cpu_count()
    # pool = multiprocessing.Pool(count/6)
    # pool.map(partial(gain_year_count_natrl_forest.create_gain_year_count_merge, pattern=pattern), tile_list)
    # pool.close()
    # pool.join()

    # For single processor use
    for tile_id in tile_list:
        gain_year_count_natrl_forest.create_gain_year_count_loss_only(tile_id)

    for tile_id in tile_list:
        if sensit_type == 'maxgain':
            gain_year_count_natrl_forest.create_gain_year_count_gain_only_maxgain(tile_id)
        else:
            gain_year_count_natrl_forest.create_gain_year_count_gain_only_standard(tile_id)

    for tile_id in tile_list:
        gain_year_count_natrl_forest.create_gain_year_count_no_change(tile_id)

    for tile_id in tile_list:
        if sensit_type == 'maxgain':
            gain_year_count_natrl_forest.create_gain_year_count_loss_and_gain_maxgain(tile_id)
        else:
            gain_year_count_natrl_forest.create_gain_year_count_loss_and_gain_standard(tile_id)

    for tile_id in tile_list:
        gain_year_count_natrl_forest.create_gain_year_count_merge(tile_id, output_pattern_list[0])

    # Intermediate output tiles for checking outputs
    uu.upload_final_set(output_dir_list[0], "growth_years_loss_only")
    uu.upload_final_set(output_dir_list[0], "growth_years_gain_only")
    uu.upload_final_set(output_dir_list[0], "growth_years_no_change")
    uu.upload_final_set(output_dir_list[0], "growth_years_loss_and_gain")

    # This is the final output used later in the model
    uu.upload_final_set(output_dir_list[0], output_pattern_list[0])


if __name__ == '__main__':
    main()