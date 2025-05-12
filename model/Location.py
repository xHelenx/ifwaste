from __future__ import annotations
import logging
import os  # Delay import for type hints
import globals_config as globals_config 

class Location:
    def __init__(self,id:int, grid:Grid, logger_name:str) -> None: # type: ignore
        """Initializes a location (house or store)

        Args:
            id (int): identifier number of the location
            grid (Grid): grid that the location is set in
            logger_name (str): name of logger used for debugging
        """        
        self.id:int = id 
        self.grid: Grid  = grid # type: ignore
        self.logger: logging.Logger|None= self.setup_logger(logger_name)
        
    def get_coordinates(self) -> tuple[int, int]: 
        """Returns coordinates of the location

        Returns:
            tuple[int, int]: x and y coordinate of the location in the grid
        """        
        return self.grid.get_coordinates(self)
    
    def unregister_logger(self) -> None:  
        """Remove debugging logger from location
        """        
        if self.logger != None:
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
                handler.close()  # Close the handler to release any resources

    def setup_logger(self,logger_name:str) -> logging.Logger|None:
        """Setup logger if logging is activated (SIMULATION_DEBUG_LOG_ON)
        Args:
            logger_name (str): Name of logger (also file name of logger)

        Returns:
            logging.Logger|None: logger
        """        
        if globals_config.SIMULATION_DEBUG_LOG_ON:
                log_dir = "LOGS"
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)  # Create the directory if it doesn't exist

                logger = logging.getLogger(logger_name)
                logger.setLevel(logging.DEBUG)

                # Create a file handler
                handler = logging.FileHandler(f"{log_dir}/{logger_name}.log")
                handler.setLevel(logging.DEBUG)

                # Add handler to the logger
                logger.addHandler(handler)
                logger.setLevel(logging.DEBUG)

                return logger  