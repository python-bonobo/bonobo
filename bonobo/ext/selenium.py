from selenium import webdriver

from bonobo import service

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/601.4.4 (KHTML, like Gecko) Version/9.0.3 Safari/601.4.4'


def create_profile(use_tor=False):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("toolkit.startup.max_resumed_crashes", "-1")

    if use_tor:
        # tor connection
        profile.set_preference('network.proxy.type', 1)
        profile.set_preference('network.proxy.socks', '127.0.0.1')
        profile.set_preference('network.proxy.socks_port', 9050)

    # user agent
    profile.set_preference("general.useragent.override", USER_AGENT)

    return profile


def create_browser(profile):
    browser = webdriver.Firefox(profile)
    browser.implicitly_wait(10)
    browser.set_page_load_timeout(10)
    return browser


@service
def browser():
    return create_browser(create_profile(use_tor=False))


@service
def torbrowser():
    return create_browser(create_profile(use_tor=True))
