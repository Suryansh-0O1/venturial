import math

def normalize_winding(face_pts, sweep_vec):
    """Ensures the 4-point face is wound correctly relative to the sweep/extrusion vector.
    If the face normal points against the sweep direction, reverses the points in-place
    to prevent 'inside-out' hex errors in blockMesh.
    """
    if len(face_pts) != 4:
        return
        
    p0, p1, p2 = face_pts[0], face_pts[1], face_pts[2]
    
    v1 = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
    v2 = [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]]
    
    n = [
        v1[1]*v2[2] - v1[2]*v2[1],
        v1[2]*v2[0] - v1[0]*v2[2],
        v1[0]*v2[1] - v1[1]*v2[0]
    ]
    
    dot = n[0]*sweep_vec[0] + n[1]*sweep_vec[1] + n[2]*sweep_vec[2]
    
    # Degenerate check 1: Sweep vector is zero (e.g. revolve axis passes through sketch center)
    mag_s = (sweep_vec[0]**2 + sweep_vec[1]**2 + sweep_vec[2]**2)**0.5
    if mag_s < 1e-6:
        raise RuntimeError(
            "Degenerate geometry: The sweep vector is zero. For Revolution, this usually means "
            "the revolution axis passes exactly through the center of your sketch, resulting "
            "in a self-intersecting 0-volume block. Move the sketch away from the axis in Edit Mode."
        )

    # Degenerate check 2: Face normal is orthogonal to sweep (0 volume block)
    mag_n = (n[0]**2 + n[1]**2 + n[2]**2)**0.5
    if mag_n > 1e-6:
        if abs(dot) / (mag_n * mag_s) < 1e-4:
            raise RuntimeError(
                "Degenerate geometry detected. The sketch is exactly parallel to the sweep direction, "
                "which generates a 0-volume block (inside-out). For Revolution, ensure the sketch "
                "doesn't lie flat on the plane orthogonal to the revolution axis. For Extrusion, "
                "ensure the sketch isn't perfectly aligned with the extrusion vector."
            )
            
    if dot < 0:
        face_pts.reverse()

def compute_revolve_sweep(face_pts, origin, axis, angle_deg):
    """Computes the sweep vector for a revolution operation."""
    cx = sum(p[0] for p in face_pts) / 4.0
    cy = sum(p[1] for p in face_pts) / 4.0
    cz = sum(p[2] for p in face_pts) / 4.0
    
    dx = cx - origin[0]
    dy = cy - origin[1]
    dz = cz - origin[2]
    
    sweep = [
        axis[1]*dz - axis[2]*dy,
        axis[2]*dx - axis[0]*dz,
        axis[0]*dy - axis[1]*dx
    ]
    
    if angle_deg < 0:
        sweep = [-s for s in sweep]
        
    return sweep
