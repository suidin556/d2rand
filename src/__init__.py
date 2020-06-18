import os
import sys

SRC_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = getattr(sys, '_MEIPASS', os.path.join(SRC_ROOT, ".."))
