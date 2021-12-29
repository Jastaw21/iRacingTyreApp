LF = []
LR = []
RF = []
RR = []


def tyre_wear():
    wear_list = []
    tyre_wear_options = []
    corner_list = []
    with open('vars.txt') as f:
        vars_list = f.readlines()

    for string in vars_list:
        wear = 'wear'
        if wear in string:
            wear_list.append(string)
        else:
            pass

    for substring in wear_list:
        first_double_space = substring.find(' ')
        tyre_wear_options.append(substring[0:first_double_space])

    for item in tyre_wear_options:
        corner = item[0:2]
        if corner in corner_list:
            pass
        else:
            corner_list.append(corner)

    for i in corner_list:
        for j in tyre_wear_options:

            if j[0:2] == i:
                dictionary(i, j)
    listsl = [LF, RF, LR, RR]

    for item in listsl:
        item_name = item[0]
        two_char = item_name[0:2]
        tyre_variables = sub_dict(two_char, list(item))

    return tyre_variables


def dictionary(corner, var):
    if corner == 'LF':
        LF.append(var)
    elif corner == 'LR':
        LR.append(var)
    elif corner == 'RF':
        RF.append(var)
    elif corner == 'RR':
        RR.append(var)


sub_dictionary = {}


def sub_dict(subset, corner):
    sub_dictionary[subset] = corner
    return sub_dictionary


def driver_inputs():
    driver_inputs_options = ['Throttle', 'Brake', 'Gear', 'SteeringWheelAngle']
    return driver_inputs_options


if __name__ == '__main__':
    print(tyre_wear())
