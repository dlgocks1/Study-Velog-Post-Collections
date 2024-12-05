import time
import velog_config
from execute_graphql_query import execute_graphql_query


def get_all_posts(username):
    cursor = ""
    all_posts = []
    limit = 50

    while True:
        variables = {
            "username": username,
            "cursor": cursor,
            "limit": limit
        }
        result = execute_graphql_query(velog_config.get_posts_query, variables)
        posts = result['data']['posts']
        all_posts.extend(posts)

        if len(posts) < limit:
            break
        else:
            cursor = posts[-1]['id']  # 이전 결과의 커서 값으로 다음 페이지를 가져옴
        time.sleep(10)

    return all_posts
