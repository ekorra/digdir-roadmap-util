from gql import Client, gql
# from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import RequestsHTTPTransport


def getGithubProjectNodes(authorizationToken):
    # Select your transport with a defined url endpoint
    transport = RequestsHTTPTransport(url="https://api.github.com/graphql", headers={
        'Authorization': authorizationToken}, verify=True, retries=5, timeout=60)
    # Create a GraphQL client using the defined transport
    client = Client(transport=transport,
                    fetch_schema_from_transport=False)

    hasNextPage = True
    params = {"after": ""}
    nodes = []
    query = getQuery()
    while hasNextPage:
        result = client.execute(query, variable_values=params)
        nodesToAdd = result["organization"]["projectV2"]["items"]["nodes"]
        nodes = nodes + nodesToAdd

        hasNextPage = result["organization"]["projectV2"]["items"]["pageInfo"]["hasNextPage"]
        if hasNextPage:
            params["after"] = result["organization"]["projectV2"]["items"]["pageInfo"]["endCursor"]

    return nodes


def getQuery():
    return gql("""
        query GitHubProjects($after: String = "") {
            organization(login: "digdir") {
                projectV2(number: 8) {
                __typename
                id
                title
                creator {
                    login
                }
                items(after: $after, first: 100) {
                    __typename
                    ... on ProjectV2ItemConnection {
                    pageInfo {
                        startCursor
                        endCursor
                        hasNextPage
                    }
                    }
                    totalCount
                    nodes {
                    __typename
                    id
                    content {
                        ... on Issue {
                        title
                        bodyHTML
                        number
                        url
                        state
                        trackedIssues(first:50){
                            totalCount
                            nodes {
                            state
                            }
                        }
                        } 
                        ... on DraftIssue {title}
                    }
                    fieldValues(first: 12) {
                        ...itemFields
                    }
                    }
                }
                }
            }
        }
        fragment itemFields on ProjectV2ItemFieldValueConnection {
        nodes {
            __typename
            ... on ProjectV2ItemFieldLabelValue {
            field {
                ... on ProjectV2Field {
                name
                }
            }
            labels(first:10) {totalCount nodes{name description url}}
            }
            ... on ProjectV2ItemFieldSingleSelectValue {
            field {
                ... on ProjectV2SingleSelectField {
                name
                }
            }
            name
            }
            ... on ProjectV2ItemFieldTextValue {
            field {
                ... on ProjectV2Field {
                name
                }
            }
            text
            }
            ... on ProjectV2ItemFieldNumberValue {
            field {
                ... on ProjectV2Field {
                name
                }
            }
            number
            }
            ... on ProjectV2ItemFieldDateValue {
            field {
                ... on ProjectV2Field {
                name
                }
            }
            date
            }
            ... on ProjectV2ItemFieldMilestoneValue {
            field {
                ... on ProjectV2Field {
                name
                }
            }
            milestone {title}
            }
        }
    }
    """)
