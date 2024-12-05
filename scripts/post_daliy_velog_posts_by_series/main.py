import os
import git
import time
from datetime import datetime, timezone

import velog_config
from execute_graphql_query import execute_graphql_query
from replace_special_characters import replace_special_characters

velog_id = os.getenv("VELOG_ID")
if not velog_id:
   raise EnvironmentError("Environment variable 'NAME' is required but not set!")
repo_path = '.'
repo = git.Repo(repo_path)

variables = {
    "username": velog_id,
    "limit": 10  # 일일 10개의 글을 가져와 체크 (필요시 증가)
}
result = execute_graphql_query(velog_config.get_posts_query, variables)
recent_posts = result['data']['posts']

filtered_posts = []
current_date = datetime.now(timezone.utc).date()  # 현재 날짜 (UTC 기준)
print(f"Today: {current_date}")

for post in recent_posts:
    released_at_date = datetime.fromisoformat(post["released_at"].replace("Z", "+00:00")).date()
    print(f"Read Post - {post['title']} ({released_at_date}) ")
    if released_at_date == current_date:
        filtered_posts.append(post)

for today_post in filtered_posts:
    posts_dir = os.path.join(repo_path, today_post['series']['name'])
    if not os.path.exists(posts_dir):
        os.makedirs(posts_dir)

    file_name = replace_special_characters(today_post['title']) + '.md'
    file_path = os.path.join(posts_dir, file_name)

    if os.path.exists(file_path):
        print(f"File already exists: {file_path}. Skipping...")
        continue

    with open(file_path, 'w', encoding='utf-8') as file:
        print(f"Writing Post {today_post['title']}")
        file.write(today_post['body'])
        file.flush()
        os.fsync(file.fileno())
        time.sleep(0.5)
        commit_message = f"[UPDATE] {today_post['title']}"
        repo.git.add(file_path)
        repo.git.commit('-m', commit_message)

repo.git.push()
