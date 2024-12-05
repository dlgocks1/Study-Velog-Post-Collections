import os
import git

import velog_config
from get_all_posts_by_username import get_all_posts
from get_series_by_username import send_graphql_query
from replace_special_characters import replace_special_characters

velog_id = os.getenv("VELOG_ID")
if not velog_id:
    raise EnvironmentError("Environment variable 'NAME' is required but not set!")
repo_path = '.'
repo = git.Repo(repo_path)

series_list = send_graphql_query(query=velog_config.get_series_query, name=velog_id)
all_posts = get_all_posts(velog_id)
filtered_posts = []

for series in series_list:
    filtered_posts = []

    # 시리즈 필터링
    for post in all_posts:
        post_series = post.get('series')
        if post_series and post_series.get('id') == series['id']:
            filtered_posts.append(post)

    # 폴더 만들기
    print(f"Add Series : [{series['name']}]")
    posts_dir = os.path.join(repo_path, series['name'])
    if not os.path.exists(posts_dir):
        os.makedirs(posts_dir)

    # 파일 쓰기
    for post in filtered_posts:
        file_name = replace_special_characters(post['title']) + '.md'
        file_path = os.path.join(posts_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(post['body'])

            commit_message = f"[UPDATE] {post['title']}"
            repo.git.add(file_path)
            repo.git.commit('-m', commit_message)

repo.git.push()
