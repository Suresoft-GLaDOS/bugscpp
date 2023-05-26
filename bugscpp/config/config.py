"""
Interface of env.py.

All the modifiable settings should be accessed via 'config' instead of using env.py directly.
"""
import sys


class _ConfigMeta(type):
    def __new__(mcs, name, bases, attrs):
        new_class = type.__new__(mcs, name, bases, attrs)
        if not hasattr(new_class, "_env_module"):

            def create_getter(getter_key: str):
                def getter(self):
                    return getattr(self._env_module, getter_key)

                return getter

            def create_setter(setter_key: str):
                def setter(self, value: str):
                    setattr(self._env_module, setter_key, value)

                return setter

            from config import env

            env_module = sys.modules[env.__name__]
            setattr(new_class, "_env_module", env_module)
            settings = {
                key: getattr(env_module, key)
                for key in dir(env_module)
                if key.startswith("DPP")
            }
            for k in settings:
                prop = property(create_getter(k), create_setter(k))
                setattr(new_class, k, prop)
        return new_class


class _Config(metaclass=_ConfigMeta):
    pass


config = _Config()
