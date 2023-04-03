from .quarternion import Quarternion

class Vector:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return str( (self.x, self.y, self.z) )

    def __iter__(self):
        return iter( (self.x, self.y, self.z) )
    
    def __eq__(self, v2):
        return all(a == b for a, b in zip(self, v2))
    
    def __mul__(self, v2):

        if isinstance(v2, Quarternion):
            # convert me to a Quarternion
            q1 = Quarternion(0.0, *self)
            qr = v2 * q1 * v2.conjugate()
            return Vector(qr.x, qr.y, qr.z)
        else:
            raise ValueError()
        
    def __sub__(self, v2):
        return Vector(self.x - v2.x, self.y - v2.y, self.z - v2.z)