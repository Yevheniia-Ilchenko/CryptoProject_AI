import json
from datetime import datetime

from extract_data import projects


def format_data(project):
    results = project.get("results", {})

    return {
        "project_name": results.get("name", ""),
        "categories": results.get("categories", []),
        "description": {
            "short": results.get("description", ""),
            "full": results.get("fullDescription", ""),
        },
        "requirements": [
            {
                "chains": results.get("chains", []),
                "balance": results.get("metrics", {}).get("balance", 0),
                "task": None,
                "difficulty": None,
                "deadline": None,
            }
        ],
        "rewards": {
            "amount": None,
            "distribution_date": None
        },
        "links": {
            "website": results.get("website", ""),
            "social": {
                "twitter": next(
                    (link["url"] for link in results.get("socialLinks", []) if link.get("type") == "twitter"), ""
                ),
                "telegram": next(
                    (link["url"] for link in results.get("socialLinks", []) if link.get("type") == "telegram"), ""
                ),
                "discord": next(
                    (link["url"] for link in results.get("socialLinks", []) if link.get("type") == "discord"), ""
                ),
            }
        },
        "status": "active",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


formatted_projects = [format_data(project) for project in projects]
with open("formatted_projects.json", "w") as f:
    json.dump(formatted_projects, f, indent=4)


def search_project(keyword, df):
    text_columns = df.select_dtypes(include=["object"]).columns
    mask = df[text_columns].apply(lambda column: column.str.contains(keyword, case=False, na=False)).any(axis=1)
    return df[mask]


def filter_status(status, df):
    return df[df["status"] == status]


def group_by_category(df):
    return df.explode("categories").groupby("categories").size()