import asyncio
import datetime
import json
import ntpath
import re
from random import choice

import aiosmtplib as asyncsmtp
import dns.resolver

from udf_package.email_verification.logger_conf import configure
from udf_package.email_verification.proxy import get_proxy

# connect redis server
from udf_package.email_verification.redis_server import redis_check

# variable set up
addressToVerify = []  # addressToVerify store all the details of mail/emails
i = 0
exp_ip = 0
valid_cnt = 0
invalid_cnt = 0
bad_cnt = 0
cnt = 0
length = 0
redis_cnt = 0
# call proxy.py
proxy_arr = get_proxy()  # proxy_arr store proxy ip and port
# using proxy_arr variable
proxy = str(choice(proxy_arr)).split(":")
proxy_ip = proxy[0]
proxy_port = proxy[1]
st = datetime.datetime.now()


async def send_mail(email, jsonLogOutputFile, outputResponseFile, print):
    global exp_ip, proxy_ip, proxy_port, invalid_cnt, valid_cnt, bad_cnt
    (data_status, redis_server, valid_cnt, invalid_cnt, bad_cnt) = redis_check(
        email, jsonLogOutputFile, valid_cnt, invalid_cnt, bad_cnt, print
    )

    # data_status means if mail id found in redis cache we will not check further
    if not data_status:  # data_status==False
        if exp_ip >= 5:
            proxy = str(choice(proxy_arr)).split(":")
            proxy_ip = proxy[0]
            proxy_port = proxy[1]
            exp_ip = 0
        # close if

        # check mail syntax
        syntax = "^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,})$"
        match = re.match(syntax, email)  # no match found return none(false)
        if match is None:
            print("%s: Is Wrong Email Address Syntax" % email)
            json.dump("email", jsonLogOutputFile)
            jsonLogOutputFile.write(":")
            jsonLogOutputFile.write('"Invalid",\n')

            # 172800 sec store for 48 hours
            redis_server.set(email, "Invalid", 172800)
            invalid_cnt += 1
            return
        # close if

        # check for domain
        domains = email.split("@")
        # print('Domain', domains[1])
        domain = domains[1]
        
        # check dns records
        try:
            records = dns.resolver.query(domain, "MX")
            await asyncio.sleep(0.002)
        except Exception as e:
            print(
                "%s : No Records Found for Domain(Risky)" % email
            )  # print on backend for information
            json.dump(email, jsonLogOutputFile)
            jsonLogOutputFile.write(":")
            jsonLogOutputFile.write('"Risky",\n')
            redis_server.set(email, "Risky", 172800)

            bad_cnt += 1
            exp_ip += 1
            return

        mxRecods = str(records[0].exchange)
        # smtp lib setup
        try:
            s1 = asyncsmtp.SMTP(mxRecods, port=25)
            await s1.connect()
            await asyncio.sleep(0.001)
        except Exception as e:  # for timeout
            print("%s : Not Able to Connect With Server:(Risky)" % email)
            pass
            json.dump(email, jsonLogOutputFile)
            jsonLogOutputFile.write(":")
            jsonLogOutputFile.write(' "Risky",\n')
            redis_server.set(email, "Risky", 172800)
            exp_ip += 1
            bad_cnt += 1
            return

        try:
            await s1.helo(timeout=5)
            pass
            await s1.mail("me@gmail.com")
            code, msg = await s1.rcpt(email)
            await asyncio.sleep(0.1)
            if code == 250: 
                datapiyush = {
                    "email": email,
                    "status": "Valid",
                    "reason": "250 Valid",
                    "code": "100"
                }
                print("%s : Piyush Valid" % email)
                jsonString = json.dumps(datapiyush)
                # json.dump([{'email': email, 'status': 'Valid'}])
                jsonLogOutputFile.write(jsonString)
                outputResponseFile.write(jsonString)
                redis_server.set(email, "Valid", 172800)
                valid_cnt += 1
                return
        except asyncsmtp.SMTPRecipientRefused:  # status code 550
            print("%s: Invalid" % email)
            json.dump("email", jsonLogOutputFile)
            jsonLogOutputFile.write(":")
            jsonLogOutputFile.write('"Invalid",\n')
            redis_server.set(email, "Invalid", 172800)
            invalid_cnt += 1
            exp_ip += 1
            return
        except asyncsmtp.SMTPSenderRefused:  # like outlook/hotmail
            # The server didn't accept the sender's email
            print("%s : Sender Refused to check test connection : (Risky)" % email)
            json.dump(email, jsonLogOutputFile)
            jsonLogOutputFile.write(":")
            jsonLogOutputFile.write(' "Risky",\n')
            redis_server.set(email, "Risky", 172800)
            bad_cnt += 1
            exp_ip += 1
            return
            pass
        except:  # if any other error occurred consider as bad request
            print("%s : Bad request (Risky)" % email)
            json.dump(email, jsonLogOutputFile)
            jsonLogOutputFile.write(":")
            jsonLogOutputFile.write(' "Risky",\n')
            redis_server.set(email, "Risky", 172800)
            bad_cnt += 1
            exp_ip += 1
            return
        try:
            await s1.quit()
        except Exception as e:
            print("%s: Not able to Quit server(Risky)" % email)
            json.dump(email, jsonLogOutputFile)
            jsonLogOutputFile.write(":")
            jsonLogOutputFile.write('"Risky",\n')
            # 172800 for 48 hours
            redis_server.set(email, "Risky", 172800)
            bad_cnt += 1
            exp_ip += 1
            return


@asyncio.coroutine
async def send_many(
    addressToVerify, found, read_File, print
):  # By which we can able to check many connections
    global cnt, outputLogFile, outputResponseFile
    if found:
        outputLogFile = open(ntpath.basename(read_File).replace(".json", "-s.json"), "w+")
        outputResponseFile = open(ntpath.basename(read_File).replace(".json", "-api-response.json"), "w+")
        # write data in file
        outputLogFile.write("{\n")

        print("START - Validating Emails ...")
        index = 0
        task = []

        for email in range(len(addressToVerify)):
            if index + 10 > addressToVerify.__len__():
                break
            # we are checking 10 mails at a time.   
            for j in range(0, 10):
                task.append(
                    asyncio.create_task(
                        send_mail(addressToVerify[index], outputLogFile, outputResponseFile, print)
                    )
                )
                index += 1
                if index % 10 == 0:
                    await asyncio.wait(task)
                # close if
            # close for
        # close for

        # we check for the remaining address and call that
        while index != addressToVerify.__len__():
            # print(colored('CALL FROM WHILE', 'green'))
            task_remaining = asyncio.create_task(
                send_mail(addressToVerify[index], outputLogFile, outputResponseFile, print)
            )
            await asyncio.wait([task_remaining])
            index += 1
            await asyncio.sleep(1)
        # close while loop
        # close for loop
        print("END - returning control...")
        outputLogFile.write("}")
        # close file
        outputLogFile.close()
        outputResponseFile.close()
        await asyncio.sleep(1)

    return outputLogFile, valid_cnt, invalid_cnt, bad_cnt, datetime.datetime.now() - st
