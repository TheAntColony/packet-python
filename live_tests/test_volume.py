import os
import sys
import unittest
import time
import packet


class TestDevice(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.manager = packet.Manager(auth_token=os.environ['PACKET_TOKEN'])
        self.projectId = self.manager.list_projects()[0].id

        self.volume = self.manager.create_volume(
            self.projectId, "volume description",
            "storage_1", "100",
            "ewr1", 7, "1day")

        while True:
            if self.manager.get_volume(self.volume.id).state == "active":
                break
            time.sleep(2)

        self.device = self.manager.create_device(
            self.projectId, "devicetest", "baremetal_0", "ewr1", "centos_7"
        )

        while True:
            if self.manager.get_device(self.device.id).state == "active":
                break
            time.sleep(2)

    def test_get_volume(self):
        volume = self.manager.get_volume(self.volume.id)
        self.assertEquals(volume.description, self.volume.description)

    def test_list_volumes(self):
        volumes = self.manager.list_volumes(self.projectId)
        for volume in volumes:
            if volume.id is self.volume.id:
                break
        self.assertRaises(TypeError)

    def test_update_volume(self):
        self.volume.description = "newdescription"
        self.volume.update()
        volume = self.manager.get_volume(self.volume.id)
        self.assertEquals(self.volume.description, volume.description)

    def test_attach_volume(self):
        self.volume.attach(self.device.id)
        while True:
            if self.manager.get_device(self.device.id).state == "active":
                break
            time.sleep(1)

    def test_detach_volume(self):
        self.volume.detach()
        while True:
            if self.manager.get_device(self.device.id).state == "active":
                break
            time.sleep(1)

    def test_create_snapshot(self):
        self.volume.create_snapshot()

    def test_get_snapshots(self):
        snapshots = self.manager.get_snapshots(self.volume.id)
        self.assertIsNotNone(snapshots)
        self.timestamp = snapshots[0].timestamp

    def test_clone_volume(self):
        self.clone = self.volume.clone()
        self.assertIsNotNone(self.clone)

    def test_restore_volume(self):
        self.volume.restore(self.timestamp)

    @classmethod
    def tearDownClass(self):
        self.volume.delete()
        self.device.delete()
        self.clone.delete()


if __name__ == "__main__":
    sys.exit(unittest.main())