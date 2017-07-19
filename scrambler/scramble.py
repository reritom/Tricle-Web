def scrambler():
    pass

def scrambler2(mode, key1, key2, key3, original):
    import os, time, random, sys
    from PIL import Image
    import numpy as np
    import matplotlib.pyplot as plt

    keys = [key1, key2, key3]
    seeds = list()

    gridSize = 5
    xNum = ""
    yNum = ""

    orig = ""
    proc = ""
    ret = ""
    final = ""

    colx = ""
    rowy = ""

    encodeArray = ["","",""]

    orig = np.array(original)
    proc = np.copy(orig)
    ret = np.copy(orig)

    #original.close()

    colx = orig.shape[0]
    rowy = orig.shape[1]

    '''Seedgen'''
    for i in range(3):
        onekey = keys[i]
        uniKey = list()
        uniVal = len(onekey)
        count = 0
        for i in range(len(onekey)):
            uniKey.append(ord(onekey[i]))

            if count%2 == 0:
                uniVal = uniVal * uniKey[i]
            else:
                uniVal = uniVal / uniKey[i]

        seed = str((uniKey[0] + uniKey[len(uniKey) - 1]))
        seed = seed + str(uniVal) + str(len(onekey))

        seeds.append(seed)

    '''Create encoding arrays from the seeds'''
    encodeArray[0] = list(range(0,colx))
    encodeArray[1] = list(range(0,rowy))

    xNum = int((colx - colx%gridSize)/gridSize)
    yNum = int((rowy - rowy%gridSize)/gridSize)

    encodeArray[2] = list(range(0,xNum*yNum))

    random.Random(seeds[0]).shuffle(encodeArray[0])
    random.Random(seeds[1]).shuffle(encodeArray[1])
    random.Random(seeds[2]).shuffle(encodeArray[2])

    if mode == 'Scramble':
        '''Scramble'''
        for x in range(colx):
            for y in range(rowy):
                proc[x][y] = orig[encodeArray[0][x]][encodeArray[1][y]]

        proc2 = np.copy(proc)
        ind = 0
        for x in range(xNum):
            for y in range(yNum):
                blue = encodeArray[2][ind]
                xEn = blue%xNum
                yEn = int((blue - xEn)/xNum)

                proc2[x*gridSize:x*gridSize+gridSize,y*gridSize:y*gridSize+gridSize,:] = proc[xEn*gridSize:xEn*gridSize+gridSize,yEn*gridSize:yEn*gridSize+gridSize,:]

                ind = ind + 1

        return Image.fromarray(proc2)

    elif mode == 'Unscramble':
        '''Uses the keys to unscramble the image'''

        ind = 0
        for x in range(xNum):
            for y in range(yNum):
                blue = encodeArray[2][ind]
                xEn = blue%xNum
                yEn = int((blue - xEn)/xNum)

                ret[xEn*gridSize:xEn*gridSize+gridSize,yEn*gridSize:yEn*gridSize+gridSize,:] = proc[x*gridSize:x*gridSize+gridSize,y*gridSize:y*gridSize+gridSize,:]

                ind = ind + 1

        ret2 = np.copy(ret)

        for x in range(colx):
            for y in range(rowy):
                ret2[encodeArray[0][x]][encodeArray[1][y]] = ret[x][y]

        return Image.fromarray(ret2)

    else:
        return False
