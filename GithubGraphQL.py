import asyncio
import backoff
import time
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import aiohttp


# Define backoff logic
@backoff.on_exception(
    backoff.expo,
    (aiohttp.ClientResponseError, asyncio.TimeoutError),
    max_tries=5,
    jitter=backoff.full_jitter
)
async def getGithubProjectNodesAsync(authorizationToken):

    transport = AIOHTTPTransport(
        url="https://api.github.com/graphql", headers={'Authorization': authorizationToken, 'Accept-Encoding': 'gzip'}, timeout=60)

    async with Client(transport=transport, fetch_schema_from_transport=True, execute_timeout=600) as session:
        hasNextPage = True
        params = {"after": ""}
        nodes = []
        query = getProjectFieldsQuery()

        starttime = time.perf_counter()
        while hasNextPage:
            try:
                intermediet_time1 = time.perf_counter()
                result = await session.execute(query, variable_values=params)

                nodesToAdd = result["organization"]["projectV2"]["items"]["nodes"]
                nodes = nodes + nodesToAdd

                hasNextPage = result["organization"]["projectV2"]["items"]["pageInfo"]["hasNextPage"]
                if hasNextPage:
                    params["after"] = result["organization"]["projectV2"]["items"]["pageInfo"]["endCursor"]
            except Exception as e:
                print(e)
                raise e
            finally:
                intermediet_time2 = time.perf_counter()
                print(
                    f" Real time: {intermediet_time2 - intermediet_time1:.2f} seconds")

        endtime = time.perf_counter()

        print(f" Total kjøretid: {endtime - starttime:.2f} seconds")
        return nodes


# Define backoff logic
@backoff.on_exception(
    backoff.expo,
    (aiohttp.ClientResponseError, asyncio.TimeoutError),
    max_tries=5,
    jitter=backoff.full_jitter)
async def Get_github_issue_async(authorizationToken, issue_number: int):
    query = get_issue_query(issue_number)
    params = {'issuenubmer': issue_number}
    transport = AIOHTTPTransport(
        url="https://api.github.com/graphql", headers={'Authorization': authorizationToken, 'Accept-Encoding': 'gzip'}, timeout=10)
    starttime = time.perf_counter()

    async with Client(transport=transport, fetch_schema_from_transport=False, execute_timeout=600) as session:
        try:
            result = await session.execute(query, variable_values=params)
            return result['repository']['issue']
        except Exception as e:
            print(f'issue {issue_number} failed: {e} ')
            raise e

        endtime = time.perf_counter()

        print(f" Issue {issue_number} : {endtime - starttime:.2f} seconds")


def get_github_projects(authorizationToken):
    return asyncio.run(getGithubProjectNodesAsync(authorizationToken))


def get_github_issue(authorizationToken, issue_number: int):
    return asyncio.run(Get_github_issue_async(authorizationToken, issue_number))


def getProjectFieldsQuery():
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
                            number
                            url
                            state
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


def get_issue_query(id: int):
    return gql('''
        query GithubIssue($issuenubmer: Int=4) {
            repository(owner: "digdir", name: "roadmap") {
                issue(number: $issuenubmer) {
                title
                number 
                url
                state
                trackedIssuesCount
                trackedIssues(first:50){
                    totalCount
                    nodes {
                    state
                    title
                    }
                }
                timelineItems(first: 50) {
                    nodes {
                        __typename
                        ... on ClosedEvent {
                            createdAt
                            actor {
                                login
                            }
                        }
                    }
                }
                bodyHTML
                }
            }
        } 
    ''')
