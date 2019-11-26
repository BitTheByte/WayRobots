from multithreading import Threader
from colorama import Fore, init
from api import *
import argparse
import time
import re

lock = multithreading.threading.Lock()