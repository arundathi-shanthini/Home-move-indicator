import sys

from home_move_indicator_data import get_data_for_home_move_predictor
from home_move_indicator_viz import visualise_locations

def run_home_move_predictor(area_list,from_notebook=False):
    # Get data
    data=get_data_for_home_move_predictor(area_list)
    print()
    print('Plotting the map:')
    # Visualise the data returned
    fig=visualise_locations(data,from_notebook)
    return

if __name__=='__main__':
    # Check for arguments passed and save that as area_list
    if(len(sys.argv)==1):
        print('No area outcodes were passed!\nProgram will exit now.')
        exit()
    area_list=sys.argv[1:]
    run_home_move_predictor(area_list)
