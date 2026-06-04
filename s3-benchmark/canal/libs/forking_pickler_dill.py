from multiprocessing.reduction import ForkingPickler, AbstractReducer
import dill


class ForkingPicklerDill(ForkingPickler):
    """
    Override the pickle method for multiprocessing, as the default "pickle" is missing quite some stream_operators
    (not easy to pickle a lambda), we use dill which has way better support.
    https://github.com/python/cpython/blob/master/Lib/multiprocessing/reduction.py#L33
    """
    PROTOCOL_VERSION = 2

    # pylint: disable=W0613

    def __init__(self, *args):
        # Convert list to tuple and set the protocol version
        parameters = list(args)
        if len(args) > 1:
            parameters[1] = ForkingPicklerDill.PROTOCOL_VERSION
        else:
            parameters.append(ForkingPicklerDill.PROTOCOL_VERSION)

        super().__init__(*parameters)

    @classmethod
    def dumps(cls, obj, protocol=PROTOCOL_VERSION):
        """Receive a raw object, and return a pickled version of it"""
        return dill.dumps(obj, protocol)

    @classmethod
    def loads(cls, data, *args, **kwargs):
        """
        Receive a pickled data object, and return an un-pickled version
        We keep the args/kwards in case the external library provides extra parameters (which we don't use)
        """
        return dill.loads(data)


class PickleDillReducer(AbstractReducer):
    """
    Set the custom pickling class
    """
    ForkingPickler = ForkingPicklerDill
    register = ForkingPicklerDill.register
