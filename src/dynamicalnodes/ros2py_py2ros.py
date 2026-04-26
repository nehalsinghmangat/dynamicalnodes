import numpy as np
from numpy.typing import NDArray
from typing import Any, Dict, List
import rclpy
from geometry_msgs.msg import (
    Vector3,
    Vector3Stamped,
    Quaternion,
    Pose,
    PoseStamped,
    PoseWithCovariance,
    PoseWithCovarianceStamped,
    Twist,
    TwistStamped,
    TwistWithCovariance,
    Wrench,
    Transform,
    TransformStamped,
    Accel,
    AccelStamped,
)

from turtlesim.msg import Pose
from nav_msgs.msg import Odometry, Path
from sensor_msgs.msg import (
    Imu,
    LaserScan,
    Image,
    CompressedImage,
    JointState,
)
from std_msgs.msg import Header, Float64, Float64MultiArray, Int32, Int32MultiArray, UInt8MultiArray
from builtin_interfaces.msg import Time


# ---------------------------------------------------------------------------
# Helper: covariance 36 <-> (6, 6)
# ---------------------------------------------------------------------------

def ros2py_covariance36(cov: List[float]) -> NDArray:
    """Flattened 36-element list -> (6, 6) ndarray."""
    arr = np.asarray(cov, dtype=float).ravel()
    if arr.size != 36:
        raise ValueError(f"Expected covariance length 36, got {arr.size}")
    return arr.reshape(6, 6)


def py2ros_covariance36(mat: NDArray) -> List[float]:
    """(6, 6) ndarray -> 36-element flat list."""
    arr = np.asarray(mat, dtype=float)
    if arr.shape != (6, 6):
        raise ValueError(f"Expected shape (6, 6), got {arr.shape}")
    return arr.ravel().tolist()


# ---------------------------------------------------------------------------
# builtin_interfaces/Time  <-> float seconds
# ---------------------------------------------------------------------------

def ros2py_time(t: Time) -> float:
    return float(t.sec) + float(t.nanosec) * 1e-9


def py2ros_time(t: float) -> Time:
    sec = int(np.floor(t))
    nsec = int(round((t - sec) * 1e9))
    if nsec >= 1_000_000_000:
        sec += 1
        nsec -= 1_000_000_000
    msg = Time()
    msg.sec = sec
    msg.nanosec = nsec
    return msg


# ---------------------------------------------------------------------------
# std_msgs/Header  <-> (time, frame_id)
# ---------------------------------------------------------------------------

def ros2py_header(h: Header) -> Dict[str, Any]:
    """Return {'t': float_seconds, 'frame_id': str}."""
    return {"t": ros2py_time(h.stamp), "frame_id": h.frame_id}


def py2ros_header(t: float, frame_id: str = "") -> Header:
    msg = Header()
    msg.stamp = py2ros_time(t)
    msg.frame_id = frame_id
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/Vector3  <->  np.ndarray(3,)
# ---------------------------------------------------------------------------

def ros2py_vector3(msg: Vector3) -> NDArray:
    return np.array([msg.x, msg.y, msg.z], dtype=float)


def py2ros_vector3(arr: NDArray) -> Vector3:
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 3:
        raise ValueError(f"py2ros_vector3 expected length 3, got {flat.size}")
    x, y, z = flat.tolist()
    msg = Vector3()
    msg.x = float(x)
    msg.y = float(y)
    msg.z = float(z)
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/Vector3Stamped  <->  np.ndarray(4,) [t, x, y, z]
# ---------------------------------------------------------------------------

def ros2py_vector3_stamped(msg: Vector3Stamped) -> NDArray:
    """Convert Vector3Stamped to [t, x, y, z]."""
    t = ros2py_time(msg.header.stamp)
    vec = ros2py_vector3(msg.vector)
    return np.concatenate(([t], vec))


def py2ros_vector3_stamped(arr: NDArray, *, frame_id: str = "") -> Vector3Stamped:
    """Convert [t, x, y, z] to Vector3Stamped."""
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 4:
        raise ValueError(f"py2ros_vector3_stamped expected length 4, got {flat.size}")

    msg = Vector3Stamped()
    msg.header = py2ros_header(float(flat[0]), frame_id)
    msg.vector = py2ros_vector3(flat[1:4])
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/Quaternion  <->  np.ndarray(4,)
# ---------------------------------------------------------------------------

def ros2py_quaternion(msg: Quaternion) -> NDArray:
    return np.array([msg.x, msg.y, msg.z, msg.w], dtype=float)


def py2ros_quaternion(arr: NDArray) -> Quaternion:
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 4:
        raise ValueError(f"py2ros_quaternion expected length 4, got {flat.size}")
    x, y, z, w = flat.tolist()
    msg = Quaternion()
    msg.x = float(x)
    msg.y = float(y)
    msg.z = float(z)
    msg.w = float(w)
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/Pose  <->  np.ndarray(7,)
# ---------------------------------------------------------------------------

def ros2py_pose(msg: Pose) -> NDArray:
    p = msg.position
    q = msg.orientation
    return np.array(
        [p.x, p.y, p.z, q.x, q.y, q.z, q.w],
        dtype=float,
    )


def py2ros_pose(arr: NDArray) -> Pose:
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 7:
        raise ValueError(f"py2ros_pose expected length 7, got {flat.size}")
    px, py, pz, qx, qy, qz, qw = flat.tolist()
    msg = Pose()
    msg.position.x = float(px)
    msg.position.y = float(py)
    msg.position.z = float(pz)
    msg.orientation.x = float(qx)
    msg.orientation.y = float(qy)
    msg.orientation.z = float(qz)
    msg.orientation.w = float(qw)
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/PoseStamped  <->  np.ndarray(8,)
# ---------------------------------------------------------------------------

def ros2py_pose_stamped(msg: PoseStamped) -> NDArray:
    """
    [t, pos.x, pos.y, pos.z, ori.x, ori.y, ori.z, ori.w]
    t in seconds.
    """
    t = ros2py_time(msg.header.stamp)
    pose_arr = ros2py_pose(msg.pose)
    return np.concatenate(([t], pose_arr))


def py2ros_pose_stamped(arr: NDArray, *, frame_id: str = "") -> PoseStamped:
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 8:
        raise ValueError(f"py2ros_pose_stamped expected length 8, got {flat.size}")
    t = float(flat[0])
    pose_vec = flat[1:]
    msg = PoseStamped()
    msg.header = py2ros_header(t, frame_id=frame_id)
    msg.pose = py2ros_pose(pose_vec)
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/PoseWithCovariance  <->  (7, (6,6))
# ---------------------------------------------------------------------------

def ros2py_pose_with_covariance(msg: PoseWithCovariance) -> Dict[str, Any]:
    """
    Returns dict with:
      'pose': ndarray(7,)
      'cov': ndarray(6,6)
    """
    pose_vec = ros2py_pose(msg.pose)
    cov = ros2py_covariance36(msg.covariance)
    return {"pose": pose_vec, "cov": cov}


def py2ros_pose_with_covariance(pose: NDArray, cov: NDArray) -> PoseWithCovariance:
    msg = PoseWithCovariance()
    msg.pose = py2ros_pose(pose)
    msg.covariance = py2ros_covariance36(cov)
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/PoseWithCovarianceStamped  <->  dict
# ---------------------------------------------------------------------------

def ros2py_pose_with_covariance_stamped(
    msg: PoseWithCovarianceStamped,
) -> Dict[str, Any]:
    """
    Returns dict:
      't': float seconds
      'frame_id': str
      'pose': ndarray(7,)
      'cov': ndarray(6,6)
    """
    t = ros2py_time(msg.header.stamp)
    frame_id = msg.header.frame_id
    inner = ros2py_pose_with_covariance(msg.pose)
    return {
        "t": t,
        "frame_id": frame_id,
        "pose": inner["pose"],
        "cov": inner["cov"],
    }


def py2ros_pose_with_covariance_stamped(
    t: float,
    frame_id: str,
    pose: NDArray,
    cov: NDArray,
) -> PoseWithCovarianceStamped:
    msg = PoseWithCovarianceStamped()
    msg.header = py2ros_header(t, frame_id=frame_id)
    msg.pose = py2ros_pose_with_covariance(pose, cov)
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/Twist  <->  np.ndarray(6,)
# ---------------------------------------------------------------------------

def ros2py_twist(msg: Twist) -> NDArray:
    """
    [linear.x, linear.y, linear.z,
     angular.x, angular.y, angular.z]
    """
    return np.array(
        [
            msg.linear.x,
            msg.linear.y,
            msg.linear.z,
            msg.angular.x,
            msg.angular.y,
            msg.angular.z,
        ],
        dtype=float,
    )


def py2ros_twist(arr: NDArray) -> Twist:
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 6:
        raise ValueError(f"py2ros_twist expected length 6, got {flat.size}")
    lx, ly, lz, ax, ay, az = flat.tolist()
    msg = Twist()
    msg.linear.x = float(lx)
    msg.linear.y = float(ly)
    msg.linear.z = float(lz)
    msg.angular.x = float(ax)
    msg.angular.y = float(ay)
    msg.angular.z = float(az)
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/TwistStamped  <->  np.ndarray(7,)
# ---------------------------------------------------------------------------

def ros2py_twist_stamped(msg: TwistStamped) -> NDArray:
    """
    [t, linear.x, linear.y, linear.z,
        angular.x, angular.y, angular.z]
    """
    t = ros2py_time(msg.header.stamp)
    twist_vec = ros2py_twist(msg.twist)
    return np.concatenate(([t], twist_vec))


def py2ros_twist_stamped(arr: NDArray, *, frame_id: str = "") -> TwistStamped:
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 7:
        raise ValueError(f"py2ros_twist_stamped expected length 7, got {flat.size}")
    t = float(flat[0])
    twist_vec = flat[1:]
    msg = TwistStamped()
    msg.header = py2ros_header(t, frame_id=frame_id)
    msg.twist = py2ros_twist(twist_vec)
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/TwistWithCovariance  <->  (6, (6,6))
# ---------------------------------------------------------------------------

def ros2py_twist_with_covariance(msg: TwistWithCovariance) -> Dict[str, Any]:
    twist_vec = ros2py_twist(msg.twist)
    cov = ros2py_covariance36(msg.covariance)
    return {"twist": twist_vec, "cov": cov}


def py2ros_twist_with_covariance(twist: NDArray, cov: NDArray) -> TwistWithCovariance:
    msg = TwistWithCovariance()
    msg.twist = py2ros_twist(twist)
    msg.covariance = py2ros_covariance36(cov)
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/Wrench  <->  np.ndarray(6,)
# ---------------------------------------------------------------------------

def ros2py_wrench(msg: Wrench) -> NDArray:
    """
    [force.x, force.y, force.z,
     torque.x, torque.y, torque.z]
    """
    return np.array(
        [
            msg.force.x,
            msg.force.y,
            msg.force.z,
            msg.torque.x,
            msg.torque.y,
            msg.torque.z,
        ],
        dtype=float,
    )


def py2ros_wrench(arr: NDArray) -> Wrench:
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 6:
        raise ValueError(f"py2ros_wrench expected length 6, got {flat.size}")
    fx, fy, fz, tx, ty, tz = flat.tolist()
    msg = Wrench()
    msg.force.x = float(fx)
    msg.force.y = float(fy)
    msg.force.z = float(fz)
    msg.torque.x = float(tx)
    msg.torque.y = float(ty)
    msg.torque.z = float(tz)
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/Transform  <->  np.ndarray(7,)
# ---------------------------------------------------------------------------

def ros2py_transform(msg: Transform) -> NDArray:
    """
    [translation.x, translation.y, translation.z,
     rotation.x, rotation.y, rotation.z, rotation.w]
    """
    t = msg.translation
    q = msg.rotation
    return np.array(
        [t.x, t.y, t.z, q.x, q.y, q.z, q.w],
        dtype=float,
    )


def py2ros_transform(arr: NDArray) -> Transform:
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 7:
        raise ValueError(f"py2ros_transform expected length 7, got {flat.size}")
    tx, ty, tz, qx, qy, qz, qw = flat.tolist()
    msg = Transform()
    msg.translation.x = float(tx)
    msg.translation.y = float(ty)
    msg.translation.z = float(tz)
    msg.rotation.x = float(qx)
    msg.rotation.y = float(qy)
    msg.rotation.z = float(qz)
    msg.rotation.w = float(qw)
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/TransformStamped  <->  np.ndarray(8,)
# ---------------------------------------------------------------------------

def ros2py_transform_stamped(msg: TransformStamped) -> NDArray:
    """
    [t, tx, ty, tz, qx, qy, qz, qw]
    """
    t = ros2py_time(msg.header.stamp)
    tr = ros2py_transform(msg.transform)
    return np.concatenate(([t], tr))


def py2ros_transform_stamped(
    arr: NDArray,
    *,
    frame_id: str = "",
    child_frame_id: str = "",
) -> TransformStamped:
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 8:
        raise ValueError(f"py2ros_transform_stamped expected length 8, got {flat.size}")
    t = float(flat[0])
    tr_vec = flat[1:]
    msg = TransformStamped()
    msg.header = py2ros_header(t, frame_id=frame_id)
    msg.child_frame_id = child_frame_id
    msg.transform = py2ros_transform(tr_vec)
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/Accel  <->  np.ndarray(6,)
# ---------------------------------------------------------------------------

def ros2py_accel(msg: Accel) -> NDArray:
    """
    [linear.x, linear.y, linear.z,
     angular.x, angular.y, angular.z]
    """
    return np.array(
        [
            msg.linear.x,
            msg.linear.y,
            msg.linear.z,
            msg.angular.x,
            msg.angular.y,
            msg.angular.z,
        ],
        dtype=float,
    )


def py2ros_accel(arr: NDArray) -> Accel:
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 6:
        raise ValueError(f"py2ros_accel expected length 6, got {flat.size}")
    lx, ly, lz, ax, ay, az = flat.tolist()
    msg = Accel()
    msg.linear.x = float(lx)
    msg.linear.y = float(ly)
    msg.linear.z = float(lz)
    msg.angular.x = float(ax)
    msg.angular.y = float(ay)
    msg.angular.z = float(az)
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/AccelStamped  <->  np.ndarray(7,)
# ---------------------------------------------------------------------------

def ros2py_accel_stamped(msg: AccelStamped) -> NDArray:
    """
    [t, linear.x, linear.y, linear.z,
        angular.x, angular.y, angular.z]
    """
    t = ros2py_time(msg.header.stamp)
    acc_vec = ros2py_accel(msg.accel)
    return np.concatenate(([t], acc_vec))


def py2ros_accel_stamped(arr: NDArray, *, frame_id: str = "") -> AccelStamped:
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 7:
        raise ValueError(f"py2ros_accel_stamped expected length 7, got {flat.size}")
    t = float(flat[0])
    acc_vec = flat[1:]
    msg = AccelStamped()
    msg.header = py2ros_header(t, frame_id=frame_id)
    msg.accel = py2ros_accel(acc_vec)
    return msg


# ---------------------------------------------------------------------------
# sensor_msgs/Imu  <->  np.ndarray(10,)
# (orientation, angular_velocity, linear_acceleration; ignores covariances)
# ---------------------------------------------------------------------------

def ros2py_imu(msg: Imu) -> NDArray:
    """
    [ori.x, ori.y, ori.z, ori.w,
     gyro.x, gyro.y, gyro.z,
     acc.x, acc.y, acc.z]
    """
    return np.array(
        [
            msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w,
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z,
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z,
        ],
        dtype=float,
    )


def py2ros_imu(arr: NDArray) -> Imu:
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 10:
        raise ValueError(f"py2ros_imu expected length 10, got {flat.size}")
    ox, oy, oz, ow, wx, wy, wz, ax, ay, az = flat.tolist()
    msg = Imu()
    msg.orientation.x = float(ox)
    msg.orientation.y = float(oy)
    msg.orientation.z = float(oz)
    msg.orientation.w = float(ow)
    msg.angular_velocity.x = float(wx)
    msg.angular_velocity.y = float(wy)
    msg.angular_velocity.z = float(wz)
    msg.linear_acceleration.x = float(ax)
    msg.linear_acceleration.y = float(ay)
    msg.linear_acceleration.z = float(az)
    return msg


# ---------------------------------------------------------------------------
# nav_msgs/Odometry  <->  np.ndarray(13,)
# (pose + twist; covariances ignored)
# ---------------------------------------------------------------------------

def ros2py_odometry(msg: Odometry) -> NDArray:
    """
    [pos.x, pos.y, pos.z,
     ori.x, ori.y, ori.z, ori.w,
     lin_vel.x, lin_vel.y, lin_vel.z,
     ang_vel.x, ang_vel.y, ang_vel.z]
    """
    p = msg.pose.pose.position
    q = msg.pose.pose.orientation
    v = msg.twist.twist.linear
    w = msg.twist.twist.angular
    return np.array(
        [
            p.x, p.y, p.z,
            q.x, q.y, q.z, q.w,
            v.x, v.y, v.z,
            w.x, w.y, w.z,
        ],
        dtype=float,
    )


def py2ros_odometry(arr: NDArray, *, frame_id: str = "", child_frame_id: str = "") -> Odometry:
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 13:
        raise ValueError(f"py2ros_odometry expected length 13, got {flat.size}")
    px, py, pz, qx, qy, qz, qw, vx, vy, vz, wx, wy, wz = flat.tolist()
    msg = Odometry()
    msg.header.frame_id = frame_id
    msg.child_frame_id = child_frame_id

    msg.pose.pose.position.x = float(px)
    msg.pose.pose.position.y = float(py)
    msg.pose.pose.position.z = float(pz)

    msg.pose.pose.orientation.x = float(qx)
    msg.pose.pose.orientation.y = float(qy)
    msg.pose.pose.orientation.z = float(qz)
    msg.pose.pose.orientation.w = float(qw)

    msg.twist.twist.linear.x = float(vx)
    msg.twist.twist.linear.y = float(vy)
    msg.twist.twist.linear.z = float(vz)

    msg.twist.twist.angular.x = float(wx)
    msg.twist.twist.angular.y = float(wy)
    msg.twist.twist.angular.z = float(wz)

    return msg


# ---------------------------------------------------------------------------
# nav_msgs/Path  <->  np.ndarray(N, 8)
# (sequence of PoseStamped-like vectors)
# ---------------------------------------------------------------------------

def ros2py_path(msg: Path) -> NDArray:
    """
    Path -> (N, 8) array of PoseStamped vectors:
    [t, px, py, pz, qx, qy, qz, qw]
    """
    if not msg.poses:
        return np.zeros((0, 8), dtype=float)
    mats = [ros2py_pose_stamped(p) for p in msg.poses]
    return np.vstack(mats)


def py2ros_path(arr: NDArray, *, frame_id: str = "") -> Path:
    """
    arr: (N, 8) or (8,) -> Path (with poses' headers set individually)
    """
    a = np.asarray(arr, dtype=float)
    if a.ndim == 1:
        a = a[None, :]
    if a.shape[1] != 8:
        raise ValueError(f"py2ros_path expected shape (N, 8), got {a.shape}")
    msg = Path()
    msg.header.frame_id = frame_id
    msg.poses = [py2ros_pose_stamped(row, frame_id=frame_id) for row in a]
    return msg


# ---------------------------------------------------------------------------
# geometry_msgs/PoseArray  <->  np.ndarray(N, 7)
# ---------------------------------------------------------------------------

def ros2py_pose_array(msg) -> NDArray:
    """
    geometry_msgs/PoseArray -> (N, 7)
    (we don't import PoseArray to avoid version issues; pass concrete msg)
    """
    poses = msg.poses
    if not poses:
        return np.zeros((0, 7), dtype=float)
    mats = [ros2py_pose(p) for p in poses]
    return np.vstack(mats)


def py2ros_pose_array(arr: NDArray, pose_array_cls: Any, *, frame_id: str = "") -> Any:
    """
    np.ndarray(N, 7) -> PoseArray-like msg.

    pose_array_cls: the actual PoseArray class type to instantiate.
    """
    a = np.asarray(arr, dtype=float)
    if a.ndim == 1:
        a = a[None, :]
    if a.shape[1] != 7:
        raise ValueError(f"py2ros_pose_array expected shape (N, 7), got {a.shape}")
    msg = pose_array_cls()
    msg.header.frame_id = frame_id
    msg.poses = [py2ros_pose(row) for row in a]
    return msg


# ---------------------------------------------------------------------------
# sensor_msgs/JointState  <->  dict of arrays
# ---------------------------------------------------------------------------

def ros2py_joint_state(msg: JointState) -> Dict[str, NDArray]:
    """
    Returns dict with keys:
      'name'      -> np.array of dtype object (names)
      'position'  -> np.array
      'velocity'  -> np.array
      'effort'    -> np.array
    """
    return {
        "name": np.array(msg.name, dtype=object),
        "position": np.asarray(msg.position, dtype=float),
        "velocity": np.asarray(msg.velocity, dtype=float),
        "effort": np.asarray(msg.effort, dtype=float),
    }


def py2ros_joint_state(
    *,
    names: List[str],
    position: NDArray,
    velocity: NDArray = None,
    effort: NDArray = None,
) -> JointState:
    msg = JointState()
    msg.name = list(names)
    msg.position = np.asarray(position, dtype=float).tolist()
    if velocity is not None:
        msg.velocity = np.asarray(velocity, dtype=float).tolist()
    if effort is not None:
        msg.effort = np.asarray(effort, dtype=float).tolist()
    return msg


# ---------------------------------------------------------------------------
# sensor_msgs/LaserScan  <->  ranges ndarray + optional metadata
# ---------------------------------------------------------------------------

def ros2py_laserscan(msg: LaserScan) -> Dict[str, Any]:
    """
    Returns dict:
      'ranges'       -> np.ndarray(N,)
      'intensities'  -> np.ndarray(N,)
      'angle_min', 'angle_max', 'angle_increment', 'time_increment',
      'scan_time', 'range_min', 'range_max' -> floats
    """
    return {
        "ranges": np.asarray(msg.ranges, dtype=float),
        "intensities": np.asarray(msg.intensities, dtype=float),
        "angle_min": float(msg.angle_min),
        "angle_max": float(msg.angle_max),
        "angle_increment": float(msg.angle_increment),
        "time_increment": float(msg.time_increment),
        "scan_time": float(msg.scan_time),
        "range_min": float(msg.range_min),
        "range_max": float(msg.range_max),
    }


def py2ros_laserscan(
    ranges: NDArray,
    *,
    angle_min: float,
    angle_max: float,
    angle_increment: float,
    time_increment: float = 0.0,
    scan_time: float = 0.0,
    range_min: float = 0.0,
    range_max: float = 0.0,
    intensities: NDArray = None,
    frame_id: str = "",
    stamp: float = 0.0,
) -> LaserScan:
    msg = LaserScan()
    msg.header = py2ros_header(stamp, frame_id=frame_id)
    msg.angle_min = float(angle_min)
    msg.angle_max = float(angle_max)
    msg.angle_increment = float(angle_increment)
    msg.time_increment = float(time_increment)
    msg.scan_time = float(scan_time)
    msg.range_min = float(range_min)
    msg.range_max = float(range_max)
    r = np.asarray(ranges, dtype=float).ravel()
    msg.ranges = r.tolist()
    if intensities is not None:
        inten = np.asarray(intensities, dtype=float).ravel()
        if inten.size != r.size:
            raise ValueError("intensities and ranges must have same length")
        msg.intensities = inten.tolist()
    return msg


# ---------------------------------------------------------------------------
# sensor_msgs/Image  <->  np.ndarray(H, W, C)
# (simple encodings only)
# ---------------------------------------------------------------------------

def ros2py_image(msg: Image) -> NDArray:
    """
    Convert sensor_msgs/Image to ndarray(H, W, C).

    Supports common encodings like 'mono8', 'rgb8', 'bgr8'.
    """
    data = np.frombuffer(msg.data, dtype=np.uint8)
    if msg.encoding.lower() in ("mono8", "8uc1"):
        arr = data.reshape(msg.height, msg.width)
    elif msg.encoding.lower() in ("rgb8", "bgr8"):
        arr = data.reshape(msg.height, msg.width, 3)
    else:
        # Fallback: just flatten; caller must interpret
        arr = data
    return arr


def py2ros_image(
    arr: NDArray,
    *,
    encoding: str = "rgb8",
    frame_id: str = "",
    stamp: float = 0.0,
) -> Image:
    a = np.asarray(arr)
    msg = Image()
    msg.header = py2ros_header(stamp, frame_id=frame_id)
    msg.encoding = encoding
    msg.is_bigendian = 0

    if encoding.lower() in ("mono8", "8uc1"):
        if a.ndim == 2:
            h, w = a.shape
        elif a.ndim == 3 and a.shape[2] == 1:
            h, w, _ = a.shape
            a = a[:, :, 0]
        else:
            raise ValueError("mono8 image must be (H,W) or (H,W,1)")
        msg.height = h
        msg.width = w
        msg.step = w
        msg.data = a.astype(np.uint8).tobytes()

    elif encoding.lower() in ("rgb8", "bgr8"):
        if a.ndim != 3 or a.shape[2] != 3:
            raise ValueError("rgb8/bgr8 image must be (H,W,3)")
        h, w, _ = a.shape
        msg.height = h
        msg.width = w
        msg.step = w * 3
        msg.data = a.astype(np.uint8).tobytes()

    else:
        # Fallback: treat as 1D array of bytes
        flat = a.astype(np.uint8).ravel()
        msg.height = 1
        msg.width = flat.size
        msg.step = flat.size
        msg.data = flat.tobytes()

    return msg


# ---------------------------------------------------------------------------
# sensor_msgs/CompressedImage  <->  bytes
# ---------------------------------------------------------------------------

def ros2py_compressed_image(msg: CompressedImage) -> Dict[str, Any]:
    """
    Returns dict:
      'format': str
      'data': bytes
    """
    return {"format": msg.format, "data": bytes(msg.data)}


def py2ros_compressed_image(
    data: bytes,
    *,
    format: str = "jpeg",
    frame_id: str = "",
    stamp: float = 0.0,
) -> CompressedImage:
    msg = CompressedImage()
    msg.header = py2ros_header(stamp, frame_id=frame_id)
    msg.format = format
    msg.data = data
    return msg


# ---------------------------------------------------------------------------
# std_msgs/Float64MultiArray, Int32MultiArray, UInt8MultiArray  <->  ndarray
# (layout ignored)
# ---------------------------------------------------------------------------

def ros2py_float64_multiarray(msg: Float64MultiArray) -> NDArray:
    return np.asarray(msg.data, dtype=float)


def py2ros_float64_multiarray(arr: NDArray) -> Float64MultiArray:
    msg = Float64MultiArray()
    msg.data = np.asarray(arr, dtype=float).ravel().tolist()
    return msg


def ros2py_int32_multiarray(msg: Int32MultiArray) -> NDArray:
    return np.asarray(msg.data, dtype=np.int32)


def py2ros_int32_multiarray(arr: NDArray) -> Int32MultiArray:
    msg = Int32MultiArray()
    msg.data = np.asarray(arr, dtype=np.int32).ravel().tolist()
    return msg


def ros2py_uint8_multiarray(msg: UInt8MultiArray) -> NDArray:
    return np.asarray(msg.data, dtype=np.uint8)


def py2ros_uint8_multiarray(arr: NDArray) -> UInt8MultiArray:
    msg = UInt8MultiArray()
    msg.data = np.asarray(arr, dtype=np.uint8).ravel().tolist()
    return msg


# ---------------------------------------------------------------------------
# std_msgs/Float64  <->  scalar float (as 1D array)
# ---------------------------------------------------------------------------

def ros2py_float64(msg: Float64) -> NDArray:
    """Convert Float64 message to 1D numpy array with single element."""
    return np.array([msg.data], dtype=float)


def py2ros_float64(arr: NDArray) -> Float64:
    """Convert scalar or 1D array to Float64 message."""
    msg = Float64()
    arr = np.asarray(arr, dtype=float).ravel()
    msg.data = float(arr[0]) if arr.size > 0 else 0.0
    return msg


# ---------------------------------------------------------------------------
# std_msgs/Int32  <->  scalar int (as 1D array)
# ---------------------------------------------------------------------------

def ros2py_int32(msg: Int32) -> NDArray:
    """Convert Int32 message to 1D numpy array with single element."""
    return np.array([msg.data], dtype=np.int32)


def py2ros_int32(arr: NDArray) -> Int32:
    """Convert scalar or 1D array to Int32 message."""
    msg = Int32()
    arr = np.asarray(arr, dtype=np.int32).ravel()
    msg.data = int(arr[0]) if arr.size > 0 else 0
    return msg


def ros2py_pose(msg: Pose) -> np.ndarray:
    """
    Convert a ROS 2 turtlesim/Pose message into a NumPy array.

    turtlesim/Pose fields:
        float32 x
        float32 y
        float32 theta
        float32 linear_velocity
        float32 angular_velocity

    Returns
    -------
    np.ndarray of shape (3,)
        [x, y, theta]
    """
    return np.array(
        [msg.x, msg.y, msg.theta],
        dtype=float
    )

def py2ros_pose(x) -> Pose:
    """
    Convert [x, y, theta] into turtlesim/Pose.
    Accepts shapes (3,), (3,1), (1,3), or anything squeeze-able to >=3 elements.
    """
    arr = np.asarray(x, dtype=float).squeeze()

    # Handle common column/row vector cases
    if arr.ndim == 2 and 1 in arr.shape:
        arr = arr.reshape(-1)

    if arr.ndim != 1 or arr.size < 3:
        raise ValueError(
            f"pose_py2ros expected at least 3 elements for [x,y,theta]; "
            f"got shape {np.asarray(x).shape} after squeeze -> {arr.shape} (size={arr.size})."
        )

    msg = Pose()
    msg.x = float(arr[0])
    msg.y = float(arr[1])
    msg.theta = float(arr[2])
    msg.linear_velocity = 0.0
    msg.angular_velocity = 0.0
    return msg

# Map ROS msg type -> msg -> np.ndarray
ROS2PY_DEFAULT = {
    Pose:ros2py_pose,
    Twist: ros2py_twist,
    PoseStamped: ros2py_pose_stamped,
    TransformStamped: ros2py_transform_stamped,
    Wrench: ros2py_wrench,
    Accel: ros2py_accel,
    AccelStamped: ros2py_accel_stamped,
    Vector3Stamped: ros2py_vector3_stamped,
    Imu: ros2py_imu,
    Odometry: ros2py_odometry,
    Path: ros2py_path,
    JointState: ros2py_joint_state,
    LaserScan: ros2py_laserscan,
    Image: ros2py_image,
    CompressedImage: ros2py_compressed_image,
    Float64: ros2py_float64,
    Float64MultiArray: ros2py_float64_multiarray,
    Int32: ros2py_int32,
    Int32MultiArray: ros2py_int32_multiarray,
    UInt8MultiArray: ros2py_uint8_multiarray,
    # add more as needed
}

# Map ROS msg type -> (np.ndarray, **kwargs) -> msg
PY2ROS_DEFAULT = {
    Pose:py2ros_pose,
    Twist: py2ros_twist,
    PoseStamped: py2ros_pose_stamped,
    TransformStamped: py2ros_transform_stamped,
    Wrench: py2ros_wrench,
    Accel: py2ros_accel,
    AccelStamped: py2ros_accel_stamped,
    Vector3Stamped: py2ros_vector3_stamped,
    Imu: py2ros_imu,
    Odometry: py2ros_odometry,
    Path: py2ros_path,
    JointState: py2ros_joint_state,
    LaserScan: py2ros_laserscan,
    Image: py2ros_image,
    CompressedImage: py2ros_compressed_image,
    Float64: py2ros_float64,
    Float64MultiArray: py2ros_float64_multiarray,
    Int32: py2ros_int32,
    Int32MultiArray: py2ros_int32_multiarray,
    UInt8MultiArray: py2ros_uint8_multiarray,
    # add more as needed
}
