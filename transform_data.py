import json
from datetime import datetime

from extract_data import projects


def format_data(project):
    """
        Formats the raw project data into a structured dictionary.

        Parameters:
        - project (dict): The raw project data fetched from the API.

        Returns:
        - dict: A formatted dictionary containing the project's:
            - Name, categories, descriptions (short and full).
            - Requirements, such as chains, balance, and placeholders for tasks, difficulty, and deadlines.
            - Rewards information (placeholders for amount and distribution date).
            - Links to social media platforms (Twitter, Telegram, Discord) and the official website.
            - Status of the project (hardcoded as "active").
            - Last updated timestamp.
   """

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
    """
        Searches for projects that contain the specified keyword in any textual column.

        Parameters:
        - keyword (str): The keyword to search for.
        - df (pd.DataFrame): The DataFrame containing project data.

        Returns:
        - pd.DataFrame: A filtered DataFrame containing rows where the keyword
          appears in any string column.
    """

    text_columns = df.select_dtypes(include=["object"]).columns
    mask = df[text_columns].apply(lambda column: column.str.contains(keyword, case=False, na=False)).any(axis=1)
    return df[mask]


def filter_status(status, df):
    """
        Filters projects by their status (e.g., "active" or "ended").

        Parameters:
        - status (str): The status to filter by (e.g., "active", "ended").
        - df (pd.DataFrame): The DataFrame containing project data.

        Returns:
        - pd.DataFrame: A filtered DataFrame containing only rows matching the specified status.
    """

    return df[df["status"] == status]


def group_by_category(df):
    """
        Groups projects by their categories and counts the number of projects in each category.

        Parameters:
        - df (pd.DataFrame): The DataFrame containing project data.

        Returns:
        - pd.Series: A Series where the index represents categories and the values
          represent the count of projects in each category.
    """

    return df.explode("categories").groupby("categories").size()