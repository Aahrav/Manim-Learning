# Capsule Construction from Two Overlapping Circles: Complete Guide

## High-level Overview

This code constructs a mathematically correct capsule (pill) shape from two overlapping circles and animates it in Manim. It combines circle–circle intersection geometry with explicit curve construction and path closing.

- Two equal circles are placed side by side so they overlap.
- The two intersection points of these circles are computed analytically.
- For each circle, the **outer** arc between the two intersection points is chosen (the one bulging away from the other circle).
- These two arcs are stitched into a single closed path and styled as a capsule.
- Dots, labels, and arrows visualize the geometry and outward directions.

---

## Geometry Setup

### Circles and Basic Data

```python
circle1 = Circle(radius=3, color=BLUE).shift(LEFT * 2)
circle2 = Circle(radius=3, color=RED).shift(RIGHT * 2)

c1 = circle1.get_center()
c2 = circle2.get_center()
r1 = circle1.radius
r2 = circle2.radius
```

- `circle1` and `circle2` are unit Manim `Circle` mobjects with radius 3.
- They are shifted left/right by 2 units, so their centers are:
  - \(C_1 = c_1 = (-2, 0, 0)\)
  - \(C_2 = c_2 = (2, 0, 0)\) (for this exact shift)
- Radii: \(r_1 = r_2 = 3\).

This guarantees overlap because the center distance is \(4 < r_1 + r_2 = 6\).

### Distance and Degeneracy Checks

```python
v = c2 - c1
dist = np.linalg.norm(v)
if dist == 0:
    # identical centers — nothing sensible to draw; bail out visually
    self.play(Create(circle1), Create(circle2))
    self.wait()
    return
```

- `v` is the vector from circle 1's center to circle 2's center:
  \[
    \vec{v} = C_2 - C_1
  \]
- `dist` is its Euclidean norm:
  \[
    d = \| \vec{v} \| = \sqrt{(C_2.x - C_1.x)^2 + (C_2.y - C_1.y)^2 + (C_2.z - C_1.z)^2}
  \]
- If `dist == 0`, both circles have the same center, so the capsule construction is not meaningful; the code simply draws the circles and exits.

---

## Circle–Circle Intersection Math

The code now computes the intersection points of two circles:

- Circle 1: center \(C_1\), radius \(r_1\)
- Circle 2: center \(C_2\), radius \(r_2\)
- Distance between centers: \(d = \text{dist}\)

### Step 1: The Parameter \(a\)

```python
a = (r1 ** 2 - r2 ** 2 + dist ** 2) / (2 * dist)
```

This comes from solving the system:

\[
\begin{cases}
\|X - C_1\|^2 = r_1^2 \\
\|X - C_2\|^2 = r_2^2
\end{cases}
\]

Subtracting these equations yields a linear relation defining the line on which the intersection chord lies. On the line from \(C_1\) to \(C_2\), the point \(X\) where the chord's perpendicular passes satisfies:

\[
a = \frac{r_1^2 - r_2^2 + d^2}{2d}
\]

- Geometrically, \(a\) is the distance from \(C_1\) to the projection point \(X\) along the center line, where the chord perpendicular passes through.

### Step 2: The Height \(h\)

```python
h_sq = r1 ** 2 - a ** 2
if h_sq < 0 and h_sq > -1e-8:
    h_sq = 0.0  # clamp tiny negative due to fp error
if h_sq < 0:
    # No intersection (disjoint) — show circles and bail
    self.play(Create(circle1), Create(circle2))
    self.wait()
    return
h = np.sqrt(h_sq)
```

From the right triangle \(C_1 X P\), where \(P\) is an intersection point:

\[
\|C_1 P\|^2 = r_1^2 = a^2 + h^2
\Rightarrow h^2 = r_1^2 - a^2
\]

- \(h\) is the distance from the line joining centers (the segment \(C_1 C_2\)) to each intersection point.
- `h_sq` can become slightly negative due to floating-point errors in edge cases, so:
  - If it is a tiny negative (e.g. -1e-10), it is clamped to 0.
  - If it's genuinely negative, circles do not intersect; the code renders circles and exits.

### Step 3: Base Point \(X\) on the Line of Centers

```python
x0 = c1[0] + a * (c2[0] - c1[0]) / dist
y0 = c1[1] + a * (c2[1] - c1[1]) / dist
```

This moves from \(C_1\) towards \(C_2\) by a distance \(a\):

\[
X = C_1 + \frac{a}{d} (C_2 - C_1)
\]

So:
- \(X = (x_0, y_0, 0)\) lies on the line segment between the centers.
- This is the midpoint of the chord segment in the direction of the center line (before going perpendicular).

### Step 4: Perpendicular Offset to Get the Two Intersection Points

```python
rx = -(c2[1] - c1[1]) * (h / dist)
ry = (c2[0] - c1[0]) * (h / dist)

p1 = np.array([x0 + rx, y0 + ry, 0.0])
p2 = np.array([x0 - rx, y0 - ry, 0.0])
```

To get the intersection points, you move from \(X\) in the direction perpendicular to the center line:

- The center-line direction is:
  \[
  \vec{u} = \frac{C_2 - C_1}{d}
  \]
- A perpendicular 2D vector to \(\vec{u} = (u_x, u_y)\) is \((-u_y, u_x)\).

Here:
- `(c2[0] - c1[0]) / dist` and `(c2[1] - c1[1]) / dist` are \(u_x, u_y\).
- `rx, ry` is \(h\) times the perpendicular unit vector.

Thus:

\[
P_1 = X + h \cdot \frac{(C_2 - C_1)^\perp}{d}, \quad
P_2 = X - h \cdot \frac{(C_2 - C_1)^\perp}{d}
\]

These are the two circle intersection points.

---

## Choosing "Outer" Arcs

You want, for each circle, the outer arc between \(P_1\) and \(P_2\), i.e. the arc that bulges away from the other circle.

### Outward Direction Vectors

Instead of using a perpendicular to pick the side, this code uses the **center-line direction**:

```python
outward_A = -(c2 - c1)  # for circle1, outward is away from circle2
outward_B = (c2 - c1)   # for circle2, outward is away from circle1
```

- For circle 1:
  - Vector from circle 1 to circle 2 is \(C_2 - C_1\).
  - "Outward" from circle 2 is the opposite direction: \( -(C_2 - C_1)\).
- For circle 2:
  - "Outward" from circle 1 is \(C_2 - C_1\) itself.

These are then normalized:

```python
def safe_normalize(u):
    n = np.linalg.norm(u)
    return u / n if n != 0 else u

outward_A = safe_normalize(outward_A)
outward_B = safe_normalize(outward_B)
```

This gives unit vectors roughly pointing "away" from the other circle.

---

## Arc Selection Logic

The core idea:

- For a given circle, two points \(P_{\text{start}}\) and \(P_{\text{end}}\) define two possible arcs (short and long).
- The code computes the **counterclockwise (CCW)** arc from start to end and checks if its **midpoint direction** matches the desired outward direction.
- If the CCW midpoint is outward, keep that arc.
- Otherwise, use the complementary arc (clockwise, i.e. negative sweep).

### Function Signature

```python
def get_arc_path(center, radius, p_start, p_end, outward_vec):
```

Inputs:
- `center`: circle center \(C\)
- `radius`: radius \(r\)
- `p_start`, `p_end`: two points on the circle
- `outward_vec`: a vector indicating the "outer side"

### Step 1: Local Vectors and Angles

```python
v_start = p_start - center
v_end = p_end - center

ang_start = np.arctan2(v_start[1], v_start[0])
ang_end = np.arctan2(v_end[1], v_end[0])
```

- `v_start`, `v_end` are vectors from the center to each point.
- `ang_start`, `ang_end` are polar angles of these vectors in radians.

### Step 2: Normalize Angles into \([0, 2\pi)\)

```python
def norm_pos(a):
    a = a % TAU
    if a < 0:
        a += TAU
    return a

ang_start = norm_pos(ang_start)
ang_end = norm_pos(ang_end)
```

- Ensures both angles are in the standard full-turn range, which makes CCW sweep computation easier.

### Step 3: CCW Sweep from Start to End

```python
sweep = ang_end - ang_start
if sweep < 0:
    sweep += TAU
```

- `sweep` is the CCW angular difference from `ang_start` to `ang_end`.
- If negative, add \(2\pi\) to get a positive sweep angle in \([0, 2\pi)\).
- This represents the **short or long** CCW arc depending on the geometry.

### Step 4: Midpoint of That CCW Arc

```python
mid_angle_ccw = ang_start + sweep / 2.0
mid_angle_ccw = norm_pos(mid_angle_ccw)
mid_pt_ccw = center + radius * np.array([np.cos(mid_angle_ccw), np.sin(mid_angle_ccw), 0.0])
```

- The parametric midpoint along that arc has angle:
  \[
    \theta_{\text{mid}} = \theta_{\text{start}} + \frac{\text{sweep}}{2}
  \]
- Convert back to coordinates:
  \[
    M_{\text{ccw}} = C + r(\cos \theta_{\text{mid}}, \sin \theta_{\text{mid}}, 0)
  \]

This midpoint lies on the CCW arc between the two intersection points.

### Step 5: Alignment with Outward Vector

```python
if np.dot(mid_pt_ccw - center, outward_vec) > 0:
    final_sweep = sweep  # CCW is outward
else:
    final_sweep = sweep - TAU  # choose the complementary (CW) arc
```

- `mid_pt_ccw - center` is the direction vector of the midpoint from the circle's center.
- The dot product
  \[
    (M_{\text{ccw}} - C) \cdot \text{outward\_vec}
  \]
  measures how aligned that midpoint direction is with the outward direction.
- If the dot product is positive, the CCW arc "faces outward" → keep `sweep`.
- If negative, the outer arc is actually the complementary direction, so we use `sweep - TAU` (a negative angle) to sweep clockwise the long way around.

This is the core decision that picks "outer" vs "inner" arc.

### Step 6: Create the Manim Arc

```python
arc = Arc(
    radius=radius,
    arc_center=center,
    start_angle=ang_start,
    angle=final_sweep,
    num_components=60,  # smoother
)
return arc
```

- `Arc` is a parametric curve in Manim:
  - `arc_center`: the center \(C\).
  - `radius`: \(r\).
  - `start_angle`: \( \theta_{\text{start}}\).
  - `angle`: total sweep (positive for CCW, negative for CW).
- `num_components` controls sampling resolution for smoothness.

---

## Building the Capsule Path

Now the arcs for each circle are generated:

```python
arc_A_obj = get_arc_path(c1, r1, p1, p2, outward_A)  # circle1: P1 → P2
arc_B_obj = get_arc_path(c2, r2, p2, p1, outward_B)  # circle2: P2 → P1
```

- Arc A uses circle 1's center and radius, and goes from \(P_1\) to \(P_2\), with "away from circle 2" as outward.
- Arc B uses circle 2's center and radius, and goes from \(P_2\) to \(P_1\), with "away from circle 1" as outward.
- Together, they trace a loop \(P_1 \to P_2\) on circle 1, then \(P_2 \to P_1\) on circle 2.

### Stitching Arcs into One VMobject

```python
capsule = VMobject()
pts_A = np.array(arc_A_obj.points)
pts_B = np.array(arc_B_obj.points)

# Snap endpoints exactly to intersection points
if pts_A.shape[0] > 0:
    pts_A[0] = p1
    pts_A[-1] = p2
if pts_B.shape[0] > 0:
    pts_B[0] = p2
    pts_B[-1] = p1

capsule.append_points(pts_A)
capsule.append_points(pts_B)

capsule.close_path()
```

- `arc_A_obj.points` and `arc_B_obj.points` are the sampled points along each arc.
- To avoid tiny numerical gaps between arcs, endpoints are "snapped" to the exact intersection coordinates:
  - First point of A → \(P_1\).
  - Last point of A → \(P_2\).
  - First point of B → \(P_2\).
  - Last point of B → \(P_1\).
- `append_points` concatenates the sampled points into a single path:
  - Path goes: \(P_1 \to \dots \to P_2\) (Arc A), then \(P_2 \to \dots \to P_1\) (Arc B).
- `close_path()` explicitly closes the loop, ensuring the object is a closed shape, which allows fill.

### Styling

```python
capsule.set_stroke(color=YELLOW, width=6)
capsule.set_fill(color=WHITE, opacity=0.5)
```

- Stroke: yellow border with width 6.
- Fill: white semi-transparent interior.
- Because the path is closed, the fill renders as a solid capsule.

---

## Debug Visuals and Animation Flow

### Debug Markers

```python
dot1 = Dot(point=p1, color=WHITE)
dot2 = Dot(point=p2, color=WHITE)
lbl1 = Text("P1", font_size=20).next_to(dot1, UP)
lbl2 = Text("P2", font_size=20).next_to(dot2, DOWN)
```

- Marks and labels intersection points.

```python
arrow_A = Arrow(start=c1, end=c1 + outward_A, buff=0, stroke_width=3)
arrow_B = Arrow(start=c2, end=c2 + outward_B, buff=0, stroke_width=3)
```

- Arrows from each center in the outward direction. Helpful to visualize "which side is outer."

### Animation Sequence

```python
self.play(Create(circle1), Create(circle2))
self.wait(0.5)

self.play(FadeIn(dot1, lbl1), FadeIn(dot2, lbl2))
self.play(Create(arrow_A), Create(arrow_B))
self.wait(0.3)

self.play(DrawBorderThenFill(capsule), run_time=3)
self.wait(2)
```

- First: draw both circles.
- Then: fade in intersection points and labels.
- Next: draw outward direction arrows.
- Finally: animate drawing and filling the capsule with `DrawBorderThenFill`, showing the path is continuous and closed.

---

## Conceptual Summary

**Math Layer**:
- Uses exact circle–circle intersection formulas \((a, h)\).
- Constructs intersection points from the center line plus perpendicular offsets.
- Uses polar angles and dot products to choose between two possible arcs.

**Manim Layer**:
- Uses `Circle` for guides, `Arc` for curved segments, and `VMobject` for stitching arcs into one continuous, closed shape.
- Snaps endpoints and calls `close_path()` to ensure filling works correctly.
- Adds debug elements (dots, labels, arrows) and an animation sequence to visualize and verify the geometry.

The result is a robust, parameterized capsule construction that generalizes to any two intersecting circles with non-coincident centers.
