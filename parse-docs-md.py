import re
import json
import os
import unicodedata
import shutil
import time

BASE_NAME_PATTERN = r'^\*\*\s*(?P<num>\d+)\s*-\s*(?P<name>.+?)\s*\*\*'
EXTRA_NAME_PATTERN = r'#\s*(?P<num>\d+)(?:-(?P<region>[A-Z]))?\s*(?::)\s*(?P<name>.+)'
NOTES_PATTERN = r'(?P<main>.+?)(?:\s*\((?P<notes>.+)\))?$'

def remove_heading(markdown_text: str, base: bool = True) -> str:
    # remove all text until first image
    lines = markdown_text.split('\n')
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        stop = False
        if base:
            is_image = re.match(r'^!\[[^\]]*\]\(', line.strip())
            stop = is_image
        else:
            is_heading = re.match(r'\*\*[^\*]+\*\*', line.strip())
            stop = is_heading
        if stop:
            break
        idx += 1
    return '\n'.join(lines[idx:])

def split_dex_file(
    content: str, 
    output_dir: str,
    name_pattern: str = BASE_NAME_PATTERN,
):
    lines = content.split('\n')
    current_segment = None
    last_image = None

    num = 0

    def print_seg(seg):
        nonlocal num
        match = re.match(name_pattern, seg["name"])
        region = match.groupdict().get('region', None)
        regions = f"-{region}" if region else ""
        filename = f"{match.group('num')}-{match.group('name')}{regions}.md"
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            print(f"num={match.group('num')}", file=f)
            print(f"name={match.group('name')}", file=f)
            if region:
                print(f"region={match.group('region')}", file=f)
            print('\n'.join(seg['lines']), file=f)
            print(f"image={seg['image']}", file=f)
        num += 1

    for line in lines:
        line = line.strip()

        # print(line)
        if line.startswith('![]('):
            last_image = line[4:].strip(')').replace("../", "")
        elif re.match(name_pattern, line):
            
            if current_segment is not None:
                print_seg(current_segment)

            current_segment = {
                "lines": [],
                "image": last_image,
                "name": line
            }
            last_image = None
        elif current_segment is not None:
            current_segment["lines"].append(line)
    
    if current_segment is not None:
        print_seg(current_segment)

    return num

CHECK_FOR_FORMS = ["Stats", "Abilities"]
FORM_PATTERN_SUFFIX = r'\s*\((.+?)\)\s*:'

def parse_dex_file(
    markdown_text: str,
) -> dict:
    lines = markdown_text.split('\n')

    # First check for things like shellos (West Side) (East Side) etc
    # found in stats or abilities

    forms = []
    for line in lines:
        pattern = f"(?:{'|'.join(CHECK_FOR_FORMS)})" + FORM_PATTERN_SUFFIX
        match = re.match(pattern, line)
        if match is not None:
            forms.append(match.group(1))

    if len(forms) == 0:
        entries = [{}]
    else:
        entries = [{'form': form} for form in forms]

    def set_for_form(key, value, form=None):
        nonlocal entries
        keys = key.split(".")
        for entry in entries:
            if form is None or entry.get('form', None) == form:
                last_depth = entry
                for key1 in keys[:-1]:
                    if key1 not in last_depth:
                        last_depth[key1] = {}
                    last_depth = last_depth[key1]
                last_depth[keys[-1]] = value

    # mrege lines to make brackets start and end in same line, to allow detecting notes etc
    lines = merge_adjacent_parentheses(lines)

    for line in lines:
        line = line.strip()
        if line.startswith('num='):
            set_for_form('num', int(line.replace('num=', '').strip()))
        elif line.startswith('name='):
            set_for_form('name', line.replace('name=', '').strip())
        elif line.startswith('region='):
            set_for_form('region', line.replace('region=', '').strip())
        elif line.startswith('image='):
            set_for_form('image', line.replace('image=', '').strip())
        elif is_stats_line(line):
            form_match = re.match(r'Stats' + FORM_PATTERN_SUFFIX, line)
            if form_match:
                form = form_match.group(1)
            else:
                form = None
            no_prefix = re.sub(r'Stats(?:\s*\(.*\)\s*)?:?\s*', '', line)

            set_for_form("stats", parse_stats_line(no_prefix), form)
        elif line.startswith('Type:'):
            no_prefix = line.replace("Type:", "").strip()
            notes_match = re.match(NOTES_PATTERN, no_prefix)
            types = re.split(r'[\\/]', notes_match.group("main"))
            if "notes" in notes_match.groupdict():
                set_for_form('type_notes', notes_match.group("notes"))
            set_for_form('type', types)
        elif line.startswith('Abilities'):
            notes_match = re.match(NOTES_PATTERN, line)
            form_match = re.match(r'Abilities' + FORM_PATTERN_SUFFIX, notes_match.group("main"))
            if form_match:
                form = form_match.group(1)
            else:
                form = None
            no_prefix = re.sub(r'Abilities(?:\s*\(.*\)\s*)?:?\s*', '', notes_match.group("main"))
            abilities = no_prefix.split("/")

            set_for_form('abilities', abilities, form)
            if "notes" in notes_match.groupdict():
                set_for_form('ability_notes', notes_match.group("notes"), form)
        elif line.startswith('Location:'):
            set_for_form('location', [])
        elif line.startswith('- '):
            for entry in entries:
                if 'location' in entry:
                    entry["location"].append(line[2:])
        elif line.startswith('Level Up:'):
            set_for_form('moves.level', [])
        elif re.match(r'\d+ - .*', line):
            move_match = re.match(r'(\d+) - (.*)', line)
            for entry in entries:
                if 'moves' in entry and 'level' in entry['moves']:
                    entry['moves']['level'].append({'level': int(move_match.group(1)), 'move': move_match.group(2)})
        elif line.startswith('TMs:'):
            set_for_form('moves.tm', [])
        elif line.startswith('TM'):
            tm_match = re.match(r'TM(\d+)(?::)? (.*)', line)
            tm = int(tm_match.group(1))
            move = tm_match.group(2)
            for entry in entries:
                if 'moves' in entry and 'tm' in entry['moves']:
                    entry['moves']['tm'].append({'tm': tm, 'move': move})
        elif line.startswith('Egg Moves:'):
            set_for_form('moves.egg', [])
        elif line:
            for entry in entries:
                if 'moves' in entry and 'egg' in entry['moves']:
                    entry['moves']['egg'].append(line)

    return entries

def merge_adjacent_parentheses(lines):
    merged_lines = []
    current_line = None

    for line in lines:
        if "(" in line and not ")" in line:
            current_line = line
        elif ")" in line and current_line:
            current_line += line
            merged_lines.append(current_line)
            current_line = None
        else:
            if current_line:
                current_line += " " + line
            else:
                merged_lines.append(line)

    if current_line:
        merged_lines.append(current_line)

    return merged_lines

# User order instead of name, jic
STAT_ORDER = [
    "HP",
    "Atk",
    "Def",
    "SpA",
    "SpD",
    "Spe",
    "BST",
]

def is_stats_line(line: str):
    return line.startswith("Stats") or not not re.search(r'(?:[^\/]+(?:\s*>\d+\s*)?\w+\s*\/){6}', line)

def parse_stats_line(line: str):
    # Example: 80 HP/82 Atk/83 Def/100>**110 SpA**/100 SpD/80 Spe/525>**535 BST**
    # Matches 80 [> [*[*]]90] Statname [*[*]]
    # group 1: original stat
    # group 2: asterisks (to distinguish change source)
    # group 3: new stat
    # group 4: name
    single_stat_pattern = r'(\d+)(?:\s*>\s*(\**)\s*(\d+))?\s*(\w+)\**'
    split = [l.strip() for l in re.split(r'[\\/]', line)]
    stats = {}
    for (stat, item) in zip(STAT_ORDER, split):
        # in case a line had asterisks after the slash by mistake
        without_starting_asterisks = re.sub(r'^\*{1,2}', '', item)
        match = re.match(single_stat_pattern, without_starting_asterisks)
        original_stat = int(match.group(1))
        asterisks = match.group(2)
        new_stat = int(match.group(3)) if match.group(3) is not None else None
        is_renegade = asterisks == '**' or asterisks == '***'
        is_lumi = asterisks == '*' or asterisks == '***'
        stat_entry = {
            'value': new_stat if new_stat else original_stat,
        }
        if new_stat:
            stat_entry['original'] = original_stat
            if is_lumi and is_renegade:
                stat_entry['changed_by'] = 'both'
            else:
                stat_entry['changed_by'] = 'luminescent' if is_lumi else 'renegade'
        stats[stat] = stat_entry

    return stats

def fill_missing(all_data: list[dict]):
    """Fill missing required entries by getting them from similar mons"""
    check_keys = [
        "stats", 
        "type",
        "moves",
        "abilities",
    ]
    for entry in all_data:
        match = None
        for key in check_keys:
            if key not in entry:
                if not match or key not in match:
                    match = find_entry(entry, all_data, key)
                if match:
                    entry[key] = match[key]
                else:
                    print(f"[warn] Couldn't find matching entry for {entry['name']} when filling missing data")
        if "stats" in entry and "BST" not in entry["stats"]:
            entry["stats"]["BST"] = {
                "value": sum([x["value"] for x in entry["stats"].values()])
            }

def find_entry(matching: dict, all_data: list[dict], with_key: str):
    for entry in all_data:
        if (
            matching['num'] == entry['num']
            or matching['name'].lower() in entry['name'].lower()
            or entry['name'].lower() in matching['name'].lower()
        ) and with_key in entry:
            return entry
    return None

def slugify(text, separator='-'):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s_]+', separator, text)

def main():
    BASE_DOCS_DIR = "docs/base"
    EXTRAS_DOCS_DIR = "docs/extras"
    INTERMEDIATE_DIR = "intermediate"
    OUT_DIR = "data/parsed"

    if os.path.exists(INTERMEDIATE_DIR):
        shutil.rmtree(INTERMEDIATE_DIR)
    shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(INTERMEDIATE_DIR, exist_ok=True)

    for docfile in os.listdir(BASE_DOCS_DIR):
        path = os.path.join(BASE_DOCS_DIR, docfile)
        if os.path.isdir(path): continue
        interm_path = os.path.join(INTERMEDIATE_DIR, slugify(docfile.replace(".md", "")))
        os.makedirs(interm_path, exist_ok=True)

        with open(path, 'r', encoding='utf-8') as file:
            markdown_text = file.read()

        no_heading = remove_heading(markdown_text)
        num_converted = split_dex_file(no_heading, interm_path)
        print(f"{docfile}: split into {num_converted} files")
    
    for docfile in os.listdir(EXTRAS_DOCS_DIR):
        path = os.path.join(EXTRAS_DOCS_DIR, docfile)
        if os.path.isdir(path): continue
        interm_path = os.path.join(INTERMEDIATE_DIR, slugify(docfile.replace(".md", "")))
        os.makedirs(interm_path, exist_ok=True)

        with open(path, 'r', encoding='utf-8') as file:
            markdown_text = file.read()

        no_heading = remove_heading(markdown_text, base = False)
        num_converted = split_dex_file(no_heading, interm_path, name_pattern=EXTRA_NAME_PATTERN)
        print(f"{docfile}: split into {num_converted} files")

    # c = 0

    print("Parsing to json...")
    t1 = time.time()

    for subdir in os.listdir(INTERMEDIATE_DIR):
        data = []

        for file in os.listdir(os.path.join(INTERMEDIATE_DIR, subdir)):
            path = os.path.join(INTERMEDIATE_DIR, subdir, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            entries = parse_dex_file(content)
            data.extend(entries)
            
            # c += 1
            # if c >= 1:
            #     break

        fill_missing(data)

        with open(os.path.join(OUT_DIR, f"{subdir}.json"), 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

        # break
    
    t2 = time.time()
    print(f"Parsed to json in {t2 - t1:.2f}s")

if __name__ == '__main__':
    main()