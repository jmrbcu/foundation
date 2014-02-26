class ReadOnlyProxy(object):

    def __init__(self, proxied=None, aliases=[]):
        # internal proxied object
        self.proxied = proxied

        # internal aliases for the proxied object
        self.aliases = aliases

    def __getattr__(self, name):
        # are we referring to the proxied object through an alias?
        if name in self.aliases:
            return self.proxied

        # get attributes from the internal proxied object
        return getattr(self.proxied, name)

    def __str__(self):
        return str(self.proxied)


class Proxy(ReadOnlyProxy):

    def __setattr__(self, name, value):
        base = super(Proxy, self)

        # are we assigning the a value to the internal
        # attributes: proxied or aliases?
        if name in ['proxied', 'aliases']:
            base.__setattr__(name, value)

        # are we assigning a value to one of the aliases?
        elif name in self.aliases:
            base.__setattr__('proxied', value)

        # value assignment to the internal proxied object
        else:
            # get the class dict of the proxied object
            dict = self.proxied.__class__.__dict__

            # check if we are assigning a value to a
            # property defined in the proxied object
            if name in dict and isinstance(dict[name], property):
                # get the property object
                prop = dict[name]
                # set the value of the property thought the fset method
                prop.fset(self.proxied, value)

            # normal assignment
            else:
                self.proxied.__dict__[name] = value


class LowerJoinedProxy(Proxy):

    def __getattr__(self, name):
        camel_name = self.camel_name(name)
        return super(LowerJoinedProxy, self).__getattr__(camel_name)

    def camel_name(self, name):
        return ''.join([n.capitalize() for n in name.split('_')])


class Borg:
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
        
class PingaPaTi(type):
    
    def __new__(cls, name, bases, dict):
        dict['pinga'] = 'metacls was here'
        return type.__new__(cls, name, bases, dict)
    
class Pinga(object):
    def __init__(self, cls):
        cls._
    
class Test(object):
    __metaclass__ = PingaPaTi
    
test = Test()
print test.foo 

