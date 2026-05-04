from mypyc.build import mypycify
from setuptools import setup

setup(
    name="chess_engine_1",
    ext_modules=mypycify(["game.py", "move_generator.py", "config.py"]),
    version="1.0",
)
