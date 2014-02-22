# internal
from galah.core.backends.redis import *
from galah.core.objects import *

# external
import pytest

# A crazy unicode string suitable for use in testing. Prints as
# "THE PONY HE COMES" with tons of decoration.
UNICODE_TEST_PONY = (
    u"TH\u0318E\u0344\u0309\u0356 \u0360P\u032f\u034d\u032dO\u031a\u200bN"
    u"\u0310Y\u0321 H\u0368\u034a\u033d\u0305\u033e\u030e\u0321\u0338\u032a"
    u"\u032fE\u033e\u035b\u036a\u0344\u0300\u0301\u0327\u0358\u032c\u0329 "
    u"\u0367\u033e\u036c\u0327\u0336\u0328\u0331\u0339\u032d\u032fC\u036d"
    u"\u030f\u0365\u036e\u035f\u0337\u0319\u0332\u031d\u0356O\u036e\u034f"
    u"\u032e\u032a\u031d\u034dM\u034a\u0312\u031a\u036a\u0369\u036c\u031a"
    u"\u035c\u0332\u0316E\u0311\u0369\u034c\u035d\u0334\u031f\u031f\u0359"
    u"\u031eS\u036f\u033f\u0314\u0328\u0340\u0325\u0345\u032b\u034e\u032d"
)

# Another crazy unicode string that renders as mostly scribbles.
UNICODE_TEST_SCRIBBLES = (
    u" \u031b \u0340 \u0341 \u0358 \u0321 \u0322 \u0327 \u0328 \u0334 \u0335 "
    u"\u0336 \u034f \u035c \u035d \u035e \u035f \u0360 \u0362 \u0338 \u0337 "
    u"\u0361 \u0489"
)

class TestNode:
    def test_allocate(self, redis_server):
        id1 = redis_server.node_allocate_id(UNICODE_TEST_PONY)
        id2 = redis_server.node_allocate_id(UNICODE_TEST_PONY)
        id3 = redis_server.node_allocate_id(UNICODE_TEST_PONY)
        assert id1 != id2 and id1 != id3 and id2 != id3

        with pytest.raises(TypeError):
            # The argument must be a unicode string
            redis_server.node_allocate_id("localhost")

        with pytest.raises(TypeError):
            # The argument must be a unicode string
            redis_server.node_allocate_id(2)

class TestVMFactory:
    def test_registration(self, redis_server):
        """
        Basic test to ensure that registering and unregistering VMs work to
        some degree.

        """

        my_id = NodeID(machine = UNICODE_TEST_PONY, local = 0)

        # Try to unregister our not registered node
        assert not redis_server.vmfactory_unregister(my_id)

        # Register our node
        assert redis_server.vmfactory_register(my_id)

        # Re-register our node
        assert not redis_server.vmfactory_register(my_id)

        # Unregister our node
        assert redis_server.vmfactory_unregister(my_id)

        # Unregister our node again
        assert not redis_server.vmfactory_unregister(my_id)

    def test_grab_clean(self, redis_server):
        """
        Tests grab to ensure that it will return True when there are no queued
        VMs waiting for deletion.

        """

        my_id = NodeID(machine = u"localhost", local = 0)
        assert redis_server.vmfactory_register(my_id)

        grab_hints = {"max_clean_vms": 2}

        # This should tell us to make a clean virtual machine
        assert redis_server.vmfactory_grab(my_id, grab_hints)

        # The last grab should have assigned us the work, so this should error
        # out.
        with pytest.raises(CoreError):
            redis_server.vmfactory_grab(my_id, grab_hints)

    def test_grab_dirty(self, redis_server):
        """
        This test ensures that we get a dirty VM from grab if there is one
        queued.

        """

        my_id = NodeID(machine = u"localhost", local = 0)
        assert redis_server.vmfactory_register(my_id)

        grab_hints = {"max_clean_vms": 2}

        fake_vm_id = NodeID(machine = u"localhost", local = 1)
        assert redis_server.vm_mark_dirty(fake_vm_id)

        fake_vm_id2 = NodeID(machine = u"localhost", local = 2)
        assert redis_server.vm_mark_dirty(fake_vm_id2)

        dirty_vm = redis_server.vmfactory_grab(my_id, grab_hints)
        assert dirty_vm == fake_vm_id
        assert isinstance(dirty_vm, NodeID)

        # We are already assigned work so this should fail
        with pytest.raises(CoreError):
            redis_server.vmfactory_grab(my_id, grab_hints)

    def test_workflow_clean(self, redis_server):
        """
        This tests performs all of the calls a vmfactory who is creating
        clean VMs would make while performing its duties.

        """

        my_id = NodeID(machine = u"localhost", local = 0)
        assert redis_server.vmfactory_register(my_id)

        grab_hints = {"max_clean_vms": 20}

        # We should be able to continually perform these operations so we'll
        # do them ten times here.
        for i in range(10):
            # This should tell us to make a clean virtual machine
            assert redis_server.vmfactory_grab(my_id, grab_hints)

            with pytest.raises(CoreError):
                redis_server.vmfactory_finish(my_id)

            # We'll pretend we created a machine
            fake_vm_id = NodeID(machine = u"localhost", local = i + 1)
            assert redis_server.vmfactory_note_clean_id(my_id, fake_vm_id)

            assert redis_server.vmfactory_finish(my_id)

            with pytest.raises(CoreError):
                redis_server.vmfactory_finish(my_id)

    def test_workflow_dirty(self, redis_server):
        my_id = NodeID(machine = u"localhost", local = 0)
        assert redis_server.vmfactory_register(my_id)

        grab_hints = {"max_clean_vms": 3}

        # We should be able to continually perform these operations so we'll
        # do them ten times here.
        for i in range(10):
            fake_vm_id = NodeID(machine = u"localhost", local = i + 1)
            assert redis_server.vm_mark_dirty(fake_vm_id)

            # This should tell us to destroy the dirty VM
            assert redis_server.vmfactory_grab(my_id, grab_hints) == fake_vm_id

            # Say that we finished
            assert redis_server.vmfactory_finish(my_id)

            # We shouldn't be able to finish twice without error
            with pytest.raises(CoreError):
                redis_server.vmfactory_finish(my_id)

class TestVM:
    def test_registration(self, redis_server):
        """Tests to see if VMs can be registered and unregistered cleanly."""

        vm_id = NodeID(machine = u"localhost", local = 0)
        assert redis_server.vm_register(vm_id)
        assert not redis_server.vm_register(vm_id)

        vm_id2 = NodeID(machine = u"localhost", local = 1)
        assert redis_server.vm_register(vm_id2)
        assert not redis_server.vm_register(vm_id2)

        assert redis_server.vm_unregister(vm_id)
        assert not redis_server.vm_unregister(vm_id)

        assert redis_server.vm_unregister(vm_id2)
        assert not redis_server.vm_unregister(vm_id2)

    def test_metadata(self, redis_server):
        """Tests to see if metadata about VMs can be stored reliably."""

        # We'll usethis key and value throughout the rest of the test
        key, value = u"bla", "hello"

        vm_id = NodeID(machine = u"localhost", local = 0)

        # Setting metadata on a VM that doesn't exist raises
        with pytest.raises(objects.IDNotRegistered):
            redis_server.vm_set_metadata(vm_id, key, value)

        # None is returned if querying metadata of a VM that doesn't exist
        assert redis_server.vm_get_metadata(vm_id, key) is None

        assert redis_server.vm_register(vm_id)

        # Only unicode keys and string values should be accepted
        with pytest.raises(TypeError):
            redis_server.vm_set_metadata(vm_id, "string", value)
        with pytest.raises(TypeError):
            redis_server.vm_set_metadata(vm_id, key, 23)

        # It should return None if no value is associated with the key
        assert redis_server.vm_get_metadata(vm_id, key) is None

        assert redis_server.vm_set_metadata(vm_id, key, value)

        # False should be returned if we are updating the value rather than
        # setting it for the first time.
        assert not redis_server.vm_set_metadata(vm_id, key, value)

        # Make sure we get back what we want
        rv = redis_server.vm_get_metadata(vm_id, key)
        assert rv == value
        assert type(rv) is type(value)
