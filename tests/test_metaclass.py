import unittest


from py_factorio_blueprints.util import ControlBehaviorMeta


class TestMetaclass(unittest.TestCase):
    def test_metaclass(self):
        class A(metaclass=ControlBehaviorMeta):
            attr1 = 'foo'

            class ControlBehavior:
                sub_attr1 = 'sub_foo'

        class B(metaclass=ControlBehaviorMeta):
            attr2 = 'bar'

            class ControlBehavior:
                sub_attr2 = 'sub_bar'

        class C(A, B):
            attr3 = 'foobar'

            class ControlBehavior:
                sub_attr3 = 'sub_foobar'

        c = C()
        self.assertEqual(c.attr1, 'foo')
        self.assertEqual(c.attr2, 'bar')
        self.assertEqual(c.attr3, 'foobar')
        self.assertEqual(c.ControlBehavior.sub_attr1, 'sub_foo')
        self.assertEqual(c.ControlBehavior.sub_attr2, 'sub_bar')
        self.assertEqual(c.ControlBehavior.sub_attr3, 'sub_foobar')
