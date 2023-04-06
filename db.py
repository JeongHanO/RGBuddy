from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbjungle

collection = db['restaurants']

# 레스토랑 리스트를 MongoDB에 저장
restaurants = [
    "코뮨173",
    "배곧곰탕",
    "이모네삼시세끼",
    "강신옥반찬",
    "장호덕손만두",
    "애플꼬마김밥",
    "밥퍼스 배곧점",
    "하루비어",
    "화덕",
    "브런치빈",
    "뜰애",
    "인더비엣",
    "스시 유우히",
    "훈이네솥뚜껑삼겹",
    "히츠지야",
    "맥도날드",
    "버거킹",
    "비비큐치킨"
]

# 레스토랑 리스트를 MongoDB에 저장
collection.insert_many([{"name": r} for r in restaurants])