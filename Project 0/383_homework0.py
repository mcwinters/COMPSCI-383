#
# COMPSCI 383 Homework 0
#
# Fill in the missing bodies of the functions as specified by the comments and docstrings.
#
# If you execute this file, the main() function below will test your implementations.  You can 
# compare your results to the answers in the comments.
# v2


# Exercise 1 (6 points)
def max_unique(lst):
    """Returns the largest element of a list that appears only once"""
    temp = []  # intitialize temp array
    for i in lst:  # iterate through input array
        if lst.count(i) == 1:  # if the current number only appears once
            temp.append(i)  # add current number to temp array
    return max(temp)  # return largest element in temp array

# Exercise 2 (6 points)
def splice_em(list_one, list_two):
    """Splice two equal-length lists together.
    
    Returns a list with alternating elements from the two lists given as arguments.  For example:
    splice_em(['a', 'b', 'c'], [1, 2, 3]) should return the list ['a', 1, 'b', 2, 'c', 3]
    
    Hint: you'll probably want to use a for or while loop to iterate.  The enumerate() and/or zip() 
    built-in functions might be helpful here: https://docs.python.org/3/library/functions.html    
    """
    #
    # fill in function body here
    #
    zipList = zip(list_one, list_two)   # aggregate elements from both lists together to make one iterable
    result = []                         # initialize spliced array
    for i, j in zipList:                # iterate over aggregated array
        result.append(i)
        result.append(j)

    return result  # fix this line!


# Exercise 3 (8 points)
def reverse_dict_list(d):
    """Reverse a dictionary that maps keys to lists of values.
    
    Given a dictionary that maps each key k1, k2, etc. to a list of values v1, v2, ..., create a 
    new dictionary keyd by v1, v2, mapping them to lists k1, k2, etc.  
    For example, reverse_dict_list({'a':[1, 2, 3], 'b':[1, 3, 5, 7], 'c':[4, 5, 6]}) should return 
    the dictionary {1:['a', 'b'], 2:['a'], 3:['a', 'b'], 5:['b', 'c'], 7:['b'], 4:['c'], 6:['c']}
    """
    newDict = {}  # intitialize new dictionary
    for i in d.values():  # iterate through values of dictionary (will be lists)
        for j in i:  # iterate through said lists to get individual elements
            for key,value in d.items():  # iterate through all pairs 
                if j in value:  # if current element is paired with current key
                    if j not in newDict:  # if we have not yet added element to new dictionary
                        newDict[j] = [key]  # add current element to new dictionary as a key, and its old key as its value
                    elif key not in newDict[j]:  # element is already in dictionary and we have not yet added current key
                        newDict[j].append(key)  # add on current key
    return newDict  # return new dictionary


# Exercise 4 (8 points)
def char_counts(some_text):
    """Return a dictionary containing each character in the text as keys, and the number of times
    they occur as values.
    Hint: recall that since a string is a sequence, you can loop through it as you would a list.
    For help with dictionaries, see the Python docs: 
    https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
    """
    newDict = {}  # initialize new dictionary
    for i in set(some_text):  # iterate through each char in input string without repeats
        newDict[i] = some_text.count(i)  # add each char to dictionary with its frequency as its value
    return newDict  # return dictionary


# Exercise 5 (10 points)
def rewrap(txt, c):
    """Wrap a string to a specified number of characters per line.
    Given a text string, eliminate any newline characters an insert new ones such that no word is 
    broken up and no line is longer than c characters (unless it consists of word whose length is
    greater than c).  Any number of whitespace characters in the input should be condensed into a
    single space.  Punctuation should be treated as a normal character, and not separated from
    words.
    For example, if s="Experience is simply the name we give our mistakes.", rewrap(s, 30) yields:
        Experience is simply the name
        we give our mistakes.
    While rewrap(s, 10) gives: 
        Experience
        is simply
        the name
        we give
        our
        mistakes.
    """
    txtlst = txt.split()   #parse only words and punctuation from txt
    i = 0
    strOut = ""            # initialize rewrapped string to be returned
    cleft = c              # counter for how many more chars allowed on current line

    while i <= len(txtlst)-1:
        if cleft == c and len(txtlst[i]) > c:   # if current word len is longer than allowed length
            strOut += txtlst[i]
            strOut += '\n'
        elif len(txtlst[i]) > cleft:      # if not enough chars left for next word in txt
            strOut += '\n'
            i -= 1              # after newline run with same index again to attach current word
            cleft = c
        else:
            # case where current word is a valid length
            strOut += txtlst[i]
            if i != len(txtlst)-1 and cleft != len(txtlst[i]):
                strOut += " "               # only add space if word is not EOL or is not last word in txt
            cleft -= (1+len(txtlst[i]))
        i += 1
        
    return strOut


# Exercise 6 (10 points)
def is_monotonicish(lst):
    """Return True if list of numbers is "mostly monotonic", False otherwise.
    In "mostly increasing" lists of numbers, the difference between each entry and the one before
    it is no less than -1.  That is, [1, 3, 5, 7] and [1, 3, 2, 3] are "mostly increasing", while
    [1, 3, 1, 5] is not.  A "mostly decreasing" list is defined simlarly, with each successive 
    being no more than one greater than the preceeding.  A "mostly monotonic" sequence of numbers
    is either mostly increasing or mostly decreasing. 
    """
    a = True  # intiialize a to check if list is mostly decreasing
    b = True  # intitialize b to check if list is mostly increasing
    for i in range(len(lst) - 1):  # iterate through list
        if (lst[i+1] - lst[i]) > 1:  # if the difference between current and next number is greater than 1
            a = False  # list is not mostly decreasing
        if (lst[i+1] - lst[i]) < -1:  # if the difference between current and next number is less than -1
            b = False  # list is not mostly increasing
    return a or b  # return True if list is either mostly increasing or mostly decreasing


# Exercise 7 (2 points +10 extra credit)
def moxie_combos(n):
    """Return a list of tuples describing all possible ways to deliver the world's best soda.
    Moxie can be packaged in single cans, six-packs of cans, or cases of 24 cans.  For example, 
    42 Moxies could be delivered in 1 case, 1 six-pack, and twelve singles, or 1 case, 3 six-packs,
    and 0 singles, or 0 cases, 2 six-packs, and 30 singles, etc.  
    For a given n, moxie_combos(n) returns a list of tuples that describe all possible ways to 
    group n cans into cases, six-packs, and singles.  It returns a list of unique three-element 
    tuples, each describing the number of cases, six-packs, and singles in that particular 
    combination.  For example, moxie_combos(19) should return the list:
    [ (0, 0, 19), (0, 3, 1), (0, 2, 7), (0, 1, 13) ]
    (Note that the order of the list does not matter.)
    Hint: you may want to consider a recursive solution --- given a valid solution for n-1, how
    can you create the solution for n?  
    """
    
    ans = []  # initialize return array

    ### function to create arrays of all combinations
    
    sizes = [24,6,1]  # initialize array to store amount of cans per size
    
    def combinations(n, sizes):  # helper method to create array of subarrays with all combinations
        if n < 0:  # if inputted target < 0, return blank array
            return []
        if n == 0:  # if inputted target == 0, return array with empy subarray
            return [[]]
        all_combinations = []  # initialize array of subarrays with all combinations

        for size in sizes:  # iterate through all possible sizes (24,6,1)
            combos = combinations(n - size, sizes)  # recursive call to combinations funtion with new total
            for combo in combos:  # iterate through new combinations
                combo.append(size)  # fill subarray with current size
                all_combinations.append(combo)  # append subarray to array

        return all_combinations  # return array of subarrays with all combinations

    ### function to turn this into array of tuples
    
    for i in combinations(n,sizes):  # iterate through array of subarrays with all combinations
        if (i.count(24), i.count(6), i.count(1)) not in ans:
            ans.append((i.count(24), i.count(6), i.count(1)))  # append tuple of current combo to ans array
        
    return ans

# The main() function below will be executed when your program is run.  Note that Python does not 
# require a main() function, but it is considered good style.  The comments on each line show
# what should be printed if your code is running correctly.
def main():
    print("1.", max_unique([9, 0, 1, 2, 5, 8, 6, 7, 5, 3, 0, 9]))      # 8
    print("2.", splice_em(['r', 'd', 'c', 'p'], [2, 2, 3, 0]))         # ['r', 2, 'd', 2, 'c', 3, 'p', 0]
    print("3.", reverse_dict_list({1:['h', 'e', 'y'], 2:['h', 'o']}))  # {'h': [1, 2], 'e': [1], 'y': [1], 'o': [2]}
    print("4.", char_counts("wowie zowie"))                            # {'w': 3, 'o': 2, 'i': 2, 'e': 2, ' ': 1, 'z': 1}
    print("5.", rewrap("I love writing Python code.", 6))              # "I love\nwriting\nPython\ncode." 
    print("6.", is_monotonicish([3, 5, 10, 9, 13]))                    # True
    print("7.", moxie_combos(13))                                      # [(0, 0, 13), (0, 1, 7), (0, 2, 1)]


###################################

# The lines below are a common Python idiom for creating Python programs that can be exectuted
# directly or used as a module.  For more info, see: 
# https://www.geeksforgeeks.org/what-does-the-if-__name__-__main__-do/
if __name__ == '__main__':
    main()