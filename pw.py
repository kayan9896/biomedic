# test_app.py
import json
import pytest
from playwright.sync_api import Page, expect

automate = True
img_count = 0
activeside = 'ap'
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    # Optional: run headless or not
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080}
    }

def dynamic_data(route):
    global img_count
    global activeside
    global automate
    with open('pw.json', 'r') as f:
        dt = json.load(f)
    if automate:
        dt['img_count'] = img_count
        dt['active_side'] = activeside
    
    route.fulfill(status=200, content_type="application/json", body=json.dumps(dt))

def image_metadata(route):
    global activeside
    global automate
    with open('imgmeta.json', 'r') as f:
        dt = json.load(f)
    if automate:
        route.fulfill(status=200, content_type="application/json", body=json.dumps(dt[activeside]))
    else:
        route.fulfill(status=200, content_type="application/json", body=json.dumps(dt['cur']))

def test_bypass_l13_and_reach_l1(page: Page):
    global img_count
    global activeside
    global automate

    # 1. Start your app (adjust URL if needed)
    page.goto("http://localhost:3000")  # <-- your dev server

    # 2. MOCK the backend API
    page.route("http://localhost:5000/get-carms", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"carm1": {"image":"http://localhost:5000/carm-images"}}'
    ))
    page.route("http://localhost:5000/carm-images", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='''
        {"image": "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAIAAADTED8xAAADMElEQVR4nOzVwQnAIBQFQYXff81RUkQCOyDj1YOPnbXWPmeTRef+/3O/OyBjzh3CD95BfqICMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMO0TAAD//2Anhf4QtqobAAAAAElFTkSuQmCC", 
        "imu_on": true}
        '''
    ))
    page.route("http://localhost:5000/check-video-connection", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='''
        {"connected": true}
        '''
    ))
    page.route("http://localhost:5000/check-tilt-sensor", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='''
        {"connected": true, "battery_low": false}
        '''
    ))
    page.route("http://localhost:5000/run2", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"templates": [{"id": 1, "name": "Mock C-Arm"}, {"id": 2, "name": "Test Case"}]}'
    ))
    page.route("http://localhost:5000/next", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"templates": [{"id": 1, "name": "Mock C-Arm"}, {"id": 2, "name": "Test Case"}]}'
    ))


    page.route("http://localhost:5000/api/states", dynamic_data)

    page.route("http://localhost:5000/api/image-with-metadata", image_metadata)
    
    select = page.locator("select")
    expect(select).to_be_visible()
    page.select_option("select", index=1)

    # 3. Wait for L13 (the connect screen)
    connect_button = page.locator("[data-testid='ctnbtn']")
    expect(connect_button).to_be_visible(timeout=5000)

    # 4. Click Connect → triggers handleConnect() → API mocked → sets isConnected=true
    connect_button.click()
    connect_button.click()
    connect_button.click()
    connect_button.click()
    
    # 5. Wait for L1 to appear
    l1_background = page.locator("[data-testid='l1-background']")
    expect(l1_background).to_be_attached(timeout=8000)

    # 6. Bonus: Take a screenshot to see it worked!
    page.screenshot(path="e2e-l1-success.png")

    start_button = page.get_by_alt_text("ContinueButton")
    expect(start_button).to_be_visible(timeout=5000)
    start_button.click()
    img_count += 1
    page.wait_for_timeout(1000)
    activeside = 'ob'
    img_count += 1
    automate = False
    page.wait_for_timeout(1000000)

    print("L13 bypassed! L1 is visible!")