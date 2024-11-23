import glm

class Sphere:
    def __init__(self, c: glm.vec3, r: float):
        self.center = c
        self.radius = r

    def ray_intersect(self, orig: glm.vec3, dir: glm.vec3):
        """
        Ray intersection with the sphere. Returns the intersection distance (t0) if hit, otherwise None.
        
        Uses P(t) = A + t*B equation plugged into the quadratic formula:
        (-b ± sqrt(b*b - 4ac)) / 2a
        
        Returns:
            t0: The intersection distance if hit, otherwise None.
        """
        L = self.center - orig
        tca = glm.dot(L, dir)
        d2 = glm.dot(L, L) - tca * tca

        # If the distance to the ray is greater than the radius, no intersection
        if d2 > self.radius * self.radius: 
            return None

        thc = glm.sqrt(self.radius * self.radius - d2)
        t0 = tca - thc  # Nearest intersection point
        t1 = tca + thc  # Furthest intersection point
        
        if t0 < 0:
            t0 = t1  # If t0 is negative, use t1 (this means the intersection is behind the camera)
        
        if t0 < 0:
            return None  # No valid intersection

        return t0  # Return the distance to the intersection
