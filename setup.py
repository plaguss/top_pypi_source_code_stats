from setuptools import find_packages, setup

setup(
    name='src',
    packages=find_packages(),
    version='0.1.0',
    description="Python's source code statistics from top PyPI packages",
    author='Agustín',
    license='MIT',
    entry_points="""
       [console_scripts]
       make_dataset=src.data.make_dataset:make_dataset
   """,
)
