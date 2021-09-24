import os
import sys
import asyncio

p = os.path.abspath("./..")

if p not in sys.path:
    sys.path.append(p)

# remove python from package
from udf_package.email_verification.process import *
from udf_package.email_verification.read_file import *
from udf_package.email_verification.write_data import *

# calling logger_conf.py and creating object and we are passing to file which need to print statement
print = configure()

# call package
if sys.argv.__len__() == 2:
    # read file name from command line
    read_File = sys.argv[1]

    # call function open_file and read file
    (addressToVerify, found) = open_file(read_File, print)

    loop = asyncio.get_event_loop()
    # call function send many where we validate mail
    json_status, valid_cnt, invalid_cnt, bad_cnt, time_taken = loop.run_until_complete(
        send_many(addressToVerify, found, read_File, print)
    )

    # writing data to file
    file_status = store(json_status)

    print("\nResult stored in %s File\n" % file_status.name)
    print("Total Email : %s" % (valid_cnt + invalid_cnt + bad_cnt))
    print("Valid : %s" % valid_cnt)
    print("Invalid : %s" % invalid_cnt)
    print("Bad/Risky : %s" % bad_cnt)
    print("Time Taken: %s" % time_taken)
else:
    print("Please Enter File Name...")
