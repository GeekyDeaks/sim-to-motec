class Quarternion:

    def __init__(self, w, x, y, z):

        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return str( (self.w, self.x, self.y, self.z) )

    def __iter__(self):
        return iter( (self.w, self.x, self.y, self.z) )
    
    def __eq__(self, q2):
        return all(a == b for a, b in zip(self, q2))
    
    def __mul__(self, q2):

        w1, x1, y1, z1 = self
        w2, x2, y2, z2 = q2
        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
        z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
        return Quarternion(w, x, y, z)
    
    def conjugate(self):
        return Quarternion(self.w, -self.x, -self.y, -self.z)


    