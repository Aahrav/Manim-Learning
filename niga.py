from manim import *
class SceneExample(Scene):
    def construct(self):
        circle = Circle()  # Create a circle
        circle.set_fill(TEAL, opacity=0.5)  # Set the color and transparency

        self.play(Create(circle))  # Animate the creation of the circle
        self.wait(1)  # Wait for a second