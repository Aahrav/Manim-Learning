from manim import *
import numpy as np

class CapsuleScene(Scene):
    def construct(self):
        # --- Create two circles (you had this) ---
        circle1 = Circle(radius=3, color=BLUE).shift(LEFT * 2)
        circle2 = Circle(radius=3, color=RED).shift(RIGHT * 2)

        c1 = circle1.get_center()
        c2 = circle2.get_center()
        r1 = circle1.radius
        r2 = circle2.radius

        # --- distance & intersection helper (guard against degenerate case) ---
        v = c2 - c1
        dist = np.linalg.norm(v)
        if dist == 0:
            # identical centers — nothing sensible to draw; bail out visually
            self.play(Create(circle1), Create(circle2))
            self.wait()
            return

        # Intersection formula (a, h) with numerical safety for floating errors
        a = (r1 ** 2 - r2 ** 2 + dist ** 2) / (2 * dist)
        h_sq = r1 ** 2 - a ** 2
        if h_sq < 0 and h_sq > -1e-8:
            h_sq = 0.0  # clamp tiny negative due to fp error
        if h_sq < 0:
            # No intersection (disjoint) — show circles and bail
            self.play(Create(circle1), Create(circle2))
            self.wait()
            return
        h = np.sqrt(h_sq)

        # Reference point along the center line between intersections
        x0 = c1[0] + a * (c2[0] - c1[0]) / dist
        y0 = c1[1] + a * (c2[1] - c1[1]) / dist

        # Perpendicular offset to get the two intersection points
        rx = -(c2[1] - c1[1]) * (h / dist)
        ry = (c2[0] - c1[0]) * (h / dist)

        p1 = np.array([x0 + rx, y0 + ry, 0.0])
        p2 = np.array([x0 - rx, y0 - ry, 0.0])

        # --- OUTWARD vectors: use center-line directions (not perpendicular) ---
        # For the left circle (circle1), outward points away from circle2: -(c2 - c1)
        outward_A = -(c2 - c1)
        # For the right circle (circle2), outward points away from circle1: (c2 - c1)
        outward_B = (c2 - c1)

        # Normalize outward vectors (not strictly required for dot-tests but clearer)
        def safe_normalize(u):
            n = np.linalg.norm(u)
            return u / n if n != 0 else u

        outward_A = safe_normalize(outward_A)
        outward_B = safe_normalize(outward_B)

        # --- Helper to build an Arc that goes from p_start -> p_end choosing the arc
        #     that faces outward_vec (keeps the outer/bulging arc) ---
        def get_arc_path(center, radius, p_start, p_end, outward_vec):
            v_start = p_start - center
            v_end = p_end - center

            ang_start = np.arctan2(v_start[1], v_start[0])
            ang_end = np.arctan2(v_end[1], v_end[0])

            # Normalize angles into [0, 2pi)
            def norm_pos(a):
                a = a % TAU
                if a < 0:
                    a += TAU
                return a

            ang_start = norm_pos(ang_start)
            ang_end = norm_pos(ang_end)

            # Compute CCW sweep from start -> end in [0, 2pi)
            sweep = ang_end - ang_start
            if sweep < 0:
                sweep += TAU

            # Mid-angle of that CCW arc
            mid_angle_ccw = ang_start + sweep / 2.0
            mid_angle_ccw = norm_pos(mid_angle_ccw)
            mid_pt_ccw = center + radius * np.array([np.cos(mid_angle_ccw), np.sin(mid_angle_ccw), 0.0])

            # If the CCW midpoint points roughly in the same direction as outward_vec,
            # keep the CCW sweep; otherwise choose the "other" arc (the long way / clockwise)
            if np.dot(mid_pt_ccw - center, outward_vec) > 0:
                final_sweep = sweep  # positive => CCW angle
            else:
                final_sweep = sweep - TAU  # negative => CW angle (long way)

            arc = Arc(
                radius=radius,
                arc_center=center,
                start_angle=ang_start,
                angle=final_sweep,
                num_components=60,  # smoother
            )
            return arc

        # Build arcs: A from p1 -> p2 on circle1, B from p2 -> p1 on circle2
        arc_A_obj = get_arc_path(c1, r1, p1, p2, outward_A)
        arc_B_obj = get_arc_path(c2, r2, p2, p1, outward_B)

        # --- Build the capsule VMobject by appending arc points ---
        capsule = VMobject()
        # Ensure exact snapping to intersection points to avoid tiny gaps
        pts_A = np.array(arc_A_obj.points)
        pts_B = np.array(arc_B_obj.points)

        # Force endpoints to exact intersection coords (snap)
        if pts_A.shape[0] > 0:
            pts_A[0] = p1
            pts_A[-1] = p2
        if pts_B.shape[0] > 0:
            pts_B[0] = p2
            pts_B[-1] = p1

        capsule.append_points(pts_A)
        capsule.append_points(pts_B)

        # Close the path explicitly (safety)
        capsule.close_path()

        capsule.set_stroke(color=YELLOW, width=6)
        capsule.set_fill(color=WHITE, opacity=0.5)

        # Dots and labels for intersections (visual debug)
        dot1 = Dot(point=p1, color=WHITE)
        dot2 = Dot(point=p2, color=WHITE)
        lbl1 = Text("P1", font_size=20).next_to(dot1, UP)
        lbl2 = Text("P2", font_size=20).next_to(dot2, DOWN)

        # Optional: arrows showing outward vectors (debug)
        arrow_A = Arrow(start=c1, end=c1 + outward_A, buff=0, stroke_width=3)
        arrow_B = Arrow(start=c2, end=c2 + outward_B, buff=0, stroke_width=3)

        # --- Play the animation ---
        self.play(Create(circle1), Create(circle2))
        self.wait(0.5)

        self.play(FadeIn(dot1, lbl1), FadeIn(dot2, lbl2))
        self.play(Create(arrow_A), Create(arrow_B))
        self.wait(0.3)

        # Draw & fill the capsule
        self.play(DrawBorderThenFill(capsule), run_time=3)
        self.wait(2)
