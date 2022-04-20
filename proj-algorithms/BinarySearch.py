
def binary_search(container, item, left, right):
    # first base case - search misses
    if right <= left:
        return -1

    # generate the index of the middle item
    middle_index = (left + right) // 2

    # We have found the item
    if container[middle_index] == item:
        return middle_index 
    
    # We have to check whether the middle_item is smaller or greater
    
    # The item is in the left sub-array
    elif container[middle_index] > item:
        print('Checking items on the left...')
        # We can discard the right side of the array (items greater than the middle item)
        return binary_search(container, item, left, middle_index - 1)
    
    # The item is in the right sub-array
    elif container[middle_index] < item:
        print('Checking items on the right...')
        return binary_search(container, item, middle_index + 1, right)
    

if __name__ == '__main__':
    nums = [3,1,-5,10, 15, 18, 29, 45]
    print(binary_search(container= sorted(nums), item = 33, left=0, right= len(nums)))