import os, re, shutil, argparse
from json import *
from time import sleep

if str(os.getcwd()).endswith("system32"):
    # This has to be in every script to prevent FileNotFoundError
    # Because for some reason, it runs it at C:\Windows\System32
    # Yeah, it is stupid, but I can't put these lines in custom_functions
    # Because that still brings up an error
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

from custom_functions import *
check("clrprint")
from clrprint import clrprint
check("markdown")
from markdown import markdown
check("bs4","beautifulsoup4")
from bs4 import BeautifulSoup
check("lzstring")
from lzstring import LZString

category_start = '<div class="category"><div oreui-type="button" oreui-color="dark" class="category-label" onclick="OreUI.toggleActive(this);toggleCategory(this);">topic_name</div><button class="category-label-selectall" onclick="selectAll(this)" data-allpacks="<all_packs>"><img src="images/select-all-button/chiseled_bookshelf_empty.png" class="category-label-selectall-img"><div class="category-label-selectall-hovertext">Select All</div></button><div class="category-controlled" oreui-color="dark" oreui-type="general"><div class="tweaks">'
subcategory_start = '<div class="subcategory"><div oreui-type="button" class="category-label" oreui-color="dark" onclick="OreUI.toggleActive(this);toggleCategory(this);">topic_name</div><button class="category-label-selectall sub" onclick="selectAll(this)" data-allpacks="<all_packs>"><img src="images/select-all-button/chiseled_bookshelf_empty.png" class="category-label-selectall-img"><div class="category-label-selectall-hovertext">Select All</div></button><div class="category-controlled" oreui-color="dark" oreui-type="general"><div class="subcattweaks">'
pack_start = '<div class="tweak" onclick="toggleSelection(this);" data-category="topic_name" data-name="pack_id" data-index="pack_index" oreui-type="button" oreui-color="dark" oreui-active-color="green">'
html_comp = '<div class="comp-hover-text" oreui-color="dark" oreui-type="general">Incompatible with: <incompatible></div>'
pack_mid = '<div class="tweak-info"><input type="checkbox" name="tweak"><img src="../relloctopackicon" style="width:82px; height:82px;" alt="pack_name"><br><label id="tweak" class="tweak-title">pack_name</label><div class="tweak-description">pack_description</div></div>'
html_conf = '<div class="conf-hover-text" oreui-color="dark" oreui-type="general">Conflicts with: <conflicts></div>'
pack_end = '</div>'
category_end = '</div></div></div>'
cat_end_w_subcat_no_end = '</div><div class="subcat<index>">'

html = ''
stats = [0, 0]
incomplete_packs = {}
cstats = [0, 0]
compatibilities = {}
conflicts = {}
pkicstats = [0, 0]
subcats = 0
ignore = False
subcat_list = []
incomplete_pkics = {}
packs = -1
pack_list = []
name_to_json = {}
with open(f"{cdir()}/jsons/others/pack_order_list.txt","r") as pol:
    for i in pol:
        pack_list.append(i)

parser = argparse.ArgumentParser(description='Run a massive script that updates Packs to-do, Icons to-do, Compatibilities to-do and the HTML')
parser.add_argument('--format', '-f', action='store_true', help='Include flag to format files')
parser.add_argument('--only-update-html', '-ouh', action='store_true', help='Only update the HTML')
parser.add_argument('--only-update-jsons', '-ouj', action='store_true', help='Only update the JSONs')
parser.add_argument('--build', '-b', action='store_true', help='Builds the website for production')
parser.add_argument('--update-theme', '-ut', action='store_true', help='Pulls the theme used for the website from the resource-packs repository')
args = parser.parse_args()

# Counts Packs and Compatibilities
if not args.build or (args.build and (args.only_update_html or args.only_update_jsons or args.format)):
    clrprint("Going through Packs...", clr="yellow")
    for j in pack_list:
        origj = j
        if not ignore:
            if j.endswith("\n"):
                j = j[:-1]
            file = load_json(f"{cdir()}/jsons/packs/{j}")
            name_to_json[file["topic"]] = j
            # Adds the categories automatically
            incomplete_pkics[file["topic"]] = []
            incomplete_packs[file["topic"]] = []
            html += category_start.replace("topic_name", file["topic"])
            current_category_packs = { "raw": [] }
            # Runs through the packs
            for i in range(len(file["packs"])):
                # Updates Incomplete Packs
                try:
                    if os.listdir(f'{cdir()}/packs/{file["topic"].lower()}/{file["packs"][i]["pack_id"]}/default') == []:
                        # Adds the packid to the topic list
                        incomplete_packs[file["topic"]].append(file["packs"][i]["pack_id"])
                        stats[1] += 1
                    else:
                        # When the packid directory has stuff inside
                        stats[0] += 1
                except FileNotFoundError:
                    # If the packs have not updated with the new directory type
                    stats[1] += 1
                    incomplete_packs[file["topic"]].append(file["packs"][i]["pack_id"])

                # Updates Incomplete pack_icon.png
                try:
                    if file["packs"][i]["pack_id"] in incomplete_packs[file["topic"]]:
                        pass
                    elif os.path.getsize(f'{cdir()}/packs/{file["topic"].lower()}/{file["packs"][i]["pack_id"]}/pack_icon.png') == os.path.getsize(f'{cdir()}/pack_icons/missing_texture.png'):
                        # Adds packid to topic list
                        incomplete_pkics[file["topic"]].append(file["packs"][i]["pack_id"])
                        pkicstats[1] += 1
                    else:
                        # When pack icon is complete
                        pkicstats[0] += 1
                except FileNotFoundError:
                    try:
                        if os.path.exists(f'{cdir()}/packs/{file["topic"].lower()}/{file["packs"][i]["pack_id"]}/pack_icon.{file["packs"][i]["icon"]}'):
                            pkicstats[0] += 1
                        else:
                            # When pack icon doesn't even exist
                            incomplete_pkics[file["topic"]].append(file["packs"][i]["pack_id"])
                            pkicstats[1] += 1
                    except KeyError:
                            incomplete_pkics[file["topic"]].append(file["packs"][i]["pack_id"])
                            pkicstats[1] += 1
                # Updates Incomplete Pack Compatibilities
                try:
                    for comp in range(len(file["packs"][i]["compatibility"])):
                        # Looks at compatibility folders
                        try:
                            if os.listdir(f'{cdir()}/packs/{file["topic"].lower()}/{file["packs"][i]["pack_id"]}/{file["packs"][i]["compatibility"][comp]}') == []:
                                # Adds the packid to the list of incomplete compatibilities
                                try:
                                    compatibilities[file["packs"][i]["pack_id"]].append(file["packs"][i]["compatibility"][comp])
                                except KeyError:
                                    compatibilities[file["packs"][i]["pack_id"]] = [file["packs"][i]["compatibility"][comp]]
                                cstats[1] += 1
                            else:
                                # When the compatibility directory has something inside
                                cstats[0] += 1
                        except FileNotFoundError:
                            # When the compatibility folder isn't there
                            # Adds the packid to the list of incomplete compatibilities
                            try:
                                compatibilities[file["packs"][i]["pack_id"]].append(file["packs"][i]["compatibility"][comp])
                            except KeyError:
                                compatibilities[file["packs"][i]["pack_id"]] = [file["packs"][i]["compatibility"][comp]]
                            cstats[1] += 1
                except KeyError:
                    pass # If it is empty, it just skips
                
                # Updates Pack Conflicts
                conflicts[file["packs"][i]["pack_id"]] = []
                try:
                    for conf in range(len(file["packs"][i]["conflict"])):
                        conflicts[file["packs"][i]["pack_id"]].append(file["packs"][i]["conflict"][conf])
                except KeyError:
                    pass # If it is empty, it just skips
                if conflicts[file["packs"][i]["pack_id"]] == []:
                    del conflicts[file["packs"][i]["pack_id"]]
                
                # Adds respective HTML
                compats = ""
                confs = ""
                if file["packs"][i]["pack_id"] not in incomplete_packs[file["topic"]]:
                    packs += 1
                    to_add_pack = pack_start
                    try:
                        c = ""
                        for c in compatibilities[file["packs"][i]["pack_id"]]:
                            compats += c
                            compats += ", "
                        to_add_pack += html_comp.replace('<incompatible>',compats[:-2])
                    except KeyError:
                        pass
                    to_add_pack += pack_mid
                    try:
                        c = ""
                        for c in conflicts[file["packs"][i]["pack_id"]]:
                            confs += c
                            confs += ", "
                        to_add_pack += html_conf.replace('<conflicts>',confs[:-2])
                    except KeyError:
                        pass
                    to_add_pack += pack_end
                    # Replace vars
                    to_add_pack = to_add_pack.replace("topic_name", file["topic"])
                    to_add_pack = to_add_pack.replace("pack_index", str(i))
                    to_add_pack = to_add_pack.replace("pack_id", file["packs"][i]["pack_id"])
                    to_add_pack = to_add_pack.replace("pack_name", file["packs"][i]["pack_name"])
                    desc = file["packs"][i]["pack_description"]
                    try:
                        if file["packs"][i]["message"][0] == "warn":
                            desc += f'<p class="desc-warn">{file["packs"][i]["message"][1]}</p>'
                        elif file["packs"][i]["message"][0] == "error":
                            desc += f'<p class="desc-error">{file["packs"][i]["message"][1]}</p>'
                        elif file["packs"][i]["message"][0] == "info":
                            desc += f'<p class="desc-info">{file["packs"][i]["message"][1]}</p>'
                    except KeyError:
                        pass
                    to_add_pack = to_add_pack.replace("pack_description", desc)
                    to_add_pack = to_add_pack.replace("relloctopackicon", f'packs/{file["topic"].lower()}/{file["packs"][i]["pack_id"]}/pack_icon.png')
                    try:
                        if os.path.exists(f'{cdir()}/packs/{file["topic"].lower()}/{file["packs"][i]["pack_id"]}/pack_icon.{file["packs"][i]["icon"]}'):
                            # Because I can't make the html use a missing texture thing, so
                            # it only replaces when it exists
                            to_add_pack = to_add_pack.replace("png", file["packs"][i]["icon"])
                    except KeyError:
                        pass
                    html += to_add_pack
                    current_category_packs["raw"].append(file["packs"][i]["pack_id"])
        html = html.replace("<all_packs>", LZString.compressToEncodedURIComponent(dumps(current_category_packs)))
        try:
            if pack_list[pack_list.index(origj) + 1].startswith("\t"):
                html += cat_end_w_subcat_no_end
                try:
                    if not pack_list[pack_list.index(origj) + 2].startswith("\t"):
                        html += category_end
                except IndexError:
                    pass
                html = html.replace("<index>", str(subcats))
                subcats += 1
                ignore = True
                subcat_list.append(pack_list[pack_list.index(origj) + 1][1:])
            elif not ignore:
                html += category_end
            else:
                ignore = False
        except IndexError:
            html += category_end
    # Seperate loop for subcategories (I'm inefficient)
    for j in range(len(subcat_list)):
        pack_html = ""
        k = subcat_list[j]
        if k.endswith("\n"):
            k = k[:-1]
        if k.startswith("\t"):
            k = k[1:]
        file = load_json(f"{cdir()}/jsons/packs/{k}")
        name_to_json[file["topic"]] = k
        # Adds the categories automatically
        incomplete_pkics[file["topic"]] = []
        incomplete_packs[file["topic"]] = []
        pack_html += subcategory_start.replace("topic_name", f'{file["subcategory_of"]} > <b>{file["topic"]}</b>')
        current_category_packs = { "raw": [] }
        for i in range(len(file["packs"])):
            # Updates Incomplete Packs
            try:
                if os.listdir(f'{cdir()}/packs/{file["topic"].lower()}/{file["packs"][i]["pack_id"]}/default') == []:
                    # Adds the packid to the topic list
                    incomplete_packs[file["topic"]].append(file["packs"][i]["pack_id"])
                    stats[1] += 1
                else:
                    # When the packid directory has stuff inside
                    stats[0] += 1
            except FileNotFoundError:
                # If the packs have not updated with the new directory type
                stats[1] += 1
                incomplete_packs[file["topic"]].append(file["packs"][i]["pack_id"])

            # Updates Incomplete pack_icon.png
            try:
                if file["packs"][i]["pack_id"] in incomplete_packs[file["topic"]]:
                    pass
                elif os.path.getsize(f'{cdir()}/packs/{file["topic"].lower()}/{file["packs"][i]["pack_id"]}/pack_icon.png') == os.path.getsize(f'{cdir()}/pack_icons/missing_texture.png'):
                    # Adds packid to topic list
                    incomplete_pkics[file["topic"]].append(file["packs"][i]["pack_id"])
                    pkicstats[1] += 1
                else:
                    # When pack icon is complete
                    pkicstats[0] += 1
            except FileNotFoundError:
                try:
                    if os.path.exists(f'{cdir()}/packs/{file["topic"].lower()}/{file["packs"][i]["pack_id"]}/pack_icon.{file["packs"][i]["icon"]}'):
                        pkicstats[0] += 1
                    else:
                        # When pack icon doesn't even exist
                        incomplete_pkics[file["topic"]].append(file["packs"][i]["pack_id"])
                        pkicstats[1] += 1
                except KeyError:
                    incomplete_pkics[file["topic"]].append(file["packs"][i]["pack_id"])
                    pkicstats[1] += 1
            
            # Updates Incomplete Pack Compatibilities
            try:
                for comp in range(len(file["packs"][i]["compatibility"])):
                    # Looks at compatibility folders
                    try:
                        if os.listdir(f'{cdir()}/packs/{file["topic"].lower()}/{file["packs"][i]["pack_id"]}/{file["packs"][i]["compatibility"][comp]}') == []:
                            # Adds the packid to the list of incomplete compatibilities
                            try:
                                compatibilities[file["packs"][i]["pack_id"]].append(file["packs"][i]["compatibility"][comp])
                            except KeyError:
                                compatibilities[file["packs"][i]["pack_id"]] = [file["packs"][i]["compatibility"][comp]]
                            cstats[1] += 1
                        else:
                            # When the compatibility directory has something inside
                            cstats[0] += 1
                    except FileNotFoundError:
                        # When the compatibility folder isn't there
                        # Adds the packid to the list of incomplete compatibilities
                        try:
                            compatibilities[file["packs"][i]["pack_id"]].append(file["packs"][i]["compatibility"][comp])
                        except KeyError:
                            compatibilities[file["packs"][i]["pack_id"]] = [file["packs"][i]["compatibility"][comp]]
                        cstats[1] += 1
            except KeyError:
                pass # If it is empty, it just skips

            # Updates Pack Conflicts
            conflicts[file["packs"][i]["pack_id"]] = []
            try:
                for conf in range(len(file["packs"][i]["conflict"])):
                    conflicts[file["packs"][i]["pack_id"]].append(file["packs"][i]["conflict"][conf])
            except KeyError:
                pass # If it is empty, it just skips
            if conflicts[file["packs"][i]["pack_id"]] == []:
                del conflicts[file["packs"][i]["pack_id"]]
            
            # Adds respective HTML
            compats = ""
            confs = ""
            if file["packs"][i]["pack_id"] not in incomplete_packs[file["topic"]]:
                packs += 1
                to_add_pack = pack_start
                try:
                    c = ""
                    for c in compatibilities[file["packs"][i]["pack_id"]]:
                        compats += c
                        compats += ", "
                    to_add_pack += html_comp.replace('<incompatible>',compats[:-2])
                except KeyError:
                    pass
                to_add_pack += pack_mid
                try:
                    c = ""
                    for c in conflicts[file["packs"][i]["pack_id"]]:
                        confs += c
                        confs += ", "
                    to_add_pack += html_conf.replace('<conflicts>',confs[:-2])
                except KeyError:
                    pass
                to_add_pack += pack_end
                # Replace vars
                to_add_pack = to_add_pack.replace("topic_name", file["topic"])
                to_add_pack = to_add_pack.replace("pack_index", str(i))
                to_add_pack = to_add_pack.replace("pack_id", file["packs"][i]["pack_id"])
                to_add_pack = to_add_pack.replace("pack_name", file["packs"][i]["pack_name"])
                desc = file["packs"][i]["pack_description"]
                try:
                    if file["packs"][i]["message"][0] == "warn":
                        desc += f'<p class="desc-warn">{file["packs"][i]["message"][1]}</p>'
                    elif file["packs"][i]["message"][0] == "error":
                        desc += f'<p class="desc-error">{file["packs"][i]["message"][1]}</p>'
                    elif file["packs"][i]["message"][0] == "info":
                        desc += f'<p class="desc-info">{file["packs"][i]["message"][1]}</p>'
                except KeyError:
                    pass
                to_add_pack = to_add_pack.replace("pack_description", desc)
                to_add_pack = to_add_pack.replace("relloctopackicon", f'packs/{file["topic"].lower()}/{file["packs"][i]["pack_id"]}/pack_icon.png')
                try:
                    if os.path.exists(f'{cdir()}/packs/{file["topic"].lower()}/{file["packs"][i]["pack_id"]}/pack_icon.{file["packs"][i]["icon"]}'):
                        # Because I can't make the html use a missing texture thing, some
                        # it only replaces when it exists
                        to_add_pack = to_add_pack.replace("png", file["packs"][i]["icon"])
                except KeyError:
                    pass
                pack_html += to_add_pack
                current_category_packs["raw"].append(file["packs"][i]["pack_id"])
        pack_html += category_end
        html = html.replace(f'<div class="subcat{j}"></div>',pack_html)
        html = html.replace("<all_packs>", LZString.compressToEncodedURIComponent(dumps(current_category_packs)))
    clrprint("Finished Counting!", clr="green")

    # HTML formatting
    with open(f"{cdir()}/webUI/index.html.template", "r") as html_file:
        real_html = html_file.read()
    html = real_html.replace("<!--Packs-->",html)
    with open(f"{cdir()}/credits.md", "r") as credits:
        html = html.replace("<!--credits-->",str(markdown(credits.read())))
    soup = BeautifulSoup(html, 'html.parser')
    html = soup.prettify()
    html = html.replace("<br/>", "<br>")
    # Update files
    clrprint("Updating files...", clr="yellow")
    if not args.only_update_html:
        dump_json(f"{cdir()}/jsons/others/incomplete_packs.json", incomplete_packs)
        dump_json(f"{cdir()}/jsons/others/incomplete_compatibilities.json", compatibilities)
        dump_json(f"{cdir()}/jsons/others/incomplete_pack_icons.json", incomplete_pkics)
        dump_json(f"{cdir()}/jsons/others/name_to_json.json", name_to_json)
    if not args.only_update_jsons:
        with open(f"{cdir()}/webUI/index.html", "w") as html_file:
            html_file.write(html)
    if not (args.only_update_html or args.only_update_jsons):
        # Just some fancy code with regex to update README.md
        with open(f"{cdir()}/README.md", "r") as file:
            content = file.read()
        # Regex to update link
        pack_pattern = r"(https://img.shields.io/badge/Packs-)(\d+%2F\d+)(.*)"
        pack_match = re.search(pack_pattern, content)
        comp_pattern = r"(https://img.shields.io/badge/Compatibilities-)(\d+%2F\d+)(.*)"
        comp_match = re.search(comp_pattern, content)
        pkic_pattern = r"(https://img.shields.io/badge/Pack%20Icons-)(\d+%2F\d+)(.*)"
        pkic_match = re.search(pkic_pattern, content)
        if pack_match and comp_match and pkic_match:
            # Replace the links using regex
            new_pack_url = f"{pack_match.group(1)}{stats[0]}%2F{stats[0] + stats[1]}{pack_match.group(3)}"
            updated_content = content.replace(pack_match.group(0), new_pack_url)
            new_comp_url = f"{comp_match.group(1)}{int(cstats[0] / 2)}%2F{int(cstats[0] / 2 + cstats[1] / 2)}{comp_match.group(3)}"
            updated_content = updated_content.replace(comp_match.group(0), new_comp_url)
            new_pkic_url = f"{pkic_match.group(1)}{pkicstats[0]}%2F{pkicstats[0] + pkicstats[1]}{pkic_match.group(3)}"
            updated_content = updated_content.replace(pkic_match.group(0), new_pkic_url)
            with open(f"{cdir()}/README.md", "w") as file:
                # Update the file
                file.write(updated_content)
        else:
            # When the regex fails if I change the link
            raise IndexError("Regex Failed")
    try:
      if args.update_theme:
        clrprint("Updating theme.css", clr="yellow")
        check("requests")
        import requests
        response = requests.get("https://becomtweaks.github.io/resource-packs/theme.css")
        if response.status_code == 200:
          with open(f"{cdir()}/webUI/theme.css","w") as theme:
            theme.write(response.text())
          clrprint("Updated theme.css!", clr="green")
    except requests.exceptions.ConnectionError:
      clrprint("Get a working internet connection before rerunning with `-ut`/`--update-theme`", clr="red")
    clrprint("Updated a lot of files!", clr="green")

    if args.format:
        clrprint("Making files Prettier", clr="yellow")
        os.system(f"cd {cdir()}")
        try:
            os.system('npx prettier --write "**/*.{js,ts,css,json}" --log-level silent')
        except KeyboardInterrupt:
            clrprint("You are a bit impatient...", clr="red")
        clrprint("Files are Prettier!", clr="green")
    elif not args.only_update_html:
        clrprint("Remember to format the files!", clr="y")

if args.build:
    clrprint("Make sure you built the HTML!", clr="y")
    try:
        shutil.rmtree(f"{cdir()}/build")
    except FileNotFoundError:
        pass
    try:
        shutil.copytree(f"{cdir()}/webUI", f"{cdir()}/build")
        os.remove(f"{cdir()}/build/index.html.template")
        with open(f"{cdir()}/build/index.html", "r") as file:
            content = file.read()
        with open(f"{cdir()}/build/index.html", "w") as file:
            file.write(content.replace("../", "https://raw.githubusercontent.com/BEComTweaks/crafting-tweaks/main/"))
        clrprint("Build success!", clr="g")
    except Exception as e:
        clrprint("Build failed!", clr="r")
        clrprint(e, clr="y")
