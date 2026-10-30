"""Generate a GitHub-only activity snapshot. Standard library; no credentials in output.

Public calendar is validated day by day; GraphQL optionally supplies commit/repo
counts. Missing metrics are omitted, never converted to zero. Failed collection
leaves the last successful snapshot intact. This script never commits or pushes.
"""
from __future__ import annotations

import argparse
import calendar
from datetime import date, datetime, timedelta, timezone
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

USER = "RahimovShaxriyor"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "engineering"
PROJECTS = {
    "cloudeware-pro": ("CloudWare Pro", ["backend", "frontend"], "backend + frontend"),
    "ExampleWeb-Redis": ("Redis Visual Demo", ["src"], "application source"),
}
DEFINITIONS = {
    "contributions": "Sum of GitHub public-profile calendar counts over the inclusive 365-day window. Can include shared private contribution counts and empty/backdated commits recognized by GitHub.",
    "commit_contributions": "Optional GraphQL totalCommitContributions within the same window; not a lifetime commit total.",
    "commit_repositories": "Optional GraphQL totalRepositoriesWithContributedCommits within the same window; excludes repositories with only issue/PR/review activity.",
    "prs_created": "All-time public pull requests authored by this account, all states.",
    "prs_merged": "All-time public pull requests authored by this account and currently merged; not PRs merged by this account on behalf of others.",
    "stars": "Current stargazer counts summed across public repositories owned by the account, including owned forks; not stars given by the account.",
    "streaks": "Consecutive positive GitHub calendar dates within the snapshot window. Current streak accepts activity through yesterday if today is zero. Longest is window-bounded, not lifetime.",
    "source_activity": "Latest committer-date commit returned by GitHub file-filtered history for explicitly listed source paths; changed files verified. Not a claim to inspect all repository history.",
}


def request(url, payload=None):
    headers = {"User-Agent": "SR-Engineering-Activity", "Accept": "application/vnd.github+json"}
    # Only the GitHub API receives the token; never public HTML or another host.
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = "Bearer " + token
    body = None if payload is None else json.dumps(payload).encode()
    if body:
        headers["Content-Type"] = "application/json"
    for attempt in range(3):
        try:
            with urlopen(Request(url, data=body, headers=headers), timeout=30) as response:
                return response.read().decode("utf-8")
        except (HTTPError, URLError) as error:
            if isinstance(error, HTTPError) and error.code not in (429, 500, 502, 503, 504):
                raise
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def api(path):
    return json.loads(request("https://api.github.com/" + path))


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.dates = {}
        self.counts = {}
        self.target = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("data-date") and a.get("id"):
            self.dates[a["id"]] = a["data-date"]
        if tag == "tool-tip":
            self.target, self.text = a.get("for"), []

    def handle_data(self, data):
        if self.target:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "tool-tip" and self.target:
            m = re.match(r"\s*(No|[\d,]+) contributions? on ", "".join(self.text))
            if m:
                self.counts[self.target] = 0 if m[1] == "No" else int(m[1].replace(",", ""))
            self.target = None

    def days(self):
        return {day: self.counts[key] for key, day in self.dates.items() if key in self.counts}


def validate_days(days, start, end):
    expected = [(start + timedelta(days=i)).isoformat() for i in range((end-start).days+1)]
    if any(day not in days for day in expected):
        raise ValueError("Incomplete contribution calendar; retaining previous snapshot")
    result = [{"date": day, "count": days[day]} for day in expected]
    if any(not isinstance(x["count"], int) or x["count"] < 0 for x in result):
        raise ValueError("Invalid contribution count")
    return result


def streaks(days):
    # GitHub calendar dates, not the viewer's local timezone. An unfinished today
    # with zero contributions does not break a streak that ended yesterday.
    counts = [x["count"] for x in days]
    current = longest = run = 0
    for count in counts:
        run = run + 1 if count else 0
        longest = max(longest, run)
    tail = counts if counts[-1] else counts[:-1]
    for count in reversed(tail):
        if not count:
            break
        current += 1
    return current, longest


def search_count(query):
    result = api("search/issues?" + urlencode({"q": query, "per_page": 1}))
    if result.get("incomplete_results"):
        raise ValueError("Incomplete search results")
    return result["total_count"]


def collect(today):
    start = today - timedelta(days=364)
    daily = {}
    for year in range(start.year, today.year+1):
        parser = CalendarParser()
        parser.feed(request(f"https://github.com/users/{USER}/contributions?from={year}-01-01&to={year}-12-31"))
        daily.update(parser.days())
    days = validate_days(daily, start, today)
    repositories = []
    for page in range(1, 101):
        batch = api(f"users/{USER}/repos?type=owner&per_page=100&page={page}")
        repositories.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise ValueError("Repository pagination limit reached")
    public_owned = [r for r in repositories if not r["private"] and r["owner"]["login"].lower() == USER.lower()]
    result = {
        "schema": 1, "user": USER, "as_of": today.isoformat(), "definitions": DEFINITIONS,
        "period_start": start.isoformat(), "days": days,
        "contributions": sum(d["count"] for d in days),
        "stars": sum(r["stargazers_count"] for r in public_owned),
        "owned_public_repositories": len(public_owned),
        "prs_created": search_count(f"author:{USER} type:pr is:public"),
        "prs_merged": search_count(f"author:{USER} type:pr is:merged is:public"),
        "commit_contributions": None, "commit_repositories": None,
        "sources": ["https://github.com/"+USER, "https://api.github.com/users/"+USER+"/repos"],
        "projects": [],
    }
    if os.environ.get("GITHUB_TOKEN"):
        # A precisely scoped 365-day count; never advertise it as all-time commits.
        query = """query($login:String!,$from:DateTime!,$to:DateTime!){
          user(login:$login){contributionsCollection(from:$from,to:$to){
            totalCommitContributions totalRepositoriesWithContributedCommits
          }} }"""
        try:
            obj = json.loads(request("https://api.github.com/graphql", {
                "query": query, "variables": {"login": USER,
                "from": start.isoformat()+"T00:00:00Z", "to": today.isoformat()+"T23:59:59Z"}}))
            if obj.get("errors"):
                raise ValueError("GraphQL metrics unavailable")
            c = obj["data"]["user"]["contributionsCollection"]
            result["commit_contributions"] = c["totalCommitContributions"]
            result["commit_repositories"] = c["totalRepositoriesWithContributedCommits"]
        except (HTTPError, URLError, ValueError, KeyError, TypeError):
            print("Optional GraphQL metrics unavailable; omitted rather than estimated.")
    for repo, (name, paths, scope) in PROJECTS.items():
        candidates = []
        for path in paths:
            candidates.extend(api(f"repos/{USER}/{repo}/commits?"+urlencode({"path":path,"per_page":1})))
        latest = max(candidates, key=lambda c:c["commit"]["committer"]["date"]) if candidates else None
        if latest:
            detail = api(f"repos/{USER}/{repo}/commits/"+latest["sha"])
            if not detail.get("files"):
                raise ValueError("Empty commit returned as source activity")
        workflows = api(f"repos/{USER}/{repo}/actions/workflows?per_page=100")
        if workflows["total_count"] > len(workflows["workflows"]):
            raise ValueError("Workflow pagination required")
        runs = []
        for workflow in workflows["workflows"]:
            if workflow["state"] != "active":
                continue
            recent = api(f"repos/{USER}/{repo}/actions/workflows/{workflow['id']}/runs?per_page=1")["workflow_runs"]
            if recent:
                r = recent[0]
                runs.append({"name": workflow["name"], "status": r["conclusion"] or r["status"],
                             "url": r["html_url"], "sha": r["head_sha"]})
        result["projects"].append({"repo":repo, "name":name, "scope":scope,
            "sha": latest["sha"] if latest else None,
            "date": latest["commit"]["committer"]["date"][:10] if latest else None,
            "subject": latest["commit"]["message"].splitlines()[0] if latest else None,
            "workflow_count":workflows["total_count"], "runs":runs})
    return result


def render(data, theme="dark", mobile=False):
    light = theme == "light"
    bg, card, edge, fg, muted, accent = (("#f6f8fc","#ffffff","#d5deea","#172b45","#4b6079","#086e9d") if light
        else ("#0e182b","#142039","#2b3c58","#e8f0ff","#a9b9d2","#68d4f3"))
    width, padding, columns = (400,24,2) if mobile else (960,32,3)
    current, longest = streaks(data["days"])
    metrics = [("Contributions",data["contributions"],"365-day window"),
               ("PRs created",data["prs_created"],"public · all time"),
               ("PRs merged",data["prs_merged"],"public · all time"),
               ("Repository stars",data["stars"],"owned public repos"),
               ("Current streak",current,"days · calendar dates"),
               ("Longest streak",longest,"days · within window")]
    if data.get("commit_contributions") is not None and data.get("commit_repositories") is not None:
        metrics.extend([("Commit contributions",data["commit_contributions"],"365-day window"),
                        ("Repos with commits",data["commit_repositories"],"365-day window")])
        if not mobile:
            columns = 4
    rows = (len(metrics)+columns-1)//columns
    top = 122 if mobile else 104
    cell_width = (width-2*padding-(columns-1)*12)/columns
    graph_top = top + rows*112 + 40
    height = graph_top + (290 if mobile else 310)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
      '<title id="title">Engineering Activity</title>',
      f'<desc id="desc">GitHub activity snapshot through {data["as_of"]}. Counts are activity, not code-quality scores. Streaks are bounded by the displayed 365-day window.</desc>',
      '<style>text{font-family:Segoe UI,Arial,sans-serif}</style>',
      f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="18" fill="{bg}" stroke="{edge}"/>']
    def text(x,y,value,size=15,color=fg,weight=400):
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(str(value))}</text>')
    text(padding,38,"SR / ENGINEERING ACTIVITY",16,accent,600)
    text(padding,65,f'{data["period_start"]} — {data["as_of"]}',14,muted)
    text(padding,87,"GitHub snapshot · not a quality score",13,muted)
    for i,(label,value,scope) in enumerate(metrics):
        x=padding+(i%columns)*(cell_width+12);y=top+(i//columns)*112
        parts.append(f'<rect x="{x}" y="{y}" width="{cell_width}" height="100" rx="10" fill="{card}" stroke="{edge}"/>')
        text(x+14,y+23,label,13 if mobile else 15,muted)
        text(x+14,y+61,f"{value:,}",32,fg,600)
        text(x+14,y+84,scope,11 if mobile else 13,muted)
    text(padding,graph_top,"Contributions over time",18,fg,600)
    text(padding,graph_top+24,"Monthly totals · edge months are partial",12 if mobile else 14,muted)
    totals={}
    for day in data["days"]:
        key=day["date"][:7];totals[key]=totals.get(key,0)+day["count"]
    peak=max(totals.values()) or 1
    gx=padding+40;gy=graph_top+60;gw=width-padding-gx;gh=130
    for ratio in (0,.5,1):
        y=gy+gh*(1-ratio)
        parts.append(f'<path d="M{gx} {y}h{gw}" stroke="{edge}"/>')
        text(padding,y+4,str(round(peak*ratio)),11,muted)
    step=gw/len(totals)
    for i,(month,count) in enumerate(totals.items()):
        h=count/peak*gh;x=gx+i*step+3
        parts.append(f'<rect x="{x:.2f}" y="{gy+gh-h:.2f}" width="{max(step-6,2):.2f}" height="{h:.2f}" rx="2" fill="{accent}"><title>{month}: {count} contributions</title></rect>')
        if not mobile or i%2==0:
            text(x,gy+gh+20,calendar.month_abbr[int(month[-2:])],10 if mobile else 13,muted)
    text(padding,height-36,"Source: GitHub · no third-party widgets",12 if mobile else 14,muted)
    text(padding,height-16,"Snapshot date: "+data["as_of"]+" UTC",12,muted)
    return "\n".join(parts)+"\n</svg>\n"


def activity_markdown(data):
    lines=["<!-- BEGIN VERIFIED PROJECT ACTIVITY -->",f"<sub>Source activity checked {data['as_of']} (UTC). File-filtered history; empty commits are excluded.</sub>",""]
    for p in data["projects"]:
        url=f'https://github.com/{USER}/{p["repo"]}'
        if p["sha"]:
            subject=p["subject"].replace("[","(").replace("]",")").replace("<","&lt;").replace(">","&gt;").replace("`","")
            lines.append(f'- **{p["name"]}** · [{p["sha"][:7]}]({url}/commit/{p["sha"]}) · {p["date"]} · {subject} ({p["scope"]}).')
        else:
            lines.append(f'- **{p["name"]}** · No source change found in the inspected paths.')
        if p["workflow_count"] == 0:
            lines.append("  GitHub Actions: no workflows present.")
        elif not p["runs"]:
            lines.append("  GitHub Actions: workflows present; no active workflow run found.")
        else:
            for r in p["runs"]:
                lines.append(f'  Workflow [{escape(r["name"])}]({r["url"]}): {r["status"]} at `{r["sha"][:7]}`. Workflow status is not a coverage score.')
    lines.append("<!-- END VERIFIED PROJECT ACTIVITY -->")
    return "\n".join(lines)


def write_snapshot(data):
    validate_days({x["date"]:x["count"] for x in data["days"]},date.fromisoformat(data["period_start"]),date.fromisoformat(data["as_of"]))
    if data["contributions"] != sum(x["count"] for x in data["days"]):
        raise ValueError("Contribution total does not match calendar")
    readme_path=ROOT/"docs"/"activity.md"
    readme=readme_path.read_text(encoding="utf-8")
    pattern=r"<!-- BEGIN VERIFIED PROJECT ACTIVITY -->.*?<!-- END VERIFIED PROJECT ACTIVITY -->"
    if len(re.findall(pattern,readme,flags=re.S)) != 1:
        raise ValueError("Activity document markers missing or duplicated")
    updated=re.sub(pattern,lambda _:activity_markdown(data),readme,flags=re.S)
    files={"snapshot.json":json.dumps(data,ensure_ascii=False,indent=2)+"\n"}
    for theme in ("dark","light"):
        for mobile in (False,True):
            files[f'activity-{theme}{"-mobile" if mobile else ""}.svg']=render(data,theme,mobile)
    OUTPUT.mkdir(parents=True,exist_ok=True)
    for name,content in files.items():
        (OUTPUT/name).write_text(content,encoding="utf-8")
    readme_path.write_text(updated,encoding="utf-8")


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--snapshot",type=Path,help="Render a saved snapshot without any network access")
    args=parser.parse_args()
    data=json.loads(args.snapshot.read_text(encoding="utf-8")) if args.snapshot else collect(datetime.now(timezone.utc).date())
    write_snapshot(data)
    print("Activity snapshot generated; no Git operations performed.")
