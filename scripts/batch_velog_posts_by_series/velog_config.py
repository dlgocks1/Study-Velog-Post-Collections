headers = {'Content-Type': 'application/json'}
velog_url = "https://v2.velog.io/graphql"

get_posts_query = """
query Posts($cursor: ID, $username: String, $limit: Int) {
  posts(cursor: $cursor, username: $username, limit: $limit) {
    id
    title
    body
    series {
        id
    }
  }
}
"""

get_series_query = '''
    query UserSeriesList($username: String!) {
      user(username: $username) {
        id
        series_list {
          id
          name
          description
          url_slug
          thumbnail
          updated_at
          posts_count
          __typename
        }
        __typename
      }
    }
'''