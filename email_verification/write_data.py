import os


# we have stored result on filename-s.json now we will store in filename-status.json
def store(json_status):
    file_s = open(json_status.name, "r")
    file_status = open(json_status.name.replace("-s.json", "-status.json"), "w+")

    data = file_s.readlines()
    data_cnt = 0

    # we are reading file again and making proper json file
    for content in range(len(data)):
        if data_cnt == data.__len__() - 2:
            # removing last comma(,)
            file_status.write(data[content].replace(",", ""))
        else:
            file_status.write(data[content])
        data_cnt += 1
    # close for
    file_status.close()
    file_s.close()
    os.remove(file_s.name)

    return file_status
