# General 
from pathlib import Path
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, List
from colorama import Fore, Style

# Helpers
from src.utils.io import read_json
from src.utils.io import write_json
from src.utils.pdf import extract_blocks_from_page

# Logging
import logging
logger = logging.getLogger(__name__)

class DocumentLoader(ABC):
    # Abstract base class for document loaders
    
    @abstractmethod
    def load_documents(self):
        pass