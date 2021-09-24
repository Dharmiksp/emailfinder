import json

import redis

# connect redis server
redis_server = redis.Redis(host="localhost", port="6379")


def redis_check(email, json_status, valid_cnt, invalid_cnt, bad_cnt, print):
    # get value from redis cache and store to redis_email
    redis_email = redis_server.get(email)

    # find something in redis cache then store to file
    if redis_email:
        json.dump(email, json_status)
        json_status.write(":")

        # decoding used for convert byte to string
        redis_value = redis_email.decode("utf-8")

        json_status.write('"')
        json_status.write(redis_value)
        json_status.write('",\n')

        if redis_value == "Valid":
            print("%s : %s " % (email, redis_value))
            valid_cnt += 1
        elif redis_value == "Invalid":
            print("%s : %s " % (email, redis_value))
            invalid_cnt += 1
        else:
            print("%s : %s " % (email, redis_value))
            bad_cnt += 1
        return True, redis_server, valid_cnt, invalid_cnt, bad_cnt

    return False, redis_server, valid_cnt, invalid_cnt, bad_cnt
