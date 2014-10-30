===============
Starting Mongo
===============

This will generate the commands you need::

    print("rm -Rf /ramdisk/*")
    print("mkdir -p /ramdisk/configdb")
    print("sudo numactl --interleave=all mongod --configsvr --dbpath /ramdisk/configdb --port 27019 &")
    print('sleep 10')
    print("sudo numactl --interleave=all mongos --configdb 127.0.0.1:27019 &")
    print('sleep 5')
    n = 6
    i0 = 17

    mongo_commands = []

    for i in range(i0 - n, i0):
        print("mkdir -p /ramdisk/db%d" % i)
        print("sudo numactl --interleave=all mongod --dbpath /ramdisk/db%d --port 270%02d&" % (i,
                                                                                              i))
        print("sleep 1")


        mongo_commands.append('sh.addShard( "127.0.0.1:270%02d" )' % i)


    print('')
    for mc in mongo_commands:
        print(mc)

    print('sh.enableSharding("input")')
    print('sh.shardCollection("input.dataset", { "_id": "hashed" } )')
