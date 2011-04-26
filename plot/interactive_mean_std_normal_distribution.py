### Interactively plot points
### to show their mean, standard deviation, 
### and the Normal distribution with that mean and std.
### By Rajeev Raizada, Jan.2011.
### Requires Python, with the Matplotlib and SciPy modules.
### You can download Python and those modules for free from
### http://www.python.org/download
### http://scipy.org
### http://matplotlib.sourceforge.net
###
### Please feel more than free to use this code for teaching.
### If you use it, I'd love to hear from you!
### If you have any questions, comments or feedback, 
### please send them to me: rajeev dot raizada at dartmouth dot edu
###
### Some tutorial exercises which might be useful to try:
### 1. Click to add n=10 points.
###    Their mean x-value is the large red dot.
###    The vertical lines show standard deviation (SD) distances from the mean.
###    How many of the points lie within one SD of the mean?
###    How many of the points lie within two SDs of the mean?
### 2. Click to add more points, putting most of them near the mean.
###    How many points do you need altogether before some of them
###    start to lie more than two SDs away from the mean?
### 3. When it is three standard deviations away from the mean,
###    the bell-shaped Normal distribution curve is very close to zero.
###    It is so close that you might not even be able to see
###    the very short vertical dotted lines at the 3 SD marks.
###    Click to add a lot of points near the mean,
###    so that the Normal curve gets taller and thinner,
###    and add a couple of far-distant points at the sides.
###    See if you can get some points to lie more than 3 SDs from the mean.

###########################################
# First, we import the modules that we need
import pylab
import scipy
import scipy.stats  # We need this one for the norm.pdf function

#####################################################
# Next, we define the functions that the program uses

### This function clears the figure and empties the points list
def clear_the_figure_and_empty_points_list():
    global coords_array 
    global point_handles_array  
    # Reset our variables to be empty
    coords_array = scipy.array([])
    point_handles_array = scipy.array([])
    handle_of_normal_curve_plot = []
    handle_of_mean_plot = []
    handle_of_std_lines = []
    ### Clear the figure window
    pylab.clf()  # clf means "clear the figure"
    ### In order to keep the boundaries of the figure fixed in place,
    ### we will draw a black box around the region that we want.
    pylab.plot(axis_x_range*scipy.array([-1, 1, 1, -1]),
           scipy.array([axis_y_lower_lim,axis_y_lower_lim,axis_y_upper_lim,axis_y_upper_lim]),'k-')
    ### We want a long title, so we put a \n in the middle, to start a new line of title-text      
    multiline_title_string = 'Click to add points, on old points to delete,' \
                             ' outside axes to reset.\n' \
                             'Dot shows the mean. Vertical dotted lines show STDs from mean'
    pylab.title(multiline_title_string)
    pylab.grid(True)  # Add a grid on to the figure window
    pylab.axis([-axis_x_range, axis_x_range, axis_y_lower_lim, axis_y_upper_lim])
    ### Because we are only looking at the x-axis mean and std,
    ### we will only show tick-labels on the x-axis
    pylab.xticks( scipy.arange(-axis_x_range,axis_x_range,2) )
    pylab.yticks([0])

    
# This is the function which gets called when the mouse is clicked in the figure window
def do_this_when_the_mouse_is_clicked(this_event):
    global coords_array 
    global point_handles_array
    x = this_event.xdata
    y = this_event.ydata
    ### If the click is outside the range, then clear figure and points list
    if this_event.xdata is None: # This means we clicked outside the axis
        clear_the_figure_and_empty_points_list()
    else: # We clicked inside the axis
        number_of_points = scipy.shape(coords_array)[0]
        if number_of_points > 0:
            point_to_be_deleted = check_if_click_is_on_an_existing_point(x,y)  
            if point_to_be_deleted != -1: # We delete a point
                # We will delete that row from coords_array. The rows are axis 0
                coords_array = scipy.delete(coords_array,point_to_be_deleted,0)
                # We will also hide that point on the figure, by finding its handle
                handle_of_point_to_be_deleted = point_handles_array[point_to_be_deleted]
                pylab.setp(handle_of_point_to_be_deleted,visible=False)
                # Now that we have erased the point with that handle,
                # we can delete that handle from the handles list
                point_handles_array = scipy.delete(point_handles_array,point_to_be_deleted)
            else:  # We make a new point
                coords_array = scipy.vstack((coords_array,[x,y]))
                this_point_num = scipy.shape(coords_array)[0]
                new_point_handle = pylab.plot(x,y,'*',color='blue')
                point_handles_array = scipy.append(point_handles_array,new_point_handle) 
        if number_of_points == 0:
            coords_array = scipy.array([[x,y]])
            this_point_num = scipy.shape(coords_array)[0]
            new_point_handle = pylab.plot(x,y,'*',color='blue')
            point_handles_array = scipy.append(point_handles_array,new_point_handle)
        ### Now plot the statistics that this program is demonstrating
        number_of_points = scipy.shape(coords_array)[0] # Recount how many points we have now
        if number_of_points > 1: 
            plot_the_mean_std_and_normal()
        ### Finally, check to see whether we have fewer than two points
        ### as a result of any possible point-deletions above.
        ### If we do, then delete the stats info from the plot, 
        ### as it isn't meaningful for just one data point
        number_of_points = scipy.shape(coords_array)[0]  
        if number_of_points < 2: # We only show mean and std if there are two or more points
            pylab.setp(handle_of_normal_curve_plot,visible=False)
            pylab.setp(handle_of_mean_plot,visible=False)
            pylab.setp(handle_of_std_lines,visible=False)        
            pylab.xlabel('')
        # Set the axis back to its original value, in case Python has changed it during plotting
        pylab.axis([-axis_x_range, axis_x_range, axis_y_lower_lim, axis_y_upper_lim])


# This is the function which calculates and plots the statistics
def plot_the_mean_std_and_normal():
    # First, delete any existing normal-curve and mean plots from the figure
    global handle_of_normal_curve_plot
    global handle_of_mean_plot
    global handle_of_std_lines
    pylab.setp(handle_of_normal_curve_plot,visible=False)
    pylab.setp(handle_of_mean_plot,visible=False)
    pylab.setp(handle_of_std_lines,visible=False)    
    #### Next, calculate and plot the stats
    x_coords =  coords_array[:,0]  ### x-coords are the first column, which is 0 in Python
    x_mean = scipy.average(x_coords)
    x_std = scipy.std(x_coords)
    handle_of_mean_plot = pylab.plot(x_mean,0,'ro',markersize=8)
    x_range_to_plot = scipy.linspace(-axis_x_range,axis_x_range,100) # Specify a range of curve-positions to plot
    normal_curve = 1/(x_std*scipy.sqrt(2*scipy.pi)) * scipy.exp(
                         -(x_range_to_plot-x_mean)**2  / (2 * x_std**2) )
    ### If we want, we can cross-check this against the scipy function norm.pdf
    #normal_curve_from_scipy = scipy.stats.norm.pdf(x_range_to_plot,x_mean,x_std)
    handle_of_normal_curve_plot = pylab.plot(x_range_to_plot,normal_curve,'r-')
    ### Now add on lines showing the standard deviations
    std_to_show = scipy.linspace(-3,3,7)  
    std_x_values = x_mean + std_to_show*x_std
    std_normal_curve_values = scipy.stats.norm.pdf(std_x_values,x_mean,x_std)
    # In order to plot these std lines all at once,
    # we will make arrays with the first row as the starting points
    # and the second row as the end points
    std_lines_x_array = scipy.vstack((std_x_values,std_x_values))
    std_lines_y_array = scipy.vstack((scipy.zeros((1,7)),std_normal_curve_values))
    handle_of_std_lines = pylab.plot(std_lines_x_array,std_lines_y_array,'r--')
    # Now display the n, mean and STD info
    number_of_points = scipy.shape(coords_array)[0] # Recount how many points we have now
    pylab.xlabel('n = ' + str(number_of_points) +
          '   Mean = ' + str(round(x_mean,2)) +  # The ',2' means show 2 decimal places
          ',  STD = '  + str(round(x_std,2)) )
    # Set the axis back to its original value, in case Python has changed it during plotting
    pylab.axis([-axis_x_range, axis_x_range, axis_y_lower_lim, axis_y_upper_lim])

        
# This is the function which deletes existing points if you click on them       
def check_if_click_is_on_an_existing_point(mouse_x_coord,mouse_y_coord):
    # First, figure out how many points we have.
    # Each point is one row in the coords_array,
    # so we count the number of rows, which is dimension-0 for Python
    number_of_points = scipy.shape(coords_array)[0]    
    this_coord = scipy.array([[ mouse_x_coord, mouse_y_coord ]]) 
            # The double square brackets above give the this_coord array 
            # an explicit structure of having rows and also columns
    if number_of_points > 0:  
        # If there are some points, we want to calculate the distance
        # of the new mouse-click location from every existing point.
        # One way to do this is to make an array which is the same size
        # as coords_array, and which contains the mouse x,y-coords on every row.
        # Then we can subtract that xy_coord_matchng_matrix from coords_array
        ones_vec = scipy.ones((number_of_points,1))
        xy_coord_matching_matrix = scipy.dot(ones_vec,this_coord)
        distances_from_existing_points = (coords_array - xy_coord_matching_matrix)
        # Because the x and y axes have different scales,
        # we need to rescale the distances so that itdoesn't matter whether
        # you try to delete a dot by clicking near it in the x or y directions.
        # When we extract the columns of distances_from_existing_points,
        # scipy returns the values as row vectors for some reason.
        # So, we transpose them back to column vectors and stack them horizontally
        axis_range_scaled_distances = scipy.hstack(
            ( distances_from_existing_points[:,0].reshape(-1,1)/(2*axis_x_range),
              distances_from_existing_points[:,1].reshape(-1,1)/(axis_y_upper_lim-axis_y_lower_lim) ) )
        squared_distances_from_existing_points = axis_range_scaled_distances**2
        sum_sq_dists = scipy.sum(squared_distances_from_existing_points,axis=1) 
                   # The axis=1 means "sum over dimension 1", which is columns for Python          
        euclidean_dists = scipy.sqrt(sum_sq_dists)
        distance_threshold = 0.01
        within_threshold_points = scipy.nonzero(euclidean_dists < distance_threshold )
        num_within_threshold_points = scipy.shape(within_threshold_points)[1]
        if num_within_threshold_points > 0:
            # We only want one matching point.
            # It's possible that more than one might be within threshold.
            # So, we take the unique smallest distance
            point_to_be_deleted = scipy.argmin(euclidean_dists)
            return point_to_be_deleted
        else: # If there are zero points, then we are not deleting any 
            point_to_be_deleted = -1
            return point_to_be_deleted

if __name__ == '__main__':
    #######################################################################
    # This is the main part of the program, which calls the above functions
    #######################################################################
    # First, initialise some of our variables to be empty
    coords_array = scipy.array([])
    point_handles_array = scipy.array([])
    handle_of_normal_curve_plot = []
    handle_of_mean_plot = []
    handle_of_std_lines = []
    ### Set up an initial space to click inside
    axis_x_range = 10
    axis_y_upper_lim = 0.2
    axis_y_lower_lim = -0.07
    ### Make the figure window
    pylab.figure()
    ### Clear the figure window
    pylab.clf() # clf means "clear the figure"
    ### In order to keep the boundaries of the figure fixed in place,
    ### we will draw a black box around the region that we want.
    pylab.plot(axis_x_range*scipy.array([-1, 1, 1, -1]),
               scipy.array([axis_y_lower_lim,axis_y_lower_lim,axis_y_upper_lim,axis_y_upper_lim]),'k-')
    ### Tell Python to call a function every time
    ### when the mouse is pressed in this figure
    pylab.connect('button_press_event', do_this_when_the_mouse_is_clicked)

    clear_the_figure_and_empty_points_list()
    pylab.show()    # This shows the figure window onscreen
