import os



from comic import Comic


class Series:

    contains = []

    def __init__(self, containing_directory):
        for file in sorted(os.listdir(containing_directory)):
            extension = (file.split(".")[-1])
            if extension in ["cbr", "cbz"]:
                print(file)
                if extension == "cbz":
                    issue = Comic(containing_directory, file)
                    if issue.set_thumbnail_from_zip():
                        self.contains.append(issue)
                if extension == "cbr":
                    issue = Comic(containing_directory, file)
                    if issue.set_thumbnail_from_rar():
                        self.contains.append(issue)




