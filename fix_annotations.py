#!/usr/bin/env python3

import json
import inspect

__author__ = "Dibyo Majumdar"
__email__ = "dibyo.majumdar@gmail.com"


def fix_annotations(cls: object):
    # Get the class name
    cls_name = cls.__name__

    # Check all attributes of the class
    for attr in cls.__dict__.values():
        # Check if the attribute is a function (ie. if it is callable) and
        # if it has stored annotations.
        if inspect.isfunction(attr):
            for param, annotation in attr.__annotations__.copy().items():
                if annotation == cls_name:
                    attr.__annotations__[param] = cls

    return cls


#####################
# Recursive version #
#####################

def get_cls_names(cls: object) -> list:
    prefix = cls.__name__
    cls_names = {prefix: cls}

    for attr in cls.__dict__.values():
        if inspect.isclass(attr):
            nested_cls_names = get_cls_names(attr)

            for name, nested_class in nested_cls_names:
                cls_names['.'.join([prefix, name])] = nested_class

    return cls_names


def check_annotations(cls: object, cls_names: list) -> cls:
    for attr_name in cls.__dict__:
        attr = getattr(cls, attr_name)

        if inspect.isclass(attr):
            check_annotations(attr, cls_names)
        elif inspect.ismethod(attr) or inspect.isfunction(attr):
            for param, annotation in attr.__annotations__.copy().items():
                if annotation in cls_names:
                    attr.__annotations__[param] = cls_names[annotation]


def fix_annotations_recursive(cls: object):
    cls_names = get_cls_names(cls)

    check_annotations(cls, cls_names)

    return cls


###########
# Testing #
###########

@fix_annotations_recursive
class Test(object):
    """
    Just a test class with just random stuff that hopefully demonstrate
    the point.
    """
    def __init__(self, greeting: str):
        self._greeting = None
        self.greeting = greeting

    def __eq__(self, other: "Test") -> bool:
        """
        Check equality of two Test instances.  Two Test instances are
        equal if they have the same greeting.
        :param other: the other instance being checked
        """
        return self.greeting == other.greeting

    def test(self) -> str:
        """
        Test the class.
        """
        return "{} This is a test class. ".format(self.greeting)

    @property
    def greeting(self) -> str:
        """
        Get and set the greeting variable.  A greeting is valid only if
        it starts with "Hello".
        """
        return self._greeting

    @greeting.setter
    def greeting(self, new_greeting: str):
        if new_greeting.startswith('Hello'):
            self._greeting = new_greeting

    @greeting.deleter
    def greeting(self):
        del self._greeting

    def to_json(self) -> str:
        """
        Encode to JSON string.
        """
        return json.dumps({'greeting': self.greeting})

    @classmethod
    def from_json(cls, s: str) -> "Test":
        """
        Decode from JSON string into Test instance.
        :param s: the JSON string to be decoded
        """
        return cls(json.loads(s)['greeting'])