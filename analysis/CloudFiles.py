__author__ = 'Sushant'

import os

import pyrax


class CloudFiles(object):
    def __init__(self, container_name=None):
        pyrax.set_setting("identity_type", "rackspace")
        pyrax.set_default_region('DFW')
        pyrax.set_credentials('sushanttripathy', '28c8e8d9119e2af5877405c7d927474c')
        self.container = None
        return

    def set_container(self, container_name):
        if container_name is not None:
            #print "Opening container : "+container_name
            try:
                self.container = pyrax.cloudfiles.get_container(container_name)
                #if self.container is not None:
                #    print "Successfully opened container"
            except Exception as e:
                #print e.message
                try:
                    #print "Creating container : "+container_name
                    self.container = pyrax.cloudfiles.create_container(container_name)
                except Exception as e_:
                    self.container = None
        return

    def write_file(self, contents, container_file_path):
        if self.container is not None and contents is not None and container_file_path is not None:
            try:
                self.container.store_object(container_file_path, contents)
            except Exception as e:
                pass
        return

    def upload_file(self, local_file_path, container_file_path=None):
        if self.container is not None and local_file_path is not None:
            if container_file_path is None:
                container_file_path = os.path.basename(local_file_path)
            with open(local_file_path, 'rb') as f:
                contents = f.read()
                self.write_file(contents, container_file_path)
        return

    def read_file(self, container_file_path):
        if self.container is not None and container_file_path is not None:
            try:
                contents = self.container.fetch_object(container_file_path)
            except Exception as e:
                contents = None
        return contents

    def download_file(self, container_file_path, local_file_path):
        if self.container is not None and container_file_path is not None and local_file_path is not None:
            contents = self.read_file(container_file_path)
            #print "Contents obtained! Length : " + repr(len(contents))
            with open(local_file_path, 'wb') as f:
                f.write(contents)
        return


"""
c = CloudFiles()

c.set_container("test_test")

c.upload_file("computer_vision/testimages/test01.jpg")

c.download_file("test01.jpg", "test01.jpg")
"""