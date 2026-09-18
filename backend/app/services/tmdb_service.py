import os
import httpx

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

HEADERS = {
    "Authorization": f"Bearer {TMDB_API_KEY}",
    "accept": "application/json"
}

def search_movies(query: str):
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {"query": query, "include_adult": "false", "language": "en-US", "page": 1}
    response = httpx.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()

    results = []
    for movie in data.get("results", []):
        results.append({
            "tmdb_id": movie["id"],
            "title": movie["title"],
            "release_date": movie.get("release_date"),
            "poster_path": movie.get("poster_path"),
            "vote_average": movie.get("vote_average"),
            "overview": movie.get("overview"),
        })
    return results

def get_movie_details(tmdb_id: int):
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
    params = {"append_to_response": "credits", "language": "en-US"}
    response = httpx.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()

    directors = [
        c["name"] for c in data.get("credits", {}).get("crew", [])
        if c.get("job") == "Director"
    ]
    cast_members = [
        c["name"] for c in data.get("credits", {}).get("cast", [])[:10]
    ]

    return {
        "tmdb_id": data["id"],
        "title": data["title"],
        "original_title": data.get("original_title"),
        "overview": data.get("overview"),
        "poster_path": data.get("poster_path"),
        "backdrop_path": data.get("backdrop_path"),
        "release_date": data.get("release_date") or None,
        "runtime": data.get("runtime"),
        "genres": [g["name"] for g in data.get("genres", [])],
        "directors": directors,
        "cast_members": cast_members,
        "vote_average": data.get("vote_average"),
        "vote_count": data.get("vote_count"),
    }
