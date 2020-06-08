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

        class D(C):
            attr4 = 'swan'

            class ControlBehavior:
                sub_attr4 = 'sub_swan'

        d = D()
        self.assertEqual(d.attr1, 'foo')
        self.assertEqual(d.attr2, 'bar')
        self.assertEqual(d.attr3, 'foobar')
        self.assertEqual(d.attr4, 'swan')
        self.assertEqual(d.ControlBehavior.sub_attr1, 'sub_foo')
        self.assertEqual(d.ControlBehavior.sub_attr2, 'sub_bar')
        self.assertEqual(d.ControlBehavior.sub_attr3, 'sub_foobar')
        self.assertEqual(d.ControlBehavior.sub_attr4, 'sub_swan')
