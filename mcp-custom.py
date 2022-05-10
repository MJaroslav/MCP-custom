from argparse import ArgumentParser
import os
import requests


def load_repository(repo: str) -> dict:
    response = requests.get(repo + "versions.json")
    if response.status_code == 200:
        return response.json()
    return {}


def load_game(repo: dict, game: str) -> dict:
    if not repo:
        return ({}, game)
    if not game:
        items = list(repo.items())
        if items:
            return (items[0][1], items[0][0])
    return (repo.get(game, {}), game)


def has_mappings(repo: dict, game: str, channel: str, version: int) -> bool:
    _game = load_game(repo, game)
    if not _game[0]:
        return (False, _game[1], version)
    _channel = _game[0].get(channel, [])
    return (version in _channel if version else _channel, _game[1], _channel[0] if not version else version)


def main():
    parser = ArgumentParser(description="Allow creating, patching and deploying MCP mappings")
    parser.add_argument('-r', '--repository', action="store", metavar="URL", help='Set repo url with "original" mappings. \
        Aizistral\'s repo used as default', default="https://github.com/Aizistral-Studios/MCP-Archive/raw/dungeon-master/")
    parser.add_argument("-c", "--channel", action="store", help='Set channel for mappings. Default is "stable"', default="stable")
    parser.add_argument("-v", "--version", action="store", help='Set version for mappings. Default is latest', type=int)
    parser.add_argument("-g", "--game", action="store", help='Set game version for mappings. Default is latest')
    parser.add_argument("-d", "--download", action="store_true", help="Download selected mappings from repository")
    parser.add_argument("-p", "--path", action="store", help='Path for downloading, default "./downloads/"', default="./downloads/")
    args = parser.parse_args()

    if not args.repository.endswith("/"): args.repository += "/"
    if not args.path.endswith("/"): args.path += "/"

    repo = load_repository(args.repository)
    result = has_mappings(repo, args.game, args.channel, args.version)
    args.game = result[1]
    args.version = result[2]
    print("Trying find mappings for {} with {} channel and version {}".format(args.game, args.channel, args.version))
    if result[0]:
        if args.download:
            response = requests.get("{0}de/oceanlabs/mcp/mcp_{1}/{2}-{3}/mcp_{1}-{2}-{3}.zip".format(args.repository, args.channel, \
                args.version, args.game))
            if response.status_code == 200:
                if not os.path.isdir(args.path): os.makedirs(args.path)
                with open("{}mcp_{}-{}-{}.zip".format(args.path, args.channel, args.version, args.game), "wb") as file:
                    file.write(response.content)
                    print("Mappings saved")
            else:
                print("Mappings not found")
    else:
        print("Mappings not found")


if __name__ == "__main__":
    main()