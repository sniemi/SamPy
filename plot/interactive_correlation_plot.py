### Interactively plot points
### to show the correlation between the x and y directions.
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
### 1. Click to make a few points in more or less a straight line.
###    What is the correlation value? 
###    Now add a point far away from the line.
###    What does adding that point do to the correlation value?
###    Try deleting the point by clicking on it, then re-adding it, to compare.
### 2. Click outside the axes to reset the plot.
###    Now put in about 10 points in a oval-ish cloud,
###    deleting and adjusting them so that you get a correlation
###    of around r=0.6.
###    What is the size of the p-value associated with this correlation?
###    (This p-value is the probability of observing this r-value
###    if the population the points were sampled from actually had zero correlation).
###    Now add another 10 points, so that there are 20 in all,
###    while keeping the correlation value at r=0.6.
###    What is the p-value now?
### 3. Click outside the axes to reset the plot.
###    Now make in turn, approximately, each of the four plots 
###    shown in Anscombe's Quartet:
###    http://en.wikipedia.org/wiki/Anscombe's_quartet
###    What does this tell you how only knowing a correlation-value
###    might give you a misleading picture of the data?

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
    handle_of_regression_line_plot = []
    ### Clear the figure window
    pylab.clf()  # clf means "clear the figure"
    ### In order to keep the boundaries of the figure fixed in place,
    ### we will draw a white box around the region that we want.
    pylab.plot(axis_range*scipy.array([-1, 1, 1, -1]),
               axis_range*scipy.array([-1, -1, 1, 1]),'w-')
    ### We want a long title, so we put a \n in the middle, to start a new line of title-text      
    multiline_title_string = 'Click to add points, on old points to delete,' \
                             ' outside axes to reset.\n' \
                             ' The red line is the linear regression best-fit.'  
    pylab.title(multiline_title_string)
    pylab.grid(True)  # Add a grid on to the figure window
    pylab.axis('equal') # Make the tick-marks equally spaced on x- and y-axes
    pylab.axis(axis_range*scipy.array([-1, 1, -1, 1]))
    
    
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
                new_point_handle = pylab.plot(x,y,'*',color='blue')
                point_handles_array = scipy.append(point_handles_array,new_point_handle) 
        if number_of_points == 0:
            coords_array = scipy.array([[x,y]])
            new_point_handle = pylab.plot(x,y,'*',color='blue')
            point_handles_array = scipy.append(point_handles_array,new_point_handle)
        ### Now plot the statistics that this program is demonstrating
        number_of_points = scipy.shape(coords_array)[0] # Recount how many points we have now
        if number_of_points > 1: 
            plot_the_correlation()
        ### Finally, check to see whether we have fewer than two points
        ### as a result of any possible point-deletions above.
        ### If we do, then delete the stats info from the plot, 
        ### as it isn't meaningful for just one data point
        number_of_points = scipy.shape(coords_array)[0]  
        if number_of_points < 2: # We only show mean and std if there are two or more points
            pylab.setp(handle_of_regression_line_plot,visible=False)
            pylab.xlabel('')
            pylab.ylabel('')
        # Set the axis back to its original value, in case Python has changed it during plotting
        pylab.axis('equal') # Make the tick-marks equally spaced on x- and y-axes
        pylab.axis(axis_range*scipy.array([-1, 1, -1, 1]))
        
        
# This is the function which calculates and plots the statistics
def plot_the_correlation():
    # First, delete any existing regression line plots from the figure
    global handle_of_regression_line_plot
    pylab.setp(handle_of_regression_line_plot,visible=False)
    #### Next, calculate and plot the stats
    number_of_points = scipy.shape(coords_array)[0]  
    x_coords =  coords_array[:,0] # Python starts counting from zero
    y_coords =  coords_array[:,1] 
    #### To get the best-fit line, we'll do a regression
    slope, y_intercept, r_from_regression, p_from_regression, std_err = (
                          scipy.stats.linregress(x_coords,y_coords)     )
    #### Plot the best-fit line in red
    handle_of_regression_line_plot = pylab.plot(axis_range*scipy.array([-1,1]), 
                    y_intercept + slope*axis_range*scipy.array([-1,1]),'r-')
    #### Uncomment the next two lines if you want to verify
    #### that the stats we get from regression and from correlation are the same.
    # r_from_corr,p_from_corr = scipy.stats.pearsonr(x_coords,y_coords) 
    # print r_from_regression,r_from_corr,p_from_regression,p_from_corr 
    #### In order to make the p-values format nicely
    #### even when they have a bunch of zeros at the start, we do this:
    p_value_string = "%1.2g" % p_from_regression 
    pylab.xlabel(str(number_of_points) + ' points: ' +
                '  p-value of corr = ' + p_value_string +
                '  Correlation, r = ' + str(round(r_from_regression,2)) ) 
                                    # The ',2' means show 2 decimal places
    # Set the axis back to its original value, in case Python has changed it during plotting
    pylab.axis('equal') # Make the tick-marks equally spaced on x- and y-axes
    pylab.axis(axis_range*scipy.array([-1, 1, -1, 1]))
        
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
        squared_distances_from_existing_points = distances_from_existing_points**2
        sum_sq_dists = scipy.sum(squared_distances_from_existing_points,axis=1) 
                   # The axis=1 means "sum over dimension 1", which is columns for Python          
        euclidean_dists = scipy.sqrt(sum_sq_dists)
        distance_threshold = 0.5
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
    handle_of_regression_line_plot = []
    ### Set up an initial space to click inside
    axis_range = 10
    ### Make the figure window
    pylab.figure()
    ### Clear the figure window
    pylab.clf() # clf means "clear the figure"
    ### In order to keep the boundaries of the figure fixed in place,
    ### we will draw a white box around the region that we want.
    pylab.plot(axis_range*scipy.array([-1, 1, 1, -1]),
               axis_range*scipy.array([-1, -1, 1, 1]),'w-')
    pylab.axis('equal')  # Make the tick-marks equally spaced on x- and y-axes
    pylab.axis(axis_range*scipy.array([-1, 1, -1, 1]))
    ### Python issues a warning when we try to calculate
    ### the correlation when there are just two points,
    ### as the p-value is zero. This next line hides that warning
    scipy.seterr(invalid="ignore")
    ### Tell Python to call a function every time
    ### when the mouse is pressed in this figure
    pylab.connect('button_press_event', do_this_when_the_mouse_is_clicked)

    clear_the_figure_and_empty_points_list()
    pylab.show()    # This shows the figure window onscreen

