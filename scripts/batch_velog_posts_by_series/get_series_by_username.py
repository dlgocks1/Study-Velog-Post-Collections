from execute_graphql_query import execute_graphql_query


def send_graphql_query(query, name):
    get_series_variables = {
        "username": name
    }
    response = execute_graphql_query(query=query, variables=get_series_variables)
    return response['data']['user']['series_list']
