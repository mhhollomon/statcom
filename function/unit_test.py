import unittest
import json
from unittest.mock import Mock
from time import strftime

import main
import github as g

class TestGitHub(unittest.TestCase) :
    def test_bad_name_format(self):

        with self.assertRaisesRegex(ValueError, 'not enough values to unpack') :
            obj = g.GitHub(main.CONFIG.TOKEN, "blogcomments-test")

    def test_wrong_name(self):
        obj = g.GitHub(main.CONFIG.TOKEN, "mhhollomon/blxxxst")

        with self.assertRaisesRegex(ValueError, 'Could not resolve to a Repository ') :
            retval = obj.get_repo_config()

    def test_no_config(self):
        obj = g.GitHub(main.CONFIG.TOKEN, "mhhollomon/yalr")

        with self.assertRaisesRegex(ValueError, 'config file not found') :
            retval = obj.get_repo_config()

    def test_get_config(self):
        obj = g.GitHub(main.CONFIG.TOKEN, "mhhollomon/blogcomments-test")

        retval = obj.get_repo_config()

        self.assertEqual(len(retval), 2)
        config_data = retval[1]

        self.assertIn( 'commitMessage', config_data)

    def test_add_file(self) :
        obj = g.GitHub(main.CONFIG.TOKEN, "mhhollomon/blogcomments-test")

        timestamp = strftime("%Y%m%d_%H%M%S")
        contents = "This is a test file at " + timestamp
        path = "_testfiles/comments/test/test_" + timestamp + ".txt"

        self.assertTrue(obj.add_file(path, "Test message", contents))


class TestMain(unittest.TestCase) :
    def test_json_none(self) :
        with self.assertRaises(ValueError) :
            main.validate_json(None)

    def test_json_missing_key(self) :
        with self.assertRaises(ValueError):
            main.validate_json({"repo" : "x/y"})

    def test_json_okay(self) :
        self.assertTrue(main.validate_json({"repo" : "x/y", "page_id" : "xyz"}))

class TestEntryPoint(unittest.TestCase) :
    def setUp(self) :
        self.headers = {'content-type' : 'application/json'}

    def test_entry_point(self) :
        repo = 'mhhollomon/blogcomments-test'
        data = {'repo' : repo, 'page_id' : 'x345y'}
        req = Mock(get_json=Mock(return_value=data), headers=self.headers, args=data)

        retval = main.hello_content(req)

        config_data = json.loads(retval[0])

        self.assertIn( 'commitMessage', config_data)

