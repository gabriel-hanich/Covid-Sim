def decode(pair):
    if pair[-1] != "+":
        try:
            min = int(pair[:pair.find("-")])
            max = int(pair[pair.find("-") + 1:])
        except ValueError:
            print("DECODE RECIEVED NON-INT PAIRS")
            raise ValueError
    else:
        min = int(pair[:2])
        max = min + 10
    return {"maxVal": max, "minVal":min}