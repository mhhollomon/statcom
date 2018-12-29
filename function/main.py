import sys
import flask
import requests
import json
import github

class CONFIG :
    TOKEN = "b14b17358ce7757b623988289a240a8043a42023"

def validate_json(json) :
    if not json :
        raise ValueError("Could not create object from json")

    for key in ('repo', 'page_id') :
        if key not in json :
            raise ValueError("Missing key " + key)

#    key = 'commitMessage'
#    if key not in json :
#        json[key] = "statcom data file"
#
#    key = 'subdir'
#    if key not in json :
#        json[key] = "statcom data file"

    return True

def hello_content(request):
    """ Responds to an HTTP request using data from the request body parsed
    according to the "content-type" header.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """
    content_type = request.headers['content-type']
    if content_type != 'application/json':
        raise ValueError("Unknown content type: {}".format(content_type))

    request_json = request.get_json(silent=True)

    validate_json(request_json)

    comment_repo = request_json['repo']

    github_obj = github.GitHub(CONFIG.TOKEN, comment_repo)

    repo_id, config = github_obj.get_repo_config()

    #print( config)

    return (json.dumps(config), { 'content-type' : 'application/json' });


def hello_error_1(request):
    # [START functions_helloworld_error]
    # This WILL be reported to Stackdriver Error
    # Reporting, and WILL NOT show up in logs or
    # terminate the function.
    from google.cloud import error_reporting
    client = error_reporting.Client()

    try:
        raise RuntimeError('I failed you')
    except RuntimeError:
        client.report_exception()

    # This WILL be reported to Stackdriver Error Reporting,
    # and WILL terminate the function
    raise RuntimeError('I failed you')

    # [END functions_helloworld_error]


def hello_error_2(request):
    # [START functions_helloworld_error]
    # WILL NOT be reported to Stackdriver Error Reporting, but will show up
    # in logs
    import logging
    print(RuntimeError('I failed you (print to stdout)'))
    logging.warn(RuntimeError('I failed you (logging.warn)'))
    logging.error(RuntimeError('I failed you (logging.error)'))
    sys.stderr.write('I failed you (sys.stderr.write)\n')

    # This WILL be reported to Stackdriver Error Reporting
    from flask import abort
    return abort(500)
    # [END functions_helloworld_error]
