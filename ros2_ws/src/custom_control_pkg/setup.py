from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'custom_control_pkg'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        # Register the package within the ROS 2 index
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        # Include package.xml so ROS 2 can discover dependencies
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='Custom PID, LQR, and Rate Control Bypassing Node for PX4 Integration',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'run_pid = custom_control_pkg.master_runner:main',
            'run_lqr = custom_control_pkg.master_runner:main',
            'run_bypass_test = custom_control_pkg.master_runner:main',
        ],
    },
)