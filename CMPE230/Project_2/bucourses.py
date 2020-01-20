#!/usr/bin/env python3
# Implemented by Olcayto Türker and Sertay Akpinar, 28.04.2019 ®
import sys
import pandas as pd

##Lists consists of long names and the abbreviatons of the all courses
programs = ['MANAGEMENT', 'ASIAN+STUDIES', 'ASIAN+STUDIES+WITH+THESIS', 'ATATURK+INSTITUTE+FOR+MODERN+TURKISH+HISTORY', 'AUTOMOTIVE+ENGINEERING', 'MOLECULAR+BIOLOGY+%26+GENETICS', 'BUSINESS+INFORMATION+SYSTEMS', 'BIOMEDICAL+ENGINEERING', 'CRITICAL+AND+CULTURAL+STUDIES', 'CIVIL+ENGINEERING', 'CONSTRUCTION+ENGINEERING+AND+MANAGEMENT', 'COMPUTER+EDUCATION+%26+EDUCATIONAL+TECHNOLOGY', 'EDUCATIONAL+TECHNOLOGY', 'CHEMICAL+ENGINEERING', 'CHEMISTRY', 'COMPUTER+ENGINEERING', 'COGNITIVE+SCIENCE', 'COMPUTATIONAL+SCIENCE+%26+ENGINEERING', 'ECONOMICS', 'EDUCATIONAL+SCIENCES', 'ELECTRICAL+%26+ELECTRONICS+ENGINEERING', 'ECONOMICS+AND+FINANCE', 'ENVIRONMENTAL+SCIENCES', 'ENVIRONMENTAL+TECHNOLOGY', 'EARTHQUAKE+ENGINEERING', 'ENGINEERING+AND+TECHNOLOGY+MANAGEMENT', 'FINANCIAL+ENGINEERING', 'FOREIGN+LANGUAGE+EDUCATION', 'GEODESY', 'GEOPHYSICS', 'GUIDANCE+%26+PSYCHOLOGICAL+COUNSELING', 'HISTORY', 'HUMANITIES+COURSES+COORDINATOR', 'INDUSTRIAL+ENGINEERING', 'INTERNATIONAL+COMPETITION+AND+TRADE', 'CONFERENCE+INTERPRETING', 'INTERNATIONAL+TRADE', 'INTERNATIONAL+TRADE+MANAGEMENT', 'LINGUISTICS', 'WESTERN+LANGUAGES+%26+LITERATURES', 'LEARNING+SCIENCES', 'MATHEMATICS', 'MECHANICAL+ENGINEERING', 'MECHATRONICS+ENGINEERING', 'INTERNATIONAL+RELATIONS%3aTURKEY%2cEUROPE+AND+THE+MIDDLE+EAST', 'INTERNATIONAL+RELATIONS%3aTURKEY%2cEUROPE+AND+THE+MIDDLE+EAST+WITH+THESIS', 'MANAGEMENT+INFORMATION+SYSTEMS', 'FINE+ARTS', 'PHYSICAL+EDUCATION', 'PHILOSOPHY', 'PHYSICS', 'POLITICAL+SCIENCE%26INTERNATIONAL+RELATIONS', 'PRIMARY+EDUCATION', 'PSYCHOLOGY', 'MATHEMATICS+AND+SCIENCE+EDUCATION', 'SECONDARY+SCHOOL+SCIENCE+AND+MATHEMATICS+EDUCATION', 'SYSTEMS+%26+CONTROL+ENGINEERING', 'SOCIOLOGY', 'SOCIAL+POLICY+WITH+THESIS', 'SOFTWARE+ENGINEERING', 'SSOFTWARE+ENGINEERING+WITH+THESIS', 'TURKISH+COURSES+COORDINATOR', 'TURKISH+LANGUAGE+%26+LITERATURE', 'TRANSLATION+AND+INTERPRETING+STUDIES', 'SUSTAINABLE+TOURISM+MANAGEMENT', 'TOURISM+ADMINISTRATION', 'TRANSLATION', 'EXECUTIVE+MBA', 'SCHOOL+OF+FOREIGN+LANGUAGES']
departments = ['AD', 'ASIA', 'ASIA', 'ATA', 'AUTO', 'BIO', 'BIS', 'BM', 'CCS', 'CE', 'CEM', 'CET', 'CET', 'CHE', 'CHEM', 'CMPE', 'COGS', 'CSE', 'EC', 'ED', 'EE', 'EF', 'ENV', 'ENVT', 'EQE', 'ETM', 'FE', 'FLED', 'GED', 'GPH', 'GUID', 'HIST', 'HUM', 'IE', 'INCT', 'INT', 'INTT', 'INTT', 'LING', 'LL', 'LS', 'MATH', 'ME', 'MECA', 'MIR', 'MIR', 'MIS', 'PA', 'PE', 'PHIL', 'PHYS', 'POLS', 'PRED', 'PSY', 'SCED', 'SCED', 'SCO', 'SOC', 'SPL', 'SWE', 'SWE', 'TK', 'TKL', 'TR', 'TRM', 'TRM', 'WTR', 'XMBA', 'YADYOK']

##Func opening url according to lists above and collects course names, course codes and instructors in different lists of one term
def func(y1, y2, d1):
  try:
    #reads html and creates multidimensional array according to the parameters y1, y2, d1 by taking required department names and abbreviations
    dfs = pd.read_html('http://registration.boun.edu.tr/scripts/sch.asp?donem=' + str(y1) + '/' + str(y2) + '-' + str(d1) + '&kisaadi=' + departments[s] + '&bolum=' + programs[s])

    U = 0   #No. of undergraduate courses in that term
    G = 0   #No. of graduate courses in that term

    courseName = []
    courseCode = []
    instructors = []

    #dfs[3][2][x] represents course names in registration table and course names are appended to courseNames list in this loop by checking every row of the table
    for x in range(len(dfs[3][2])):
        if dfs[3][2][x] != 'LAB' and dfs[3][2][x] != 'P.S.' and dfs[3][2][x] != 'Name':
            courseName.append(dfs[3][2][x])

    #dfs[3][0][x] represents course codes in registration table and course codes are appended to courseCodes list in this loop by checking every row of the table
    for x in range(len(dfs[3][0])):
        if dfs[3][0][x] != 'Code.Sec' and dfs[3][5][x] != 'STAFF' and dfs[3][5][x] != 'STAFF STAFF' and dfs[3][2][x] != 'LAB' and dfs[3][2][x] != 'P.S.':
            code = str(dfs[3][0][x])
            courseCode.append(code[:-3])    #To delete section names in a course code in the registration system

    #dfs[3][5][x] represents instuctors in registration table and course codes are appended to instructors list in this loop by checking every row of the table
    for x in range(len(dfs[3][5])):
        if dfs[3][5][x] != 'STAFF' and dfs[3][5][x] != 'STAFF STAFF' and dfs[3][5][x] != 'Instr.' and dfs[3][2][x] != 'LAB' and dfs[3][2][x] != 'P.S.':
            instructors.append(dfs[3][5][x])

    #These fors appends all course codes, course names and instructors in that term to seperately to different lists containing all course codes, course names and instructors
    for x in courseCode:
        allcourses.append(x)

    for x in courseName:
        allnames.append(x)

    for x in instructors:
        allinstructors.append(x)

    #Converts this list to a set of course codes
    courseCode = list(dict.fromkeys(courseCode))

    #Takes all courses one by one and checks if it's an undergraduate course and updates U or G
    for x in courseCode:

      #c = float(x[-6])
      try:
        if float(x[-6]) < 5:
            U = U + 1
        else:
            G = G + 1
      except:               #If course code is not in generally used form U is incremented
          U = U + 1
    courseName = list(dict.fromkeys(courseName))
    termcourses.append((courseCode))    #A list of lists containing all course codes in that term
    instructors = list(dict.fromkeys(instructors))  #A set containg all instructors in that term
    I = len(instructors)
    allUG.append(U)
    allG.append(G)
    allI.append(I)

  except:
      print("")




for s in range(len(programs)):


    allcourses= [] #A list of all courses
    termcourses= [] #A list of list of courses according to the term
    allnames = []   #All course names
    allinstructors=[]   #All instructors
    allUG=[]    #A list containing U numbers for each year
    allG=[]     #A list containing G numbers for each year
    allI=[]     #A list containing I numbers for each year
    bastır=[]   #For printing the first line for a department

    bastır.append(departments[s])

    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    y1 = int(arg1[:4])    #start year according to argument
    y2 = int(arg2[:4])    #end year according to argument
    D1 = arg1[5:]         #starting semester
    D2 = arg2[5:]         #ending semester

    #changes D1 and D2 according to term name
    if D1 == 'Fall':
        D1 = 1
    elif D1 == 'Spring':
        D1 = 2
    else:
        D1 = 3

    if D2 == 'Fall':
        D2 = 1
    elif D1 == 'Spring':
        D2 = 2
    else:
        D2 = 3
    i=0

    #Calls the func function according to start semester and after all calls for the func checks if it's the last term by comparing values with D2 and y2
    if D1==1:
     while i==0:

        if D1==1:

         func(y1, y1 + 1, D1)
         if D2==1 and y1==y2:   #Check if it ends or not
             break

        elif D1==2:

         func(y1, y1+1, D1)
         if D2==2 and y1==y2-1:
             break

        else:

         func(y1, y1+1, D1)
         y1=y1+1                #increments the year if summer term is called
         if D2==3 and y1-1==y2-1:   #checks the last term is called or not
             break


        D1 = D1+1
        if D1>3:
         D1 = 1


    elif D1==2:
     while i == 0:
      if D1==2:

        func(y1-1, y1, D1)
        if D2==2 and y1-1==y2-1:
          break

      elif D1==3:

         func(y1-1, y1, D1)
         y1=y1+1
         if D2 == 3 and y1 - 2 == y2 - 1:
             break


      elif D1==1:

        func(y1-1, y1, D1)
        if D2==1 and y1-1==y2:
          break

      D1=D1+1
      if D1>3:
        D1=1


    else:

      while i==0:

        if D1==3:

         func(y1-1, y1, D1)
         y1=y1+1
         if D2==3 and y1-2==y2-1:
             break

        elif D1==1:

         func(y1-1, y1, D1)
         if D2==1 and y1-1==y2:
             break


        else:

          func(y1-1, y1, D1)
          if D2==2 and y1-1==y2-1:
              break


        D1=D1+1
        if D1>3:
            D1=1




    allcourses = list(dict.fromkeys(allcourses))
    allnames = list(dict.fromkeys(allnames))
    U=0
    G=0

    #Decide no. of U and G for all departments
    for x in allcourses:


        try:
            if float(x[-6]) < 5:
                U = U + 1
            else:
                G = G + 1
        except:
            U = U + 1


    allinstructors = list(dict.fromkeys(allinstructors))
    I = len(allinstructors)

    #A list for printing the department name, U's and G's and total offerings
    bastır.append(str(U) + ' ' + str(G))
    bastır.append("")
    TU=0
    TG=0

    #For printing the first line
    for i in range(len(allG)):

        bastır.append( str(allUG[i]) +  ' ' + str(allG[i]) + ' ' + str(allI[i]))
        TU = TU+allUG[i]
        TG = TG + allG[i]

    bastır.append(str(TU) + " " + str(TG) + " " + str(I))

    bas=''
    for i in bastır:
         bas= bas +',' +str(i)


    print(bas)

    #For printing each course in each department
    for i in range(len(allcourses)):
        inst= []
        num1=0
        try:
         strList = [allcourses[i], allnames[i]]
        except IndexError:
         allnames.append(allnames[len(allnames)-1])
         strList = [allcourses[i], allnames[i]]

        for term in termcourses:

            for course2 in term:

                if allcourses[i] == course2:
                    try:
                     inst.append(allinstructors[i])
                     strList.append('X')
                     num1=num1+1
                     break
                    except:
                     allinstructors.append(allinstructors[len(allinstructors)-1])
                     inst.append(allinstructors[i])
                     strList.append('X')
                     num1 = num1 + 1

            if allcourses[i] not in term:
                strList.append(' ')

        inst = list(dict.fromkeys(inst))
        num2= len(inst)
        strList.append(str(num1) +  "/" + str(num2))


        bas=''
        for i in strList:
         bas= bas +',' +str(i)

        print(bas)

