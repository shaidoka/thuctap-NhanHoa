try:
    print("10"+10)
except IOError:
    print("Input/Output Error")
except TypeError:
    print("Data types Error")
except:
    print("Hey you got an error")
finally:
    print("Finally always run whether there is error or not")