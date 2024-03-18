import requests
from time import time
from bs4 import BeautifulSoup
# import pandas as pd
from collections import defaultdict
import asyncio
term = "202401"  # spring24


def getDepts():
    data = []
    page = requests.get("https://app.testudo.umd.edu/soc/")
    soup = BeautifulSoup(page.content, 'html.parser')

    for div in soup.find_all("div", class_="course-prefix row"):
        abbrv = div.find('span', class_='prefix-abbrev').text
        data.append({"dept": abbrv, "courses": []})
    return data


async def agetClasses(e, courses):
    classes = []
    url = f"https://app.testudo.umd.edu/soc/{term}/{e['dept']}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    for div in soup.find_all('div', class_='course-id'):
        classname = div.text
        classes.append(classname)
        courses[classname] = {}
    e['courses'] = classes


async def classNames():
    data = getDepts()
    courses = defaultdict(dict)
    tasks = []
    for e in data:
        t = asyncio.create_task(agetClasses(e, courses))
        tasks.append(t)
    await asyncio.gather(*tasks)
    await aSectionsRequests(courses, term)
    return data, courses


# i am assuming the term is all the same
async def aSectionsRequests(courses, term):
    url = f"https://app.testudo.umd.edu/soc/{term}/sections?"
    tasks = [] 
    rstrings = []
    courseList = []
    for c in courses:
        rstrings.append(f'&courseIds={c}')
        courseList.append(c)
    start = 0
    for end in range(300, len(rstrings), 300):
        url2 = url + "".join(rstrings[start:end])
        t = asyncio.create_task(aSections(courses, url2, courseList[start:end]))
        tasks.append(t)
        start = end
    await asyncio.gather(*tasks)


async def aSections(courses, url, courseList):
    page = requests.get(url) 
    soup = BeautifulSoup(page.content, 'html.parser')
    for c in courseList: 
        sections_percourse = []
        for course in soup.find_all('div', id=c):
            # if not course:
            #     print("first loop failed for", c)
            # print("this is not working")
            # print(course)
            # for sections in course.find_all('div', has_section_class=True):
            for sections in course.find_all('div', class_="section"):
                # if not sections:
                #     print("second loop failed", c)
                instructor = sections.find('span', class_= "section-instructor").text
                total_seats =  sections.find('span', class_="total-seats-count").text
                open_seats = sections.find('span', class_="open-seats-count").text
                waitlist = sections.find('span', class_="waitlist-count").text 
                possible = sections.find('div', class_='class-days-container')
                secs = {}
                if possible:
                    # print("possible failed for ",c)
                    for slot in possible.find_all('div', class_="row"):
                        start_time = slot.find('span', class_="class-start-time")
                        if start_time:
                            start_time = start_time.text

                        end_time = slot.find('span', class_="class-end-time")
                        if end_time:
                            end_time = end_time.text

                        building = slot.find('span', class_="building-code")
                        if building:
                            building = building.text

                        classroom = slot.find('span', class_="class-room")
                        if classroom:
                            classroom = classroom.text

                        days = slot.find('span', class_="section-days")
                        if days:
                            days = days.text

                        flag = slot.find("span", class_='class-type')
                        if not flag:
                            class_type = "Lecture"
                        else:
                            class_type = flag.text
                        secs = {
                            "start_time": start_time,
                            "end_time": end_time,
                            "building": building,
                            "days": days,
                            "class type": class_type,
                            "classroom": classroom,
                        }
                    item = {
                        "instructors": instructor,
                        "total_seats": total_seats,
                        "open_seats": open_seats,
                        "waitlist": waitlist,
                        "sections": secs
                    }
                    sections_percourse.append(item)
                    # print(item)
                else:
                    print(sections)
        courses[c]["sections"] = sections_percourse


def run():
    start_time = time()
    res = asyncio.run(classNames())
    elapsed_time = (time() - start_time) / 60
    print(elapsed_time)
    return {"depts": res[0], "courses": res[1], "runtime": elapsed_time}


if __name__ == "__main__":
    start_time = time()
    res = asyncio.run(classNames())
    print("data", res[0])
    print("courses", res[1])
    elapsed_time = (time() - start_time) / 60
    print(elapsed_time)
