import re
from itertools import product

def extract_themes_old_format(text):
    groups = []
    blocks = re.findall(r'\(([^)]+)\)', text)
    for block in blocks:
        thms = re.findall(r'\{([A-Z0-9]{3}_[A-Z0-9]{2})\}', block)
        if thms:
            groups.append(thms)
    return groups

def extract_themes_from_diversity_expression(text):
    start = text.find("Diversity Expression")
    if start == -1:
        return []

    lines = [line.strip() for line in text[start:].splitlines()
             if line.strip() and "Diversity Expression" not in line]
    raw_block = " ".join(lines)

    matches = re.findall(r'(.+?)\1+', raw_block)
    expr_block = matches[0] if matches else raw_block

    expr_block = re.sub(r'[^\w\s(),._\[\]-]', '', expr_block)
    expr_block = re.sub(r'HP[-_]?\d{5,} ?\[.*?\] ?AND', '', expr_block, flags=re.IGNORECASE)

    branches = split_top_level_or(expr_block)
    branches = list(dict.fromkeys(branches))

    all_groups = []
    for branch in branches:
        raw_thms = re.findall(r'\b[A-Z0-9]{3}_[A-Z0-9]{2}\b', branch)
        thms = filter_until_prefix_conflict_with_parentheses(branch, raw_thms)
        groups = expand_prefix_conflicts_as_or(thms)
        all_groups.extend(groups)
    return all_groups

def split_top_level_or(text):
    result = []
    current = ""
    depth = 0
    i = 0
    while i < len(text):
        if text[i:i+2].lower() == "or" and depth == 0:
            if current.strip():
                result.append(current.strip())
            current = ""
            i += 2
        else:
            if text[i] == "(": depth += 1
            elif text[i] == ")": depth -= 1
            current += text[i]
            i += 1
    if current.strip():
        result.append(current.strip())
    return result

def filter_until_prefix_conflict_with_parentheses(branch_text, thms):
    seen = {}
    accepted = []
    for th in thms:
        prefix = th.split("_")[0]
        matches = list(re.finditer(r'\b' + re.escape(th) + r'\b', branch_text))
        if not matches:
            continue
        if prefix in seen:
            prev = seen[prefix]
            if not in_same_parentheses(branch_text, prev, th):
                break
        seen[prefix] = th
        accepted.append(th)
    return accepted

def in_same_parentheses(text, th1, th2):
    stack = []
    pairs = []
    for i, c in enumerate(text):
        if c == "(":
            stack.append(i)
        elif c == ")":
            if stack:
                start = stack.pop()
                pairs.append((start, i))
    for start, end in pairs:
        if th1 in text[start:end] and th2 in text[start:end]:
            return True
    return False

def expand_prefix_conflicts_as_or(thms):
    prefix_map = {}
    for th in thms:
        prefix = th.split("_")[0]
        prefix_map.setdefault(prefix, []).append(th)

    if all(len(v) == 1 for v in prefix_map.values()):
        return [thms]

    all_options = list(prefix_map.values())
    result = []
    for combo in product(*all_options):
        prefixes = [t.split("_")[0] for t in combo]
        if len(set(prefixes)) == len(combo):
            result.append(combo)
    return [list(group) for group in result]
