# python imports
import copy
from collections import OrderedDict
from cStringIO import StringIO


class TreeNode(object):

    def create_node(self, id, parent=None):
        self.id = id
        self.parent = None

        self.childs = []
        self._child_dict = {}
        self._sorted = True

        # used for caching
        self._level = -1
        self._pos = -1

        if parent:
            parent.add_child(self)

    @property
    def count(self):
        return len(self.childs)

    @property
    def pos(self):
        _pos = self._pos
        if _pos != -1:
            return _pos

        if self.parent is not None:
            _pos = self.parent.childs.index(self)
            self._pos = _pos
            return _pos

        # we have no parent so, pos is invalid: -1
        return _pos

    @property
    def level(self):
        _level = self._level
        if _level != -1:
            return _level

        _level = 0
        current = self
        while current.parent:
            _level += 1
            current = current.parent

        self._level = _level
        return _level

    def add_child(self, child, duplicates=False):
        return self.insert_child(self.count, child, duplicates)

    def insert_child(self, index, child, duplicates=False):
        child_list = self.childs
        child_dict = self._child_dict

        if not duplicates and child.id in child_dict:
            return False

        count = len(child_list)
        if not index < count:
            index = count
        elif index < 0:
            index = index % count

        child_list.insert(index, child)
        child_dict[child.id] = child
        child.parent = self
        child._pos = index

        return True

    def find_child(self, id, deep_search=False):
        child = self._child_dict.get(id)
        if child:
            return child

        if deep_search:
            for child in self.childs:
                child = child.find_child(id, deep_search)
                if child:
                    return child
        return None

    def remove_child(self, index):
        if not 0 <= index < self.count:
            return False

        node = self.childs[index]

        if node.id not in self._child_dict:
            return False

        self._child_dict.pop(node.id)
        self.childs.pop(index)

        # update the cached pos from index to end
        for child in self.childs[index:]:
            child._pos -= 1

        return True

    def merge(self, node):
        if not self.__class__ == node.__class__:
            raise TypeError('node must be of the very same type')

        if not self.level == node.level:
            raise TypeError('nodes must have the same level')

        for child in node.childs:

            self.add_child(child)
            added_child = self.find_child(child.id)
            added_child.merge(child)

    def walk(self):
        yield self
        for child in self.childs:
            for node in child.walk():
                yield node

    def sort(self, key=None, reverse=False, levels=0):
        if not levels or self.level <= levels:
            self.childs.sort(key=key, reverse=reverse)

        if not levels or self.level + 1 < levels:
            for child in self.childs:
                child.sort(key=key, reverse=reverse, levels=levels)

        # invalidate caching
        self._pos = -1

    def tree_str(self):
        result = StringIO()
        indent = self.level * 4 * ' '
        result.write(
            '\n'.join((indent + s for s in self.__str__().split('\n'))
        ))

        for child in self.childs:
            result.write('\n\n' + child.tree_str())
        return result.getvalue()


if __name__ == '__main__':
    import sys

    import gc
    gc.set_debug(gc.DEBUG_LEAK)

    class Person(TreeNode):
        def __init__(self, name, parent=None):
            self.name = name
            self.last_name = 'Last Name'
            self.create_node(name, parent)

        def __eq__(self, other):
            return self.name == other.name

        def __hash__(self):
            return hash(self.name)

        def __str__(self):
            return (
                'First Name: ' + self.name + '\n' +
                'Last Name: ' + self.last_name + '\n' +
                'Level: ' + str(self.level) + '\n' +
                'Pos: ' + str(self.pos) + '\n' +
                'Parent: ' + (self.parent.name if self.parent else '<no parent>')
            )


    father = Person('Jose')
    jose = Person('Jose M.')
    jose_new = Person('Jose M.')
    chela = Person('Asela M.')
    daira = Person('Daira')
    manu = Person('Manolito')
    sandra = Person('Sandra')
    manu.add_child(Person('YYY'))
    manu.add_child(Person('XXX'))



    father.add_child(jose)
    father.add_child(chela)
    father.add_child(jose_new)
    jose.add_child(sandra)
    jose.add_child(manu)
    father.add_child(daira)

    del jose_new
    del chela
    del daira
    del manu
    del sandra

    father.sort(key=lambda i: i.name)
    print father.tree_str()
    print 50 * '-'

    jose.remove_child(father.find_child('Manolito', True).pos)
    jose.remove_child(father.find_child('Sandra', True).pos)
    print father.tree_str()

    del jose
    father = None
    del father

    print gc.garbage
    print gc.collect()
    print gc.collect()


