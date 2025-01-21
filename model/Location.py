from __future__ import annotations
import logging
import os  # Delay import for type hints
import globals 

class Location:
    def __init__(self,id:int, grid:Grid, logger_name:str) -> None: # type: ignore
        self.id:int = id 
        self.grid: Grid  = grid # type: ignore
        self.logger: logging.Logger|None= self.setup_logger(logger_name)
        
    def get_coordinates(self) -> tuple[int, int]: 
        return self.grid.get_coordinates(self)
    
    def unregister_logger(self) -> None:  
        if self.logger != None:
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
                handler.close()  # Close the handler to release any resources

    def setup_logger(self,logger_name:str) -> logging.Logger|None:
        if globals.SIMULATION_DEBUG_LOG_ON:
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