#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: github.com/imvast
@Date: 8/1/2023
"""

from tls_client   import Session
from threading    import Thread
from colorama     import Fore
from os           import system, _exit
from time         import sleep
from json         import loads, dumps
from base64       import b64encode
from httpx        import get, delete, post
from random       import choice, uniform
from terminut     import Console
from veilcord     import VeilCord, Solver, extractCode
from base64       import b64decode
from toml         import load


class jsolve:
    def __call__(session: Session, siteurl: str, sitekey: str, rqdata: str) -> str:
        solveer = Solver(
            session = session,
            service = "CAPSOVLER",
            capKey  = config.get("captchaKey"),
            siteUrl = siteurl,
            siteKey = sitekey,
            rqData = rqdata,
            user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9015 Chrome/108.0.5359.215 Electron/22.3.2 Safari/537.36"
        )
        return solveer.solveCaptcha()
    

class Joiner:
    def __init__(
        self, 
        invite: str, 
        proxies: list = None, 
        xcontext = None
    ) -> None:
        self.invite = invite
        self.proxies = proxies
        self.xcontext = xcontext

    def newSession(self):
        self.client = Session(
            client_identifier="discord_1_0_9015",
            random_tls_extension_order=True
        )
        self.client.proxies = (
            f"http://{choice(self.proxies).strip()}"
            if self.proxies != None and len(self.proxies) != 0
            else None
        )
        self.client.headers = {
            "authority": "discord.com",
            "accept": "*/*",
            "accept-language": "en-US",
            "connection": "keep-alive",
            "content-type": "application/json",
            "origin": "https://discord.com",
            "referer": "https://discord.com/channels/@me",
            "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9015 Chrome/108.0.5359.215 Electron/22.3.2 Safari/537.36",
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "en-US",
            "x-discord-timezone": "America/New_York",
            "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDE1Iiwib3NfdmVyc2lvbiI6IjEwLjAuMjI2MjEiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMTUgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMiBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMjIuMy4yIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjE5ODM5LCJuYXRpdmVfYnVpbGRfbnVtYmVyIjozMjI2NiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbCwiZGVzaWduX2lkIjowfQ==",
        }
        if self.xcontext is not None:
            self.client.headers["x-context-properties"] = self.xcontext
            
        self.veilcord = VeilCord(self.client, "app", user_agent=self.client.headers.get("user-agent"), build_num=glbuildnum)
        self.fingerp, self.client.cookies = self.veilcord.getFingerprint(self.client.headers.get("x-super-properties"))
        
        return self.client

    def getUserID(self, token):
        return b64decode(token.split(".")[0]).decode()
    
    def get_random_presence(self):
        return {
            "status": choice(["online", "dnd", "idle"]), 
            "since": 0, 
            "activites": [], 
            "afk": False
        }
        
    def join(self, token, invite, hideJoin, captcha=None, caprq=None):
        if captcha == "fail": return
        
        self.newSession()

        if config.get("ShowWS"):
            Console.printf(f"(~) Connecting Token To WS [{token[:25]}...]")
            
        session = self.veilcord.openSession(self.get_random_presence())
        session_id = self.veilcord.getSession(token, session)

        if session_id is None:
            return print("(!) Failed Getting SessionID.")
        
        try:
            self.client.headers["authorization"] = token
            if captcha is not None:
                self.client.headers["x-captcha-key"] = captcha
                self.client.headers["x-captcha-rqtoken"] = caprq

            r = self.client.post(
                f"https://discord.com/api/v9/invites/{invite}",
                json = {"session_id": session_id}
            )
            
            match r.status_code:
                case 200:
                    Console.printf(f"(+) Joined [{invite}] - [200]")
                    if "MEMBER_VERIFICATION_GATE_ENABLED" in r.text:
                        self.BypassRules(token, invite, r.json()["guild"]["id"])
                    if hideJoin:
                        self.DeleteJoinMessage(token, r.json()["guild"]["id"])
                    if "GUILD_ONBOARDING" in r.text:
                        self.BypassOnboarding(token, r.json().get("guild").get("id"))
                case 429:
                    Console.printf(f"(-) RATELIMIT BY CLOUDFLARE | use proxies or vpn :D")
                    return sleep(3)
                case 403:
                    if "captcha" in r.text:
                        return Console.printf("(!) Invalid CaptchaKey")
                    if "The user is banned from this guild." in r.text:
                        return Console.printf("(!) Token banned from server.")
                    if config.get("RemoveLocked"):
                        with open("tokens.txt", "r+") as file:
                            file.seek(0)
                            file.writelines([line for line in file.readlines() if token not in line])
                            file.truncate()
                    if "You need to verify your account" in r.text:
                        return Console.printf(f"(-) Token Locked. [{token[:25]}]")
                    return Console.printf(f"(-) Token Err. [{token[:25]}] | {r.text}")
                case 401:
                    if config.get("RemoveInvalid"):
                        with open("tokens.txt", "r+") as file:
                            file.seek(0)
                            file.writelines([line for line in file.readlines() if token not in line])
                            file.truncate()
                    return Console.printf(f"(-) Token Invalid. [{token[:25]}]")
                case 400:
                    Console.printf(f"(-) Captcha Gay [{token[:25]}] | Solving...")
                    if config.get("captchaKey") != "":
                        capSKEY = r.json()["captcha_sitekey"]
                        rqtoken = r.json().get("captcha_rqtoken")
                        rqdata  = r.json().get("captcha_rqdata")
                        key = jsolve()(self.client, f"https://discord.com/invite/{invite}", capSKEY, rqdata)
                        return self.join(token, invite, hideJoin, captcha=key, caprq=rqtoken)
                case _:
                    return Console.printf(f"(!) Error [{r.text}]")
        except Exception as e:
            Console.printf(f"(!) Join Exception: {e}")
            return self.join(token, invite, hideJoin)

    def BypassRules(self, token, invcode, guildid):
        try:
            self.client.headers["authorization"] = token
            rulereq = get(
                f"https://discord.com/api/v9/guilds/{guildid}/member-verification?with_guild=false&invite_code={invcode}",
            )
            if rulereq.status_code != 200:
                return print(
                    f"{rulereq.status_code} | Failed bypasruel cuz idk | {rulereq.text}"
                )
            submitpayload = rulereq.json()
            submitpayload["form_fields"][0]["response"] = True
            del submitpayload["description"]
            submitpayload = dumps(submitpayload)
            self.client.headers["content-type"] = "application/json"
            res = self.client.put(
                f"https://discord.com/api/v9/guilds/{guildid}/requests/@me",
                json=submitpayload
            )
            Console.printf(f"Bypassed Gate: {res.status_code}")
        except Exception as e:
            Console.printf(f"(!) err@BypassRules: {e}")
            
    def BypassOnboarding(self, token, guild_id):
        self.client.headers["authorization"] = token
        board_info = self.client.get(f"https://discord.com/api/v9/guilds/{guild_id}/onboarding").json()
        
        required_prompts = [prompt for prompt in board_info["prompts"] if prompt["required"]]
        
        onboarding_responses = [choice(prompt["options"])["id"] for prompt in required_prompts]
        onboarding_prompts_seen = {str(prompt["id"]): 1696435631351 for prompt in required_prompts}
        onboarding_responses_seen = {str(option["id"]): 1696435631351 for prompt in required_prompts for option in prompt["options"]}

        payload = {
            "onboarding_responses": onboarding_responses,
            "onboarding_prompts_seen": onboarding_prompts_seen,
            "onboarding_responses_seen": onboarding_responses_seen
        }

        response = self.client.post(f'https://discord.com/api/v9/guilds/{guild_id}/onboarding-responses', json=payload)
        if "guild_id" in response.text:
            print("bypassed onboard")
        else:
            print(f"fail bypass ob; {response.text}")
            
    def DeleteJoinMessage(self, token, guildid):
        headers = {
            "authorization": token
        }
        selfid = self.getUserID(token)
        res = get(f"https://discord.com/api/v9/guilds/{guildid}", headers=headers)
        if "system_channel_id" in res.text:
            chanid = res.json()["system_channel_id"]
            try:
                response = get(
                    f"https://discord.com/api/v9/channels/{chanid}/messages",
                    params = {"limit": "3"},
                    headers = headers
                ).json()[0]
                if response["type"] == 7:
                    if int(response["author"]["id"]) == int(selfid):
                        try:
                            fRes = delete(
                                f"https://discord.com/api/v9/channels/{chanid}/messages/{response['id']}",
                                headers=headers
                            )
                            if fRes.is_success:
                                Console.printf(f"(+) Join Message Removed.")
                            else:
                                Console.printf(f"(!) join message del status @ {fRes}")
                        except:
                            Console.printf("(!) failed del join message")
            except Exception as e:
                Console.printf(f"(!) Failed to delete join message. {e}")


def start():
    system("cls")
    Console.printf(
        f"""
        {Fore.LIGHTMAGENTA_EX}╦  ╦{Fore.MAGENTA}┌─┐┌─┐┌┬┐  {Fore.LIGHTMAGENTA_EX} ╦{Fore.MAGENTA}┌─┐┬┌┐┌┌─┐┬─┐
        {Fore.LIGHTMAGENTA_EX}╚╗╔╝{Fore.MAGENTA}├─┤└─┐ │   {Fore.LIGHTMAGENTA_EX} ║{Fore.MAGENTA}│ │││││├┤ ├┬┘
        {Fore.LIGHTMAGENTA_EX} ╚╝ {Fore.MAGENTA}┴ ┴└─┘ ┴   {Fore.LIGHTMAGENTA_EX}╚╝{Fore.MAGENTA}└─┘┴┘└┘└─┘┴└─

        """
        + Fore.RESET,
        showTimestamp=False,
    )

    with open("tokens.txt", "r") as f:
        tokens = [x.strip() for x in f.readlines()]

    proxies = (open("./proxies.txt", "r").readlines())
    proxy = (
        proxies
        if proxies != None and len(proxies) != 0 
        else None
    )

    if len(tokens) > 100 and not proxy:
        print("You should probably use proxies lol.")


    link = Console.inputf("(?) Invite > ")
    inv = extractCode(link)
    if inv is None:
        Console.printf("(!) Invite check failed.", showTimestamp=False)
        return
    res = get(f"https://discord.com/api/v9/invites/{inv}")
    if res.status_code == 404:
        return Console.printf("(!) Invalid Invite.", showTimestamp=False)

    WAIT_AMT = Console.inputf("(?) Join Delay > ")

    deljoin = Console.inputf("(?) Delete Join Message (y/N) > ").lower() == "y"

    try:
        res = get(
            f"https://discord.com/api/v9/invites/{inv}?inputValue={inv}&with_counts=true&with_expiration=true"
        ).json()
        jsonContext = {
            "location": "Join Guild",
            "location_guild_id": str(res["guild"]["id"]),
            "location_channel_id": str(res["channel"]["id"]),
            "location_channel_type": int(res["channel"]["type"]),
        }
        json_str = dumps(jsonContext)
        xContext = b64encode(json_str.encode()).decode()
        xcontext = xContext
    except:
        xcontext = None
        
    print()
    dis = Joiner(inv, proxy, xcontext)
    
    if "," in WAIT_AMT:
        WAIT_AMT = WAIT_AMT.split(",")

    for token in tokens:
        if type(WAIT_AMT) is list: NEW_WAIT_AMT = round(uniform(float(WAIT_AMT[0]), float(WAIT_AMT[1])), 3)
        else: 
            NEW_WAIT_AMT = float(WAIT_AMT)\
            if WAIT_AMT else 0.2 if (
                NEW_WAIT_AMT := float(WAIT_AMT) if WAIT_AMT else 0.2
            ) == 0 else NEW_WAIT_AMT
            
        sleep(NEW_WAIT_AMT)
        Thread(target=dis.join, args=[token, inv, deljoin]).start()




if __name__ == "__main__":
    Console.init(colMain=Fore.MAGENTA)
    config = load("config.toml").get("opts")
    glbuildnum = VeilCord.getBuildNum()

    try:
        start()
    except KeyboardInterrupt:
        _exit(0)
    except Exception as e:
        Console.printf(f"(!) Thread Exception: {e}")
