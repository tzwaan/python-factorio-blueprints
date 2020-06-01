import unittest

from py_factorio_blueprints.util import (
    Color, Direction, Vector
)


class TestColor(unittest.TestCase):
    def test_empty_color(self):
        color = Color()
        self.assertEqual(color.r, 1)
        self.assertEqual(color.g, 1)
        self.assertEqual(color.b, 1)
        self.assertEqual(color.a, 1)

    def test_positional_arguments(self):
        color_pos = Color(0, 0.25, 0.5, 0.75)
        color_kwargs = Color(r=0, g=0.25, b=0.5, a=0.75)
        self.assertEqual(color_pos, color_kwargs)

        color_pos = Color(0, 0.25)
        color_kwargs = Color(r=0, g=0.25)
        self.assertEqual(color_pos, color_kwargs)

    def test_repr(self):
        color = Color()
        self.assertEqual(repr(color), "<Color (r:1, g:1, b:1, a:1)>")

    def test_iter(self):
        values = [0, 0.25, 0.5, 0.75]
        color = Color(*values)
        for i, comp in enumerate(color):
            self.assertEqual(comp, values[i])

    def test_value_clamp(self):
        color = Color(
            r=10,
            g=10,
            b=10,
            a=10)
        self.assertEqual(color.r, 1)
        self.assertEqual(color.g, 1)
        self.assertEqual(color.b, 1)
        self.assertEqual(color.a, 1)
        color = Color(
            r=-10,
            g=-10,
            b=-10,
            a=-10)
        self.assertEqual(color.r, 0)
        self.assertEqual(color.g, 0)
        self.assertEqual(color.b, 0)
        self.assertEqual(color.a, 0)

    def test_to_json(self):
        obj = {
            'r': 0,
            'g': 0.25,
            'b': 0.5,
            'a': 0.75
        }
        color = Color(**obj)
        self.assertEqual(obj, color.to_json())


class TestDirection(unittest.TestCase):
    def test_init(self):
        self.assertEqual(0, Direction(0))
        self.assertEqual(0, Direction(8))
        self.assertEqual(7, Direction(7))
        self.assertEqual(7, Direction(-1))

    def test_add(self):
        self.assertIsInstance(Direction(1) + Direction(1), Direction)
        self.assertEqual(2, Direction(1) + Direction(1))
        self.assertEqual(2, Direction(3) + Direction(7))

    def test_sub(self):
        self.assertIsInstance(Direction(1) - Direction(1), Direction)
        self.assertEqual(1, Direction(3) - Direction(2))
        self.assertEqual(7, Direction(1) - Direction(2))

    def test_div(self):
        with self.assertRaises(TypeError):
            direction = Direction(1) // Direction(1)
        with self.assertRaises(TypeError):
            direction = Direction(1) / Direction(1)

    def test_repr(self):
        self.assertEqual(repr(Direction(3)), "<Direction (Down-Right)>")

    def test_shorthands(self):
        self.assertTrue(Direction.up().is_up)
        self.assertTrue(Direction.right().is_right)
        self.assertTrue(Direction.down().is_down)
        self.assertTrue(Direction.left().is_left)

    def test_rotate(self):
        direction = Direction.up()
        direction = direction.rotate(1)
        self.assertTrue(direction.is_right)
        direction = direction.rotate(6, direction=Direction.COUNTER_CLOCKWISE)
        self.assertTrue(direction.is_left)

        direction = direction.rotate45(2)
        self.assertTrue(direction.is_up)


class TestVector(unittest.TestCase):
    def test_new(self):
        self.assertEqual(Vector(None), None)
        self.assertEqual(Vector(), None)

    def test_init(self):
        vec1 = Vector(1, 2)
        vec2 = Vector((1, 2))
        vec3 = Vector(x=1, y=2)
        vec4 = Vector({'x': 1, 'y': 2})
        self.assertEqual(vec1, vec2)
        self.assertEqual(vec1, vec3)
        self.assertEqual(vec1, vec4)
        with self.assertRaises(TypeError):
            Vector(1, 2, x=1, y=2)

    def test_to_json(self):
        pos = {
            "x": 1.2,
            "y": 3.4
        }
        self.assertEqual(Vector(pos).to_json(), pos)

    def test_eq(self):
        vec = Vector(1, 2)
        self.assertEqual(vec, (1, 2))
        with self.assertRaises(ValueError):
            if vec == (1, 2, 3):
                pass

    def test_iter(self):
        vec = Vector(1, 2)
        vec2 = [nr for nr in vec]
        self.assertEqual(vec2, [1, 2])

    def test_xy(self):
        vec = Vector(1, 2)
        self.assertEqual(vec.xy, (1, 2))

    def test_yx(self):
        vec = Vector(1, 2)
        self.assertEqual(vec.yx, (2, 1))

    def test_repr(self):
        vec = Vector(1, 2)
        self.assertEqual("<Vector (1, 2)>", repr(vec))

    def test_add(self):
        self.assertEqual(Vector(1, 2) + Vector(1, 3),
                         Vector(2, 5))
        self.assertEqual(Vector(1, 2) + (1, 3),
                         Vector(2, 5))
        self.assertEqual(Vector(1, 2) + 1,
                         Vector(2, 3))
        self.assertEqual(1 + Vector(1, 2),
                         Vector(2, 3))

    def test_sub(self):
        self.assertEqual(Vector(2, 4) - Vector(1, 2),
                         Vector(1, 2))
        self.assertEqual(Vector(2, 4) - (1, 2),
                         Vector(1, 2))
        self.assertEqual(Vector(2, 4) - 1,
                         Vector(1, 3))
        self.assertEqual(4 - Vector(1, 2),
                         Vector(3, 2))

    def test_mul(self):
        self.assertEqual(Vector(2, 4) * Vector(2, 3),
                         Vector(4, 12))
        self.assertEqual(Vector(2, 4) * (2, 3),
                         Vector(4, 12))
        self.assertEqual(Vector(2, 4) * 2,
                         Vector(4, 8))
        self.assertEqual(2 * Vector(2, 4),
                         Vector(4, 8))

    def test_truediv(self):
        self.assertEqual(Vector(4, 6) / Vector(2, 4),
                         Vector(2, 1.5))
        self.assertEqual(Vector(4, 6) / (2, 4),
                         Vector(2, 1.5))
        self.assertEqual(Vector(4, 6) / 3,
                         Vector(4/3, 2))
        self.assertEqual((4, 6) / Vector(2, 4),
                         Vector(2, 1.5))
        self.assertEqual(4 / Vector(2, 3),
                         Vector(2, 4/3))

    def test_floordiv(self):
        self.assertEqual(Vector(3, 7) // Vector(2, 3),
                         Vector(1, 2))
        self.assertEqual(Vector(3, 7) // (2, 3),
                         Vector(1, 2))
        self.assertEqual(Vector(3, 7) // 2,
                         Vector(1, 3))
        self.assertEqual(7 // Vector(2, 3),
                         Vector(3, 2))

    def test_mod(self):
        self.assertEqual(Vector(7, 8) % Vector(5, 4),
                         Vector(2, 0))
        self.assertEqual(Vector(7, 8) % (5, 4),
                         Vector(2, 0))
        self.assertEqual(Vector(7, 8) % 5,
                         Vector(2, 3))
        self.assertEqual(8 % Vector(3, 4),
                         Vector(2, 0))

    def test_ceil(self):
        self.assertEqual(Vector(1.2, 4.3).ceil(),
                         Vector(2, 5))

    def test_floor(self):
        self.assertEqual(Vector(1.2, 4.3).floor(),
                         Vector(1, 4))

    def test_copy(self):
        vec = Vector(1, 2)
        vec2 = vec.copy()
        self.assertEqual(vec, vec2)
        self.assertIsNot(vec, vec2)

    def test_rotate(self):
        vec = Vector(1, 2)
        self.assertEqual(vec.rotate(1), Vector(-2, 1))
        self.assertEqual(vec.rotate(-1), Vector(2, -1))


if __name__ == '__main__':
    unittest.main()
