# testbed_navigation

Map loading, AMCL localization and Nav2 navigation for the testbed robot (ROS 2 Humble, Gazebo Classic 11).
The Nav2 nodes are started individually from this package's own launch files; `nav2_bringup` is not launched or depended on.
I used `nav2_bringup` (Humble) as a reference, as suggested in `help.md`: `navigation.launch.py` is adapted from its
`navigation_launch.py`, and `nav2_params.yaml` starts from its default `nav2_params.yaml`, adjusted for this robot.


## Contents

### Launch files

| File | Nodes started | Notes |
|---|---|---|
| `launch/map_loader.launch.py` | `map_server`<br>`lifecycle_manager_map` | Loads `testbed_bringup/maps/testbed_world.yaml`. |
| `launch/localization.launch.py` | `amcl`<br>`lifecycle_manager_localization` | Publishes `map -> odom`. |
| `launch/navigation.launch.py` | controller, smoother, planner,<br>behavior server, BT navigator,<br>waypoint follower, velocity smoother<br>`lifecycle_manager_navigation` | Adapted from the Nav2 Humble navigation launch file. |
| `launch/testbed_nav_all.launch.py` | The three stage files above, in order | Convenience launcher. The stage files stay independent. |

### Configuration

| File | Purpose |
|---|---|
| `config/amcl_params.yaml` | AMCL parameters (initial pose = Gazebo spawn pose, x=0, y=5). |
| `config/nav2_params.yaml` | Nav2 parameters, kept close to the Nav2 Humble defaults. |
| `rviz/navigation.rviz` | RViz layout for navigation (Fixed Frame `map`, map, costmap, plan, scan). |

## Build

```bash
cd ~/assignment_ws
colcon build --symlink-install
source install/setup.bash
```

## Run

Terminal 1, simulation and RViz:

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

Terminal 2, the whole stack (map, then localization after 3 s, then navigation after 8 s):

```bash
ros2 launch testbed_navigation testbed_nav_all.launch.py
```

Or start each stage by hand, in this order, one terminal each:

```bash
ros2 launch testbed_navigation map_loader.launch.py
ros2 launch testbed_navigation localization.launch.py
ros2 launch testbed_navigation navigation.launch.py
```

Optionally open the navigation RViz layout: `rviz2 -d $(ros2 pkg prefix testbed_navigation)/share/testbed_navigation/rviz/navigation.rviz`.

Send a goal with the **2D Goal Pose** tool (Fixed Frame `map`, click on free floor and drag to set the heading). The `/map` display must use Durability **Transient Local**.

## Checks

```bash
for n in map_server amcl controller_server planner_server behavior_server bt_navigator smoother_server velocity_smoother waypoint_follower; do echo -n "$n: "; ros2 lifecycle get /$n; done   # all active
ros2 action list | grep navigate_to_pose
```

## Design choices

- Three stage launch files, each with its own lifecycle manager, so each stage can be started, restarted and checked on its own.
- Frames: `map -> odom` (AMCL) -> `base_footprint` (Gazebo diff-drive plugin). `base_link` is identical to `base_footprint` (identity joint), so the Nav2 default `base_link` frame works.
- Scan topic `/scan`; AMCL differential motion model and likelihood-field laser model.
- Controller: DWB local planner with the Nav2 default critics. Planner: NavFn. Costmaps: voxel/obstacle layer on `/scan`, inflation layer.
- Every node uses simulation time.

## Challenges and fixes

- **Starter code bugs** are listed in `BUGS.txt` at the repository root (lidar range and height, map yaml path, missing install directories, `use_sim_time`, and others).
- **Lidar scan flickering:** two lidar and two IMU sensors were defined on the same links (my own additions plus the starter ones), so `/scan` had two publishers. Keeping only the starter sensor fixed it.
- **Controller did not start ("No critics defined for FollowPath"):** the copied navigation launch file still pointed its default `params_file` at the old `params/` folder, so the controller ran on built-in defaults. The default now points at this package's `config/nav2_params.yaml`, and `testbed_nav_all.launch.py` also passes the file explicitly.
- **Map not shown in RViz:** the map is published once, so the RViz Map display needs Durability `Transient Local`, and the `map` frame only exists once AMCL runs.
