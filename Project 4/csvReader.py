import csv

dict = {"Awesomeness":0, "Enrolled":0, "Fever":0, "Test":0, "Fever & Enrolled":0, "Fever & notEnrolled":0, "Awesome & Fever":0, "Awesome & notFever":0, 
        "Test & Fever":0, "Test & notFever":0, "Awesome & Test":0, "Awesome or Test":0, "Enrolled & Awesome":0, "Enrolled & Awesome & Test":0}

with open('383_fever_data.csv', newline = '') as csvFile:
    file = csv.reader(csvFile, delimiter=',', quotechar='|')
    for row in file:
        Awesomeness, Enrolled, Fever, Test = (row[1] == "TRUE"), (row[2] == "TRUE"), (row[3] == "TRUE"), (row[4] == "TRUE")
        
        if Enrolled: dict["Enrolled"] += 1
        if Fever: dict["Fever"] += 1
        if Awesomeness: dict["Awesomeness"] += 1
        if Test: dict["Test"] += 1
            
        if Enrolled and Fever: dict["Fever & Enrolled"] += 1
        if not Enrolled and Fever: dict["Fever & notEnrolled"] += 1
            
        if Fever and Awesomeness: dict["Awesome & Fever"] += 1
        if not Fever and Awesomeness: dict["Awesome & notFever"] += 1
            
        if Fever and Test: dict["Test & Fever"] += 1
        if not Fever and Test: dict["Test & notFever"] += 1
        
        if Awesomeness and Test: dict["Awesome & Test"] += 1
        if Awesomeness or Test: dict["Awesome or Test"] += 1
        if Awesomeness and Enrolled: dict["Enrolled & Awesome"] += 1     
        if Awesomeness and Enrolled and Test: dict["Enrolled & Awesome & Test"] += 1   

print(dict)