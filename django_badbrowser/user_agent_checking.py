import httpagentparser
from pkg_resources import parse_version


def check_user_agent(user_agent, requirements):
    """
    :param dict user_agent: The dict output from httpagentparser.detect().
    :param tuple requirements: The settings.BADBROWSER_REQUIREMENTS value.
    :rtype: bool
    :returns: True if the browser is good, False if bad.
    """

    if not user_agent:
        return True

    if not requirements:
        return True

    if type(user_agent) == getattr(httpagentparser, 'Result', dict):
        parsed = user_agent
    else:
        parsed = httpagentparser.detect(user_agent)

    if "browser" not in parsed:
        return True

    if "name" not in parsed["browser"]:
        return True

    if "version" not in parsed["browser"]:
        return True

    user_browser = parsed["browser"]["name"].lower()
    user_browser_version = parsed["browser"]["version"]

    for browser, browser_version in requirements:
        if user_browser == browser.lower():
            if not browser_version:
                return False
            if parse_version(browser_version) <= parse_version(user_browser_version):
                return True
            else:
                return False

    return True
