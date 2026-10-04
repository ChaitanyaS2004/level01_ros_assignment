"""Convenience launch: optional simulation + map loader + localization + navigation.

The three stage launch files stay independent; this file only includes them, staggered in time
so each stage finds the previous one running.

  ros2 launch testbed_navigation testbed_nav_all.launch.py                         # sim already running
  ros2 launch testbed_navigation testbed_nav_all.launch.py sim:=true start_delay:=15
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression


def generate_launch_description():
    nav_launch = os.path.join(get_package_share_directory('testbed_navigation'), 'launch')
    sim_launch = os.path.join(get_package_share_directory('testbed_bringup'), 'launch',
                              'testbed_full_bringup.launch.py')

    use_sim_time = LaunchConfiguration('use_sim_time')
    start_delay = LaunchConfiguration('start_delay')

    nav2_params = os.path.join(
        get_package_share_directory('testbed_navigation'), 'config', 'nav2_params.yaml')

    def stage(file_name, **extra):
        args = {'use_sim_time': use_sim_time}
        args.update(extra)
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav_launch, file_name)),
            launch_arguments=args.items())

    def after(extra_seconds, action):
        return TimerAction(
            period=PythonExpression(['float(', start_delay, ') + ', str(extra_seconds)]),
            actions=[action])

    return LaunchDescription([
        DeclareLaunchArgument('sim', default_value='false',
                              description='Also start the Gazebo + RViz bringup'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('start_delay', default_value='0.0',
                              description='Seconds to wait before starting the stack '
                                          '(use ~15 together with sim:=true)'),

        IncludeLaunchDescription(PythonLaunchDescriptionSource(sim_launch),
                                 condition=IfCondition(LaunchConfiguration('sim'))),

        after(0.0, stage('map_loader.launch.py')),
        after(3.0, stage('localization.launch.py')),
        after(8.0, stage('navigation.launch.py', params_file=nav2_params)),
    ])
