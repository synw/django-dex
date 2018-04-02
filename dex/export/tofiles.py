import os
from ..msgs import msg


class ExportToFile():

    def sanitize_filename(self, name):
        """
        Cleans up filenames
        """
        if name.startswith("/"):
            name = name[1:]
        if name.endswith("/"):
            name = name[:-1]
        name.replace("/", "_")
        if name == "":
            name = "index"
        return name

    def tofiles(self, q, destination, slug_field,
                content_field, extension, func=None):
        """
        Exports data from a query to files
        Each record will be a file
        """
        # check dir
        if self.dir_exists(destination) == False:
            msg.error("The directory " + destination + " does not exist")
            return
        # run
        msg.info("Saving files to " + destination)
        for row in q.values():
            name = self.sanitize_filename(row[slug_field])
            content = row[content_field]
            filename = name + "." + extension
            filepath = destination + "/" + filename
            mesg = "Processing " + filepath
            # process custom function
            if func is not None:
                content = func(row)
            # write fifle
            self.write_file(filepath, content)
            msg.status(mesg)
        msg.ok("Done")

    def write_file(self, filepath, content):
        filex = open(filepath, "w")
        filex.write(content)
        filex.close()
        return (True, msg)

    def dir_exists(self, path):
        """
        Check if a directory exists
        """
        if not os.path.isdir(path):
            return False
        return True
