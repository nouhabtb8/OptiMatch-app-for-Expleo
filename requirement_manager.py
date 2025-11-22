import re
from datetime import datetime

#  Nouveau regex autorisant lettres ET chiffres dans les 3+2 positions
VALID_THEME_REGEX = re.compile(r'^[A-Z0-9]{3}_[A-Z0-9]{2}$')

class RequirementManager:
    def __init__(self):
        self.requirements = []
        self.history = []
        self.last_result = []
        self.phase_initiale = True

    def validate_requirement(self, text):
        id_match = re.search(r'REQ-\d{7} [A-Z]\b', text)
        if not id_match:
            potential_id = re.search(r'REQ-\d+\s?[A-Z]?', text)
            incorrect_id = potential_id.group(0) if potential_id else "Aucun ID détecté"
            return False, f"ID requirement incorrect : {incorrect_id}"

        raw_thematic_groups = re.findall(r'\{([^}]+)\}', text)
        incorrect = [t for t in raw_thematic_groups if not re.match(r'^[A-Z0-9]{3}_[A-Z0-9]{2}$', t)]
        return False, f"Thématique incorrecte : {', '.join(incorrect)}" if incorrect else (True, "")

    def extract_id(self, text):
        match = re.search(r'REQ-\d{7} [A-Z]\b', text)
        return match.group(0) if match else "ID inconnu"

    def is_valid_combination(self, combo):
        prefixes = [theme.split("_")[0] for theme in combo]
        return len(prefixes) == len(set(prefixes))

    def compare_sets(self, left, right):
        results = []
        for a in left:
            for b in right:
                combined = a + b
                unique = list(set(combined))
                if self.is_valid_combination(unique):
                    results.append(" AND ".join(sorted(unique)))
        return results

    def add_requirement(self, req_id, themes):
        #  Ne garder que les thématiques valides selon le nouveau format
        cleaned_themes = []
        for group in themes:
            valid_group = [t for t in group if VALID_THEME_REGEX.match(t)]
            if valid_group:
                cleaned_themes.append(valid_group)

        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.requirements.append({"id": req_id, "themes": cleaned_themes, "timestamp": timestamp})
        self.rebuild_history()

    def delete_requirement(self, index):
        if 0 <= index < len(self.requirements):
            del self.requirements[index]
            self.rebuild_history()

    def get_all_requirements(self):
        return self.requirements

    def rebuild_history(self):
        self.history.clear()
        self.last_result.clear()
        self.phase_initiale = True

        previous = None
        count_non_empty = 0

        for req in self.requirements:
            themes = req["themes"]

            if not themes:
                if count_non_empty < 2:
                    self.history.append([])  # garder la trace vide
                    continue
                else:
                    if self.history:
                        self.history.append(self.history[-1].copy())
                    else:
                        self.history.append([])
                    continue

            # Requirement non vide
            count_non_empty += 1

            if previous is None:
                previous = themes
                self.history.append([])  # pas de comparaison
                continue

            result = self.compare_sets(previous, themes)
            self.history.append(result)
            self.last_result = result

            previous = [line.split(" AND ") for line in result] if result else previous

        self.phase_initiale = False
