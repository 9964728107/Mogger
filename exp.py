arr1 = [1, 2, 3, 4, 5]
arr2 = [1, 2, 3, 4, 6]

result = list(map(lambda x, y: x == y, arr1, arr2))
print(result)