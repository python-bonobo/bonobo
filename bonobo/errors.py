# -*- coding: utf-8 -*-
#
# Copyright 2012-2014 Romain Dorgueil
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


class AbstractError(NotImplementedError):
    """Abstract error is a convenient error to declare a method as "being left as an exercise for the reader"."""

    def __init__(self, method):
        super().__init__(
            'Call to abstract method {class_name}.{method_name}(...): missing implementation.'.format(
                class_name=method.__self__.__name__,
                method_name=method.__name__,
            )
        )


class InactiveIOError(IOError):
    pass


class InactiveReadableError(InactiveIOError):
    pass


class InactiveWritableError(InactiveIOError):
    pass


class ValidationError(RuntimeError):
    def __init__(self, inst, message):
        super(ValidationError, self).__init__(
            'Validation error in {class_name}: {message}'.format(
                class_name=type(inst).__name__,
                message=message,
            )
        )


class ProhibitedOperationError(RuntimeError):
    pass


class ConfigurationError(Exception):
    pass


class MissingServiceImplementationError(KeyError):
    pass
