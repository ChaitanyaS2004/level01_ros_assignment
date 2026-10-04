"""AMCL localization (map -> odom). Needs map_loader.launch.py running."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    default_params = os.path.join(
        get_package_share_directory('testbed_navigation'), 'config', 'amcl_params.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('params_file', default_value=default_params),
        Node(package='nav2_amcl', executable='amcl', name='amcl', output='screen',
             parameters=[params_file, {'use_sim_time': use_sim_time}]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_localization', output='screen',
             parameters=[{'use_sim_time': use_sim_time, 'autostart': True,
                          'node_names': ['amcl']}]),
    ])
