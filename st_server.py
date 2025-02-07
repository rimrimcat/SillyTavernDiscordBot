import asyncio
import nest_asyncio
from time import sleep
from typing import Any, Literal, Optional, TypedDict

from aiohttp import web
from playwright.async_api import (
    Browser,
    BrowserType,
    Page,
    Playwright,
    async_playwright,
)

from settings import SILLY_TAVERN_PORT, LOCAL_SERVER_PORT, CHARACTER_NAME


SILLY_TAVERN_URL = f"http://localhost:{SILLY_TAVERN_PORT}"


## CONNECTIONS
CONNECTIONS = '//div[@id="API-status-top"]'
CONNECT_API = '//div[@id="api_button_openai"]'

## CHAT
CHAT_AREA = '//textarea[@id="send_textarea"]'
CHAT_MENU = '//div[@id="options_button"]'
CHAT_SEND = '//div[@id="send_but"]'
NEW_CHAT = '//a[@id="option_start_new_chat"]'
MANAGE_CHAT_FILES = '//span[@data-i18n="Manage chat files"]'

CHAT_HISTORY_NEW = '//div[@id="newChatFromManageScreenButton"]'
CHAT_HISTORY_BLOCKS = '//div[@class="select_chat_block  wide100p flex-container"]'

RENAME_CHAT = '//div[@title="Rename chat file"]'
POPUP_RENAME_CHAT = '//textarea[@id="dialogue_popup_input"]'

MESSAGE_LAST_CONTEXT = '//div[@class="mes lastInContext"]'
MESSAGE_LLM = '//div[@class="mes last_mes"]'
MESSAGE_LLM_EDIT = '//div[@class="mes_button mes_edit fa-solid fa-pencil interactable"]'
MESSAGE_LLM_TEXTAREA = '//textarea[@id="curEditTextarea"]'
MESSAGE_LLM_CANCEL_EDIT = '//div[@title="Cancel"]'
MESSAGE_LLM_REGENERATE = (
    '//div[@class="swipe_right fa-solid fa-chevron-right interactable"]'
)


## CHARACTER
CHARACTERS = '//div[@id="rightNavDrawerIcon"]'
LLM_CHARACTER = f'//span[@title="[Character] {CHARACTER_NAME}"]'
LLM_GROUP_CHARACTER = f'//div[@title="[Group] Group: {CHARACTER_NAME}"]'

## PERSONA
PERSONA_MANAGEMENT = '//div[@title="Persona Management"]'
NEW_PERSONA = '//div[@id="create_dummy_persona"]'
POPUP_NEW_PERSONA = (
    '//textarea[@class="popup-input text_pole result-control auto-select"]'
)
POPUP_PERSONA_BODY = '//div[@class="popup-body"]'
PERSONA_DESCRIPTION = '//textarea[@id="persona_description"]'


OK = '//div[@data-i18n="OK"]'
OK_2 = '//div[@id="dialogue_popup_ok"]'
CLOSE = '//div[@id="select_chat_cross"]'
TOAST_CLOSE = '//button[@class="toast-close-button"]'

THROBBER = "//dialog"


class Datas:
    class Data(TypedDict, total=True):
        persona: str
        chat: str
        message: str
        character: str
        trigger: bool

    @staticmethod
    def json_to_data(json: Any) -> Data:
        return {
            "persona": json.get("persona", ""),
            "chat": json.get("chat", ""),
            "message": json.get("message", ""),
            "character": json.get("character", ""),
            "trigger": json.get("trigger", False),
        }


class Responses:
    class Response(TypedDict):
        status: Literal["success", "error"]
        data: dict[str, str]
        message: str

    @staticmethod
    def working() -> Response:
        return {
            "status": "success",
            "data": {},
            "message": "it is working",
        }

    @staticmethod
    def missing(missing_keys: list[str]) -> Response:
        return {
            "status": "error",
            "data": {},
            "message": f"missing or empty required keys: {missing_keys}",
        }

    @staticmethod
    def successful_llm_response(llm_message: str) -> Response:
        return {
            "status": "success",
            "data": {"message": llm_message},
            "message": "LLM replied successfully",
        }

    @staticmethod
    def successful_send() -> Response:
        return {
            "status": "success",
            "data": {},
            "message": "Message sent successfully",
        }


class ST:
    browsertype: BrowserType
    browser: Browser
    page: Page

    def __init__(self, browsertype: BrowserType, browser: Browser, page: Page) -> None:
        self.browser = browser
        self.page = page

    @classmethod
    async def create(cls, playwright: Playwright):
        browsertype = playwright.chromium  # or "firefox" or "webkit".
        browser = await browsertype.launch(headless=True, slow_mo=50)
        page = await browser.new_page()

        await page.goto(SILLY_TAVERN_URL)

        return ST(browsertype, browser, page)

    async def click(self, element: str, timeout: Optional[float] = None):
        await self.page.wait_for_selector(element, timeout=timeout)
        await self.page.click(element)

    async def type(self, element: str, content: str):
        await self.page.wait_for_selector(element)
        textarea = self.page.locator(element)
        await textarea.fill(content)

    async def click_inner(self, elements: list[str]):
        await self.page.wait_for_selector(elements[0])
        curr_selector = self.page.locator(elements[0])

        for element in elements[1:]:
            curr_selector = curr_selector.locator(element)

        # await self.page.click(curr_selector)
        await curr_selector.click()

    async def click_first(self, element: str):
        blocks = await self.page.query_selector_all(CHAT_HISTORY_BLOCKS)
        await blocks[0].click()

    async def wait_load(self):
        await self.page.wait_for_selector(THROBBER, state="visible")
        await self.page.wait_for_selector(THROBBER, state="hidden")

    async def select_direct(self):
        await self.click(CHARACTERS)
        await self.click(LLM_CHARACTER)
        await self.click(CHARACTERS)

    async def select_group(self):
        await self.click(CHARACTERS)
        await self.click(LLM_GROUP_CHARACTER)
        await self.click(CHARACTERS)

    async def send_message(self, message: str):
        await self.page.locator(CHAT_AREA).fill(message)
        await self.click(CHAT_SEND)

    async def start(self):
        await self.click(CONNECTIONS)
        await self.click(CONNECT_API)
        await self.click(CONNECTIONS)

    async def new_chat(self, chat_name: str):
        await self.click(CHAT_MENU)
        await self.click(MANAGE_CHAT_FILES)
        await self.click(CHAT_HISTORY_NEW)

        await self.click(CHAT_MENU)
        await self.click(MANAGE_CHAT_FILES)

        blocks = await self.page.query_selector_all(CHAT_HISTORY_BLOCKS)
        rename_chat = await blocks[0].query_selector(RENAME_CHAT)
        if rename_chat is None:
            raise RuntimeError("Can't find rename_chat! Did UI change?")
        await rename_chat.click()
        await self.type(POPUP_RENAME_CHAT, chat_name)
        await self.click(OK_2)
        await self.click(CLOSE)

    async def new_persona(self, persona: str):
        await self.click(PERSONA_MANAGEMENT)
        await self.click(NEW_PERSONA)
        await self.type(POPUP_NEW_PERSONA, persona)
        await self.click(OK)
        await self.click(PERSONA_MANAGEMENT)
        sleep(0.1)

    async def switch_chat(self, chat_name: str):
        await self.click(CHAT_MENU)
        await self.click(MANAGE_CHAT_FILES)
        await self.page.get_by_text(chat_name + ".jsonl", exact=True).click()
        await self.wait_load()

    async def switch_persona(self, persona: str):
        await self.click(PERSONA_MANAGEMENT)

        loc = self.page.locator('//div[@id="persona-management-block"]')
        await loc.locator('//span[@class="ch_name flex1"]', has_text=persona).click()

        try:
            await self.click(TOAST_CLOSE, timeout=50)
            print("toast successfully pressed")
        except:
            pass

        await self.click(PERSONA_MANAGEMENT)
        sleep(0.1)

    async def switch_or_new_persona(self, persona: str):
        await self.click(PERSONA_MANAGEMENT)

        # wait for animation
        loc = self.page.locator('//div[@id="persona-management-button"]')
        await loc.locator('//div[@class="drawer-content openDrawer"]').wait_for()

        await self.page.select_option(
            '//select[@class="J-paginationjs-size-select"]', value="1000"
        )

        try:
            loc = self.page.locator('//div[@id="persona-management-block"]')
            await loc.locator('//span[@class="ch_name flex1"]', has_text=persona).click(
                timeout=500
            )
            print(f"Switching to persona {persona}")

            try:
                await self.click(TOAST_CLOSE, timeout=100)
            except:
                print(f"Already using persona {persona}!")
        except:
            # PERSONA DOESN'T EXIST
            print(f"Creating persona {persona}!")
            await self.click(NEW_PERSONA)
            await self.type(POPUP_NEW_PERSONA, persona)
            await self.page.locator(POPUP_PERSONA_BODY).press("Enter")
            
            # SELECT PERSONA
            loc = self.page.locator('//div[@id="persona-management-block"]')
            await loc.locator('//span[@class="ch_name flex1"]', has_text=persona).click()
            await self.click(TOAST_CLOSE, timeout=50)
        
        await self.click(PERSONA_MANAGEMENT)
        sleep(0.2)

    async def switch_or_new_chat(self, chat_name: str):
        await self.click(CHAT_MENU)
        await self.click(MANAGE_CHAT_FILES)
        try:
            await self.page.get_by_text(chat_name + ".jsonl", exact=True).click(
                timeout=700
            )
            print(f"Switching to chat {chat_name}")
            await self.wait_load()
        except:
            print(f"Creating new chat {chat_name}")
            await self.click(CHAT_HISTORY_NEW)
            await self.click(CHAT_MENU)
            await self.click(MANAGE_CHAT_FILES)

            blocks = await self.page.query_selector_all(CHAT_HISTORY_BLOCKS)
            rename_chat = await blocks[0].query_selector(RENAME_CHAT)
            if rename_chat is None:
                raise RuntimeError("Can't find rename_chat! Did UI change?")
            await rename_chat.click()
            await self.type(POPUP_RENAME_CHAT, chat_name)
            await self.click(OK_2)
            await self.click(CLOSE)

    async def switch_or_new_group_chat(self, chat_name: str):
        await self.click(CHAT_MENU)
        await self.click(MANAGE_CHAT_FILES)
        try:
            await self.page.get_by_text(chat_name, exact=True).click(timeout=700)
            print(f"Switching to chat {chat_name}")
            await self.wait_load()
        except:
            print(f"Creating new chat {chat_name}")
            await self.click(CHAT_HISTORY_NEW)
            await self.click(CHAT_MENU)
            await self.click(MANAGE_CHAT_FILES)

            blocks = await self.page.query_selector_all(CHAT_HISTORY_BLOCKS)
            rename_chat = await blocks[0].query_selector(RENAME_CHAT)
            if rename_chat is None:
                raise RuntimeError("Can't find rename_chat! Did UI change?")
            await rename_chat.click()
            await self.type(POPUP_RENAME_CHAT, chat_name)
            await self.click(OK_2)
            await self.click(CLOSE)

    async def get_persona_description(self, persona: Optional[str] = None):
        desc = ""

        await self.click(PERSONA_MANAGEMENT)
        # wait for animation
        loc = self.page.locator('//div[@id="persona-management-button"]')
        await loc.locator('//div[@class="drawer-content openDrawer"]').wait_for()

        await self.page.select_option(
            '//select[@class="J-paginationjs-size-select"]', value="1000"
        )

        try:
            if persona is not None:
                loc = self.page.locator('//div[@id="persona-management-block"]')
                await loc.locator(
                    '//span[@class="ch_name flex1"]', has_text=persona
                ).click(timeout=500)
                try:
                    await self.click(TOAST_CLOSE, timeout=100)
                except:
                    print(f"Already using persona {persona}!")

            desc = await self.page.locator(PERSONA_DESCRIPTION).input_value()
        except:
            pass

        await self.click(PERSONA_MANAGEMENT)
        sleep(0.2)

        return desc

    async def set_persona_description(self, persona: str, desc: str):
        await self.click(PERSONA_MANAGEMENT)
        # wait for animation
        loc = self.page.locator('//div[@id="persona-management-button"]')
        await loc.locator('//div[@class="drawer-content openDrawer"]').wait_for()

        await self.page.select_option(
            '//select[@class="J-paginationjs-size-select"]', value="1000"
        )

        try:
            loc = self.page.locator('//div[@id="persona-management-block"]')
            await loc.locator('//span[@class="ch_name flex1"]', has_text=persona).click(
                timeout=500
            )
            try:
                await self.click(TOAST_CLOSE, timeout=100)
            except:
                print(f"Already using persona {persona}!")

            await self.page.locator(PERSONA_DESCRIPTION).fill(desc)
        except:
            pass

        await self.click(PERSONA_MANAGEMENT)
        sleep(0.2)

    async def get_llm_response(self):
        await self.page.wait_for_selector(MESSAGE_LAST_CONTEXT)
        loc = self.page.locator(MESSAGE_LLM).locator(MESSAGE_LLM_EDIT)
        await loc.wait_for(timeout=60000)
        await loc.click()
        response = await self.page.locator(MESSAGE_LLM_TEXTAREA).input_value()
        await self.page.locator(MESSAGE_LLM).locator(MESSAGE_LLM_CANCEL_EDIT).click()
        return response

    async def send_direct_message(self, persona: str, chat_name: str, message: str):
        await self.select_direct()
        await self.switch_or_new_chat(chat_name)
        await self.switch_or_new_persona(persona)
        await self.send_message(message)
        return await self.get_llm_response()

    async def send_group_message(self, persona: str, chat_name: str, message: str):
        await self.select_group()
        await self.switch_or_new_group_chat(chat_name)
        await self.switch_or_new_persona(persona)
        await self.send_message(message)
        sleep(0.2)

    async def trigger_llm_group_message(self, chat_name: str):
        await self.select_group()
        await self.switch_or_new_group_chat(chat_name)
        await self.send_message("/trigger")
        return await self.get_llm_response()

    async def done(self):
        await self.page.reload()
        await self.start()

    async def close(self):
        await self.browser.close()


class AsyncServer:
    name = "[SERVER]"

    def __init__(self, st: ST):
        self.st = st
        self.host = "localhost"
        self.port = LOCAL_SERVER_PORT
        self.app = web.Application()

        self.setup_routes()

    def setup_routes(self):
        self.app.router.add_get("/", self.main)
        self.app.router.add_post("/stop", self.stop)
        self.app.router.add_post("/chat", self.chat)
        self.app.router.add_post("/groupchat", self.groupchat)

    async def main(self, request: web.Request):
        return web.json_response(
            Responses.working(),
            status=200,
        )

    async def stop(self, request: web.Request):
        await self.st.close()
        await self.app.shutdown()
        exit()

    def validate_data_for_chat(self, data: Datas.Data):
        missing_keys: list[str] = []
        for key in ["persona", "chat", "message"]:
            if not data[key]:
                missing_keys.append(key)

        if len(missing_keys) > 0:
            resp = web.json_response(
                Responses.missing(missing_keys),
                status=400,
            )
            print(f"{self.name}: Response\n{resp}")
            return resp
        return None

    async def chat(self, request: web.Request):
        data: Datas.Data = await request.json()
        print(f"{self.name}: Received chat request:\n{data}")
        val_resp = self.validate_data_for_chat(data)

        if val_resp:
            return val_resp

        message = await self.st.send_direct_message(
            persona=data.get("persona"),
            message=data.get("message"),
            chat_name=data.get("chat"),
        )
        await self.st.done()

        print(f"{self.name}: Success.")
        return web.json_response(
            Responses.successful_llm_response(message),
        )

    async def groupchat(self, request: web.Request):
        data: Datas.Data = await request.json()
        print(f"{self.name}: Received chat request:\n{data}")
        val_resp = self.validate_data_for_chat(data)

        if val_resp and data["trigger"] and not data["chat"]:
            message = await self.st.trigger_llm_group_message(data["chat"])
            await self.st.done()
            print(f"{self.name}: Success.")
            return web.json_response(
                Responses.successful_llm_response(message),
            )
        elif val_resp and not data["trigger"]:
            return val_resp

        await self.st.send_group_message(
            persona=data["persona"],
            message=data["message"],
            chat_name=data["chat"],
        )

        if data["trigger"]:
            message = await self.st.trigger_llm_group_message(data["chat"])
            await self.st.done()
            print(f"{self.name}: Success.")
            return web.json_response(
                Responses.successful_llm_response(message),
            )
        else:
            await self.st.done()
            print(f"{self.name}: Success.")
            return web.json_response(Responses.successful_send())

    async def run(self):
        print(f"Starting server at {self.host}:{self.port}...")
        nest_asyncio.apply(asyncio.get_event_loop())
        web.run_app(
            self.app, host=self.host, port=self.port, loop=asyncio.get_event_loop()
        )


async def main():
    async with async_playwright() as playwright:
        st = await ST.create(playwright)
        await st.done()
        
        ass = AsyncServer(st)
        await ass.run()

if __name__ == "__main__":
    asyncio.run(main())
