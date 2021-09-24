import json
from udf_package.email_verification.logger_conf import configure

addressToVerify = []
found = False
i = 0

#               return addressToVerify, found
def open_file(
    file_name, print
):  # open specified file and return addressToVerify and found
    global i, found

    print("File Name:%s " % file_name)
    print("Processing...")
    try:
        with open(file_name, "r") as f:

            # read data from json file
            readData = json.load(f)

            for i1 in readData:
                # store details/email in addressToVerify
                addressToVerify.append(readData[i])
                i += 1
                found = True
                f.close()
            return addressToVerify, found
    except FileNotFoundError as e:
        print("No such file or directory:%s" % file_name)
        return addressToVerify, found
