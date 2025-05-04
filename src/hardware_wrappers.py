from imports_and_constants import *

# Wrapper for MicroManager core
class CoreWrapper():
    def __init__(self):
        if Microscope:
            self.core_instance = Core() # Microscope
        else:
            pass # Detached

    def get_x_position(self):
        """ 
        Retrieves x position of stage from hardware.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Value of the x position of the stage.
        """

        if Microscope:
            return self.core_instance.get_x_position() # Microscope
        else:
            return 0 # Detached

    def get_y_position(self):
        """ 
        Retrieves y position of stage from hardware.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Value of the y position of the stage.
        """

        if Microscope:
            return self.core_instance.get_y_position() # Microscope
        else:
            return 0 # Detached

    def set_roi(self, x_start: int, y_start: int, x_size: int, y_size: int):
        """ 
        Interacts with micromanager to set the ROI of the camera. The x dimensions of ROI will 
        be from x_start to x_start + x_size and likewise with the y coordinates.

        Parameters
        ----------
        x_start: int
                 the x coordinate that the ROI should begin at
        y_start: int
                 the y coordinate that the ROI should begin at
        x_size: int
                 the size of the ROI in the x dimension after x_start
        y_size: int
                 the size of the ROI in the y dimension after y_start

        Returns
        -------
        None
        """
        
        if Microscope:
            self.core_instance.set_roi(x_start,y_start,x_size,y_size)
        else:
            pass

# Wrapper for LiveStreamManager
class LiveStreamWrapper():
    def __init__(self):
        if Microscope:
            self.livestream_instance = pycromanager.Studio().get_snap_live_manager() # Microscope
        else:
            pass # Detached

    def get_is_live_mode_on(self) -> bool:
        """ 
        Returns a boolean value indicating whether live mode is on in Micromanager.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            True if live stream mode is on.
        """
        
        if Microscope:
            return self.livestream_instance.get_is_live_mode_on() # Microscope
        else:
            return True # Detached

    def snap(self, display_img_bool: bool) -> np.ndarray:
        """ 
        Snaps an image from the micromanager livestream if livemode is on. 

        Parameters
        ----------
        display_img_bool: bool
            If set to true, will show recently captured image in Micromanager 
            video stream. Typically only set to true for debugging, not production.

        Returns
        -------
        numpy.ndarray
            2D numpy array of captured image.
        """

        if Microscope:
            return self.livestream_instance.snap(display_img_bool) # Microscope
        else:
            # return np.random.randint(0, 256, size=(2048, 2048), dtype=np.uint16) # Detached 1

            time.sleep(0.1) # Detached 2
            return np.load('hongruo.npy')

    def is_live_mode_on(self) -> bool:
        """ 
        Returns a boolean value indicating whether live mode is on in Micromanager.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            True if live stream mode is on.
        """

        if Microscope:
            return self.livestream_instance.is_live_mode_on()
        else:
            pass

    def set_live_mode_on(self, on_or_off: bool):
        """ 
        Enables or disabled Micromanager live mode. 

        Parameters
        ----------
        on_or_off: bool
            If set to true, Micromanager live mode is started. If false,
            live mode is stopped.

        Returns
        -------
        None
        """

        if Microscope:
            return self.livestream_instance.set_live_mode_on(on_or_off)
        else:
            pass

# Abstraction for stage interaction
class MoveStage():
    
    @staticmethod
    def drive_stage(x_vel:int, y_vel:int, prev_x_vel:int, prev_y_vel:int):
        """ 
        Stage begins to move with a velocity based on the given x and y velocity
        vectors. Must keep track of previous x and y velocities for the API to 
        stop the previous movement before beginning a new one!

        Parameters
        ----------
        x_vel: int
            X Velocity
        y_vel: int
            Y Velocity
        prev_x_vel: int
            Previous X Velocity
        prev_y_vel: int
            Previous X Velocity

        Returns
        -------
        None
        """

        if Microscope:
            my_module.lastResort(x_vel,y_vel,prev_x_vel,prev_y_vel) # Microscope
        else:
            pass # Detached

    @staticmethod
    def connectToMicroscope():
        """ 
        Interacts with API to connect to microscope.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        if Microscope:
            my_module.connectToMicroscope() # Microscope
        else:
            pass # Detached

    @staticmethod
    def runXYVectorialTransfer(x_dir: int, x_speed: int , y_dir: int, y_speed: int):
        """ 
        Will drive stage in a direction given a vector, only if stage starts from zero
        velocity. Advised to use drive_stage member function as it is safer to stop 
        previous movements first.

        Parameters
        ----------
        x_dir: int
            Direction of x movement. 0 for no movement, -1 for negative x-axis movement
            and 1 for positive x-axis movement.
        x_speed: int
            Interacts with microscope's X speed table. Please read Nikon Ti2 SDK for further 
            details.
        y_dir: int
            Direction of y movement. 0 for no movement, -1 for negative y-axis movement
            and 1 for positive y-axis movement.
        y_speed: int
            Interacts with microscope's Y speed table. Please read Nikon Ti2 SDK for further 
            details.

        Returns
        -------
        None
        """

        if Microscope:
            my_module.runXYVectorialTransfer(x_dir, x_speed, y_dir, y_speed) # Microscope
        else:
            pass # Detached

# Abstraction for receiving stage coordinates
class GetStageCoords():

    @staticmethod
    def get_x_coord(core_wrap: CoreWrapper):
        """ 
        Retrieves x position of stage from abstraction.

        Parameters
        ----------
        core_wrap: CoreWrapper
            Takes an instance of the wrapper of the Micromanager core.

        Returns
        -------
        int
            Value of the x position of the stage.
        """

        if Microscope:
            return core_wrap.get_x_position() # Microscope
        else:
            return 0 # Detached

    @staticmethod
    def get_y_coord(core_wrap: CoreWrapper):
        """ 
        Retrieves y position of stage from abstraction.

        Parameters
        ----------
        core_wrap: CoreWrapper
            Takes an instance of the wrapper of the Micromanager core.

        Returns
        -------
        int
            Value of the y position of the stage.
        """

        if Microscope:
            return core_wrap.get_y_position() # Microscope
        else:
            return 0 # Detached
        
# Abstraction for converting pixel coordinates to cartesian coordinates
class PixToCartCoords():

    @staticmethod
    def pixel_to_cartesian_coords(core_wrap: CoreWrapper, head_pixel_x:int, head_pixel_y:int,image_height:int,image_width:int) -> np.ndarray:
        """ 
        This function takes as input the coordinates of the tracking point within the image
        and then converts it to a cartesian coordinate of where the stage should be next.

        Parameters
        ----------
        core_wrap: CoreWrapper
            Takes an instance of the wrapper of the Micromanager core.
        head_pixel_x: int
            The x location of the pixel within the image where the tracking point lies.
        head_pixel_y: int
            The y location of the pixel within the image where the tracking point lies.
        image_height: int
            Height of the captured image.
        image_width: int
            Width of the captured image.

        Returns
        -------
        np.ndarray
            Returns a 1x2 numpy array of the form [cartesian_x_coord, cartesian_y_coord]
        """

        if Microscope:
            x_scaling_factor = 0.1 * (770 / 512)  # Microscope
            y_scaling_factor = 0.1 * (770 / 512)

            x_cur_pos = core_wrap.get_x_position()
            y_cur_pos = core_wrap.get_y_position()

            # Convert pixel coordinates to stage coordinates
            # Subtract y difference from y offset to account for different coordinate systems
            x_new_pos = (head_pixel_x - image_width / 2) * x_scaling_factor + x_cur_pos
            y_new_pos = (head_pixel_y - image_height / 2) * y_scaling_factor + y_cur_pos

            return [x_new_pos, y_new_pos]
        else:
            return [0,0] # Detached