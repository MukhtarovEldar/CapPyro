import basic

while True:
    text = input('basic >> ')
    result, error = basic.run(text)

    print(error.as_string()) if error else print(result)