import os
import re
import logging

class LayerQueueManager:
    """
    Manages the queue of layer files for multi-layer printing.
    Handles loading, sorting, and tracking of layer files.
    """
    
    def __init__(self):
        """Initialize the layer queue manager."""
        self.layer_files = []
        self.current_layer_index = -1
        self.total_layers = 0
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
    def load_from_folder(self, folder_path):
        valid_extensions = ['.emd']
        layer_file_tuples = []
        
        for file in os.listdir(folder_path):
            if any(file.lower().endswith(ext) for ext in valid_extensions):
                file_path = os.path.join(folder_path, file)
                
                # New regex pattern to match img_X.emd format
                img_match = re.search(r'img_(\d+)\.emd', file)
                
                if img_match:
                    # Extract layer number from img_X format
                    layer_num = int(img_match.group(1))
                    layer_file_tuples.append((layer_num, file_path))
                else:
                    # Fallback to modification time if no layer number found
                    mod_time = os.path.getmtime(file_path)
                    layer_file_tuples.append((mod_time, file_path))
        
        # Sort by the first element (layer number or modification time)
        layer_file_tuples.sort(key=lambda x: x[0])
        
        # Store just the file paths in order
        self.layer_files = [file_path for _, file_path in layer_file_tuples]
        self.total_layers = len(self.layer_files)
        self.current_layer_index = -1
        
        return self.layer_files
    
    def get_current_layer(self):
        """
        Get the current layer file.
        
        Returns:
            str: Path to the current layer file, or None if no current layer
        """
        if 0 <= self.current_layer_index < self.total_layers:
            return self.layer_files[self.current_layer_index]
        return None
    
    def get_next_layer(self):
        """
        Advance to the next layer and return its file path.
        
        Returns:
            str: Path to the next layer file, or None if no more layers
        """
        if self.current_layer_index + 1 < self.total_layers:
            self.current_layer_index += 1
            self.logger.info(f"Advancing to layer {self.current_layer_index + 1} of {self.total_layers}")
            return self.layer_files[self.current_layer_index]
        
        self.logger.info("No more layers available")
        return None
    
    def peek_next_layer(self):
        """
        Look at the next layer without advancing.
        
        Returns:
            str: Path to the next layer file, or None if no more layers
        """
        if self.current_layer_index + 1 < self.total_layers:
            return self.layer_files[self.current_layer_index + 1]
        return None
    
    def reset(self):
        """Reset to the beginning of the queue."""
        self.current_layer_index = -1
        self.logger.info("Layer queue reset")
    
    def set_current_layer_index(self, index):
        """
        Set the current layer index to a specific value.
        Useful for resuming from a saved state.
        
        Args:
            index (int): The index to set as current
        
        Returns:
            bool: True if successful, False otherwise
        """
        if 0 <= index < self.total_layers:
            self.current_layer_index = index
            self.logger.info(f"Current layer index set to {index}")
            return True
        
        self.logger.error(f"Invalid layer index: {index}")
        return False
    
    def progress_percentage(self):
        """
        Calculate the current progress as a percentage.
        
        Returns:
            int: Progress percentage (0-100)
        """
        if self.total_layers == 0:
            return 0
        
        if self.current_layer_index < 0:
            return 0
            
        return int((self.current_layer_index + 1) / self.total_layers * 100)

    def get_layer_count(self):
        """
        Get the total number of layers/files in the queue.
        
        Returns:
            int: The total number of layers
        """
        return self.total_layers    