import requests

import velog_config


def execute_graphql_query(query, variables):
    data = {'query': query, 'variables': variables}
    response = requests.post(url=velog_config.velog_url, headers=velog_config.headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("GraphQL 요청 실패: {}".format(response.text))
