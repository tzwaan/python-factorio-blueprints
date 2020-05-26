import unittest

from py_factorio_blueprints.util import Color, Direction


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


if __name__ == '__main__':
    unittest.main()
