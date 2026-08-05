from ..schemas.models import Profiles
def extract_links(links):
    profiles={
            "project_links":[]
        }
    for link in links:
        link=link.lower()

        if link.startswith("mailto:"):
            profiles["email"]=link.replace("mailto:","")
        elif "linkedin.com" in link:
            profiles["linkedin"]=link
        elif "leetcode.com" in link:
            profiles["leetcode"]=link
        elif "geeksforgeeks.org" in link:
            profiles["geeksforgeeks"]=link
        elif "github.com" in link:
            path=link.replace("https://github.com/","").strip("/")
            if path.count("/")==0:
                profiles["github"]=link
            else:
                profiles["project_links"].append(link)

    return Profiles(**profiles)