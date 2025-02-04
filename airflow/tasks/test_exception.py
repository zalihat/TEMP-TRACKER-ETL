def test_except():
    try:
        x = 1/0
        print('this is the try block')
        return x
    except:
        print('this is the except block')
x = test_except()