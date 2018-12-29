import requests
import json
import base64

class GitHub(object) :
    def __init__(self, authtoken, repo) :
        self._authtoken = authtoken
        self._reposelector = repo
        self._repo_owner, self._repo_name = self._reposelector.split('/', 2)

    def get_repo_config(self):
        """Return the node id and contents of the statcom.json file for the repo.
        This uses the V4 graphql github api.

        Returns
            repo_id : (string) node id for the repo to be used in future queries for speed.
            config  : (dict) contents of the statcom.json file on the master branch.
        """

        query = """query{{  
            repository(name: "{name}", owner: "{owner}") {{ 
                id
                object(expression: "master:statcom.json") {{ id ... on Blob {{ text }} }} }} 
            }}"""

        query = query.format(name=self._repo_name, owner=self._repo_owner)
        #print(query)

        r = self._send_request('POST', 'https://api.github.com/graphql', {'query' : query})
        res = r.json()

        if 'errors' in res :
            raise ValueError(res['errors'][0]['message'])

        repo_obj = res['data']['repository']

        repo_id = repo_obj['id']

        if repo_obj['object'] is None :
            raise ValueError("config file not found")

        config = json.loads(repo_obj['object']['text'])

        return (repo_id, config)

    def add_file(self, path, message, contents) :
        """Add a file at the given path with the given contents
        Args:
            path : (string) unix style path from repository root including the filename
                (dir/dir2/filename.ext)
            message: (string) commit message
            contents: (string) contents for the file. It will be written as-is.
        Returns:
            True if success.
        """
        url = "https://api.github.com/repos/{owner}/{name}/contents/{path}"
        url = url.format(owner=self._repo_owner, name=self._repo_name, path=path)

        print(url)

        b64contents = base64.b64encode(bytes(contents, "utf-8")).decode("utf-8")
        print(b64contents)

        r = self._send_request('PUT', url, { "message" : message, "content" : b64contents })

        retval = r.status_code == 201
        if not retval :
            print("error : " + r.content)
        
        return retval

    def _send_request(self, op, url, data) :
        """package up the given data to authenticate to github"""

        header = { 'Authorization' : "bearer " + self._authtoken,
                'User-Agent' : 'mhhollomon / statcom'
                }
        req = requests.Request(op, url, json=data, headers=header).prepare()

        # maybe should break the session out and cache it.
        # later.
        with requests.Session() as s :
            resp = s.send(req)

        return resp
