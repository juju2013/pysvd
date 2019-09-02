import re
import pysvd

# Note construtors: First class specific code is executed than parent constructor
# called, so that on last constructor of Base parser() can be called also hierachical
# on every parent object automatically.


class Base(object):
    """Base class for all SVD elements"""

    def __init__(self, node):
        self.node = node
        self.parent = getattr(self, 'parent', None)

        self.parse(self.node)

    def parse(self, node):
        """Overwrite in derived classes to parse nodes"""
        pass

    def add_attributes(self, attr):
        """Add not 'None' entries as class attributes"""
        self.__dict__.update({k: v for k, v in attr.items() if v is not None})

    def find(self, name):
        """Find child by name. Has to be overwritten by each derived class with child elements."""
        assert not hasattr(super(), 'find')
        return None

    @classmethod
    def add_elements(cls, parent, elements, node, name):
        """Parse node elements and add them to elements list"""

        for subnode in node.findall(name):
            elements.append(cls(parent, subnode))


class Parent(Base):
    """Base class for parents"""

    def __init__(self, parent, node):
        self.parent = parent

        super().__init__(node)


class Group(Parent):
    """Base class for elements with registerPropertiesGroup"""

    attributes = ['size', 'access', 'protection', 'resetValue', 'resetMask']

    def __init__(self, parent_, node):
        super().__init__(parent_, node)

    def __getattr__(self, attr):
        if attr in self.attributes:
            parent = self.parent
            while parent is not None:
                try:
                    return parent.__getattribute__(attr)
                except:
                    parent = parent.parent

        raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, attr))


class Derive(Group):
    """Base for deriveable classes"""

    def __init__(self, parent, node):
        super().__init__(parent, node)

    def parse(self, node):
        super().parse(node)

        # If derived, search class, call parse attributes of derived object and call base ctor
        derivedFrom = pysvd.node.Attribute(node, 'derivedFrom')
        if derivedFrom is not None:
            parts = derivedFrom.split('.')
            count = len(parts) - 1
            object = self.parent
            while count:
                object = object.parent
                count -= 1

            if object is None:
                name = pysvd.parser.Text(pysvd.node.Element(node, 'name'))
                raise KeyError("Can not find root element from path '{}' to derive '{}'".format(derivedFrom, name))

            for name in parts:
                res = object.find(name)
                if res is None:
                    raise KeyError("Can not find path element '{}' from path '{}' in object '{}'".format(name, derivedFrom, object.name))
                object = res

            self.parse(object.node)
            self.derived = True
        else:
            self.derived = False


class Dim(Derive):

    def __init__(self, parent, node):
        super().__init__(parent, node)

    def parse(self, node):
        super().parse(node)

        self.name = pysvd.parser.Text(pysvd.node.Element(node, 'name', True))
        self.description = pysvd.parser.Text(pysvd.node.Element(node, 'description'))
        self.dimName = pysvd.parser.Text(pysvd.node.Element(node, 'dimName'), self.name)
        self.offset = 0

    # Replace %s with name if not None
    def set_index(self, value):
        value = str(value)
        self.name = self.name.replace('%s', value)
        if self.description is not None:
            self.description = self.description.replace('%s', value)

        if self.dimName is not None:
            self.dimName = self.dimName.replace('%s', value)

    def set_offset(self, value):
        self.offset = value

    @classmethod
    def add_elements(cls, parent, elements, node, name):
        """Parse node elements with respect to dim entries and return a list with constucted elements"""

        for subnode in node.findall(name):
            dim = pysvd.parser.Integer(pysvd.node.Element(subnode, 'dim'))
            if dim is not None:
                dimIncrement = pysvd.parser.Integer(pysvd.node.Element(subnode, 'dimIncrement', True))
                dimIndex = pysvd.parser.Text(pysvd.node.Element(subnode, 'dimIndex'))
                if dimIndex is not None:
                    if ',' in dimIndex:
                        dimIndices = dimIndex.split(',')
                    elif '-' in dimIndex:
                        match = re.search('([0-9]+)\-([0-9]+)', dimIndex)
                        dimIndices = list(range(int(match.group(1)), int(match.group(2)) + 1))
                    else:
                        raise ValueError("Unexpected value in 'dimIndex': {}".format(dimIndex))

                    if len(dimIndices) != dim:
                        raise AttributeError("'dim' size does not match elements in 'dimIndex' ({} != {})".format(dim, len(dimIndex)))
                else:
                    dimIndices = [dim]

                offset = 0
                for index in dimIndices:
                    object = cls(parent, subnode)
                    object.set_index(index)
                    object.set_offset(offset)
                    elements.append(object)
                    offset += dimIncrement
            else:
                elements.append(cls(parent, subnode))
